"""
MCP Configuration Generator API Routes
Generates config JSON for Claude Desktop, Claude Code, and Cursor
"""
import os
import sys
import json
from fastapi import APIRouter
from core.config import settings

router = APIRouter()


def _get_mcp_server_path() -> str:
    """Get the absolute path to the MCP server script"""
    return os.path.abspath(
        os.path.join(settings.BASE_DIR, "mcp_server", "server.py")
    )


def _get_python_path() -> str:
    """Get the current Python executable path"""
    return sys.executable


@router.get("/config")
async def get_mcp_config():
    """
    Generate MCP configuration for Claude Desktop, Claude Code, and Cursor.
    Returns ready-to-paste JSON configs.
    """
    server_path = _get_mcp_server_path()
    python_path = _get_python_path()
    duckdb_path = os.path.abspath(
        os.path.join(settings.BASE_DIR, settings.DUCKDB_PATH)
    )

    env_vars = {
        "DUCKDB_PATH": duckdb_path,
        "USE_FALKORDB": str(settings.USE_FALKORDB).lower(),
        "FALKORDB_HOST": settings.FALKORDB_HOST,
        "FALKORDB_PORT": str(settings.FALKORDB_PORT),
    }

    # Claude Desktop config
    claude_desktop = {
        "mcpServers": {
            "supply-chain-analytics": {
                "command": python_path,
                "args": [server_path],
                "env": env_vars,
            }
        }
    }

    # Claude Code config (same format)
    claude_code = {
        "mcpServers": {
            "supply-chain-analytics": {
                "command": python_path,
                "args": [server_path],
                "env": env_vars,
            }
        }
    }

    # Cursor config
    cursor = {
        "mcpServers": {
            "supply-chain-analytics": {
                "command": python_path,
                "args": [server_path],
                "env": env_vars,
            }
        }
    }

    instructions = """
## How to Connect AI to Your Supply Chain Data

### Claude Desktop
1. Open Claude Desktop settings
2. Go to Developer → Edit Config
3. Paste the "claude_desktop" JSON into your `claude_desktop_config.json`
4. Restart Claude Desktop
5. You'll see the supply chain tools in the 🔧 menu

### Claude Code (CLI)
1. Create `.claude/mcp.json` in your project root
2. Paste the "claude_code" JSON content
3. Restart Claude Code

### Cursor
1. Go to Settings → MCP Servers
2. Add a new server with the config from "cursor" JSON
3. Or paste into `.cursor/mcp.json` in your project root
4. Restart Cursor

### What You Can Do
Once connected, ask your AI assistant things like:
- "Show me sales trends for the last quarter"
- "Which items need to be reordered?"
- "Analyze supplier performance and risk"
- "What are the top-selling products?"
- "Find anomalies in our supply chain data"
- "Create a demand forecast for SKU-001"
"""

    return {
        "claude_desktop": claude_desktop,
        "claude_code": claude_code,
        "cursor": cursor,
        "instructions": instructions,
        "server_path": server_path,
        "python_path": python_path,
    }


@router.get("/config/claude-desktop")
async def get_claude_desktop_config():
    """Get just the Claude Desktop config"""
    config = await get_mcp_config()
    return config["claude_desktop"]


@router.get("/config/cursor")
async def get_cursor_config():
    """Get just the Cursor config"""
    config = await get_mcp_config()
    return config["cursor"]
