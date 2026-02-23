"""
FalkorDB Service - Graph database for supply chain relationships
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FalkorDBService:
    """FalkorDB client for graph-based supply chain analysis"""

    def __init__(self, host: str = "localhost", port: int = 6379):
        self.host = host
        self.port = port
        self.graph = None
        self._connected = False
        self._connect()

    def _connect(self):
        """Attempt to connect to FalkorDB"""
        try:
            from falkordb import FalkorDB
            db = FalkorDB(host=self.host, port=self.port)
            self.graph = db.select_graph("supply_chain")
            self._connected = True
            logger.info("Connected to FalkorDB")
        except Exception as e:
            logger.warning(f"FalkorDB not available: {e}. Graph features disabled.")
            self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    def sync_supply_chain_data(self, sales_data: list, inventory_data: list,
                                supplier_data: list, po_data: list):
        """Sync all data into graph for relationship analysis"""
        if not self._connected:
            return

        try:
            # Clear existing graph
            self.graph.query("MATCH (n) DETACH DELETE n")

            # Create Supplier nodes
            for s in supplier_data:
                self.graph.query(
                    """CREATE (:Supplier {
                        supplier_id: $sid, 
                        name: $name, 
                        lead_time: $lt,
                        country: $country,
                        rating: $rating
                    })""",
                    params={
                        "sid": str(s.get("supplier_id", "")),
                        "name": str(s.get("supplier_name", "")),
                        "lt": int(s.get("lead_time", 0)),
                        "country": str(s.get("country", "")),
                        "rating": float(s.get("rating", 0)),
                    },
                )

            # Create Product nodes from inventory
            seen_skus = set()
            for item in inventory_data:
                sku = str(item.get("sku", ""))
                if sku not in seen_skus:
                    seen_skus.add(sku)
                    self.graph.query(
                        """CREATE (:Product {
                            sku: $sku,
                            qty_on_hand: $qty,
                            reorder_point: $rp,
                            location: $loc
                        })""",
                        params={
                            "sku": sku,
                            "qty": int(item.get("qty_on_hand", 0)),
                            "rp": int(item.get("reorder_point", 0)),
                            "loc": str(item.get("location", "")),
                        },
                    )

                    # Link product to supplier if supplier_id exists
                    sup_id = item.get("supplier_id")
                    if sup_id:
                        self.graph.query(
                            """MATCH (p:Product {sku: $sku}), (s:Supplier {supplier_id: $sid})
                               CREATE (s)-[:SUPPLIES]->(p)""",
                            params={"sku": sku, "sid": str(sup_id)},
                        )

            # Create PurchaseOrder nodes and relationships  
            for po in po_data:
                po_num = str(po.get("po_number", ""))
                self.graph.query(
                    """CREATE (:PurchaseOrder {
                        po_number: $pon,
                        quantity: $qty,
                        order_date: $od
                    })""",
                    params={
                        "pon": po_num,
                        "qty": float(po.get("quantity", 0)),
                        "od": str(po.get("order_date", "")),
                    },
                )

                # Link PO → Product
                sku = str(po.get("sku", ""))
                if sku:
                    self.graph.query(
                        """MATCH (po:PurchaseOrder {po_number: $pon}), (p:Product {sku: $sku})
                           CREATE (po)-[:ORDERS]->(p)""",
                        params={"pon": po_num, "sku": sku},
                    )

                # Link PO → Supplier
                sup_id = po.get("supplier_id")
                if sup_id:
                    self.graph.query(
                        """MATCH (po:PurchaseOrder {po_number: $pon}), (s:Supplier {supplier_id: $sid})
                           CREATE (po)-[:FROM_SUPPLIER]->(s)""",
                        params={"pon": po_num, "sid": str(sup_id)},
                    )

            logger.info("Supply chain graph synced successfully")

        except Exception as e:
            logger.error(f"Error syncing graph: {e}")

    def get_supply_chain_network(self) -> Dict[str, Any]:
        """Get the full supply chain network"""
        if not self._connected:
            return {"error": "FalkorDB not connected", "nodes": [], "edges": []}

        try:
            # Get all nodes
            suppliers = self.graph.query(
                "MATCH (s:Supplier) RETURN s.supplier_id, s.name, s.country, s.rating"
            ).result_set

            products = self.graph.query(
                "MATCH (p:Product) RETURN p.sku, p.qty_on_hand, p.location"
            ).result_set

            # Get relationships
            supply_links = self.graph.query(
                "MATCH (s:Supplier)-[:SUPPLIES]->(p:Product) RETURN s.supplier_id, p.sku"
            ).result_set

            return {
                "suppliers": [{"id": r[0], "name": r[1], "country": r[2], "rating": r[3]} for r in suppliers],
                "products": [{"sku": r[0], "qty": r[1], "location": r[2]} for r in products],
                "supply_links": [{"supplier": r[0], "product": r[1]} for r in supply_links],
            }
        except Exception as e:
            return {"error": str(e)}

    def get_supplier_dependencies(self, supplier_id: str) -> Dict[str, Any]:
        """Get all products and POs linked to a supplier"""
        if not self._connected:
            return {"error": "FalkorDB not connected"}

        try:
            products = self.graph.query(
                """MATCH (s:Supplier {supplier_id: $sid})-[:SUPPLIES]->(p:Product)
                   RETURN p.sku, p.qty_on_hand""",
                params={"sid": supplier_id},
            ).result_set

            pos = self.graph.query(
                """MATCH (po:PurchaseOrder)-[:FROM_SUPPLIER]->(s:Supplier {supplier_id: $sid})
                   RETURN po.po_number, po.quantity, po.order_date""",
                params={"sid": supplier_id},
            ).result_set

            return {
                "supplier_id": supplier_id,
                "products_supplied": [{"sku": r[0], "qty_on_hand": r[1]} for r in products],
                "purchase_orders": [{"po_number": r[0], "quantity": r[1], "order_date": r[2]} for r in pos],
            }
        except Exception as e:
            return {"error": str(e)}

    def get_product_supply_chain(self, sku: str) -> Dict[str, Any]:
        """Trace the full supply chain for a product"""
        if not self._connected:
            return {"error": "FalkorDB not connected"}

        try:
            suppliers = self.graph.query(
                """MATCH (s:Supplier)-[:SUPPLIES]->(p:Product {sku: $sku})
                   RETURN s.supplier_id, s.name, s.lead_time, s.rating""",
                params={"sku": sku},
            ).result_set

            orders = self.graph.query(
                """MATCH (po:PurchaseOrder)-[:ORDERS]->(p:Product {sku: $sku})
                   RETURN po.po_number, po.quantity, po.order_date""",
                params={"sku": sku},
            ).result_set

            return {
                "sku": sku,
                "suppliers": [{"id": r[0], "name": r[1], "lead_time": r[2], "rating": r[3]} for r in suppliers],
                "purchase_orders": [{"po_number": r[0], "quantity": r[1], "order_date": r[2]} for r in orders],
            }
        except Exception as e:
            return {"error": str(e)}

    def run_cypher_query(self, query: str) -> List:
        """Execute a raw Cypher query"""
        if not self._connected:
            return [{"error": "FalkorDB not connected"}]
        try:
            result = self.graph.query(query)
            return result.result_set
        except Exception as e:
            return [{"error": str(e)}]
