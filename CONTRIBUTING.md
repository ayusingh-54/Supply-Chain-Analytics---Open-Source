# Contributing to Supply Chain Analytics

Thank you for considering contributing to Supply Chain Analytics! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Project Architecture](#project-architecture)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Release Process](#release-process)

---

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the maintainers.

---

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**Bug reports should include:**

- A clear, descriptive title
- Steps to reproduce the behavior
- Expected vs. actual behavior
- Environment details (OS, Python version, browser)
- Screenshots or logs if applicable

### 💡 Suggesting Features

Feature requests are welcome! Please include:

- A clear description of the feature
- The problem it solves or use case it enables
- Any alternative solutions you've considered
- Mockups or examples if applicable

### 🔧 Code Contributions

We welcome code contributions for:

- Bug fixes
- New MCP tools for AI integration
- Analytics algorithms (forecasting, risk analysis)
- UI/UX improvements to the Streamlit frontend
- API endpoint additions
- Test coverage improvements
- Documentation updates
- Performance optimizations

### 📝 Documentation

Help improve our docs:

- Fix typos or clarify existing documentation
- Add missing API documentation
- Write tutorials or how-to guides
- Improve code comments and docstrings

---

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- Docker (optional, for FalkorDB)

### Setup Steps

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/supply-chain-analytics.git
cd supply-chain-analytics

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize database
python scripts/setup_database.py

# 6. Generate sample data (for testing)
python scripts/generate_sample_data.py

# 7. Run tests to verify setup
pytest tests/ -v
```

### Running Services Locally

```bash
# Terminal 1: Backend API
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2: Streamlit Frontend
cd streamlit_app && streamlit run app.py

# Terminal 3: MCP Server (if testing AI integration)
cd mcp_server && python server.py
```

---

## Project Architecture

```
backend/                    # FastAPI Backend
├── api/routes/             # API endpoint handlers
├── core/                   # Configuration & database initialization
├── models/                 # Pydantic schemas
└── services/               # Business logic layer
    ├── duckdb_service.py   # Analytics database operations
    ├── falkordb_service.py # Graph database operations
    └── file_service.py     # File validation & processing

streamlit_app/              # Streamlit Frontend
├── pages/                  # Multi-page app views
└── utils/                  # API client & helpers

mcp_server/                 # MCP Server
└── server.py               # Tool definitions & implementations
```

### Key Design Decisions

1. **DuckDB as primary store**: Embedded OLAP engine — no external database server needed
2. **FalkorDB optional**: Graph features degrade gracefully when FalkorDB is unavailable
3. **MCP Server independent**: Connects directly to DuckDB, can be used standalone
4. **Service layer pattern**: Business logic is decoupled from API routes
5. **Schema-driven validation**: Data categories have declarative schema rules in config

---

## Coding Standards

### Python Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- Use type hints for function parameters and return values
- Maximum line length: 100 characters
- Use docstrings for all public functions, classes, and modules

```python
def calculate_quality_score(
    total_rows: int,
    valid_rows: int,
    issues: List[Dict]
) -> float:
    """
    Calculate a data quality score from 0-100.

    Args:
        total_rows: Total number of rows in the uploaded file
        valid_rows: Number of rows that passed validation
        issues: List of quality issues found during validation

    Returns:
        Quality score as a float between 0.0 and 100.0
    """
    ...
```

### Naming Conventions

| Element       | Convention         | Example                       |
| ------------- | ------------------ | ----------------------------- |
| Variables     | `snake_case`       | `file_category`               |
| Functions     | `snake_case`       | `get_sales_summary()`         |
| Classes       | `PascalCase`       | `DuckDBService`               |
| Constants     | `UPPER_SNAKE_CASE` | `MAX_FILE_SIZE_MB`            |
| Files         | `snake_case`       | `duckdb_service.py`           |
| API endpoints | `kebab-case`       | `/api/database/sales-summary` |

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add demand forecasting with ARIMA model
fix: handle null values in supplier rating column
docs: add API reference for /api/files/upload endpoint
test: add unit tests for quality scoring engine
refactor: extract validation logic into FileValidator class
chore: update DuckDB dependency to 0.10.1
```

### Branch Naming

```
feature/add-prophet-forecasting
fix/null-pointer-in-upload
docs/api-reference-update
test/mcp-tool-coverage
refactor/service-layer-cleanup
```

---

## Testing Guidelines

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=backend --cov-report=html --cov-report=term-missing

# Specific test class
pytest tests/test_services.py::TestFileService -v

# Specific test
pytest tests/test_api.py::TestHealthEndpoint::test_health -v
```

### Writing Tests

1. **Location**: Place tests in `tests/` directory
2. **Naming**: Files: `test_*.py`, Classes: `Test*`, Functions: `test_*`
3. **Isolation**: Tests must not depend on external services (FalkorDB disabled)
4. **Cleanup**: Use fixtures with proper teardown

```python
class TestNewFeature:
    """Tests for the new feature"""

    def test_happy_path(self):
        """Test the expected successful behavior"""
        result = my_function(valid_input)
        assert result.status == "success"

    def test_edge_case(self):
        """Test boundary conditions"""
        result = my_function(edge_input)
        assert result is not None

    def test_error_handling(self):
        """Test that errors are handled gracefully"""
        with pytest.raises(ValueError):
            my_function(invalid_input)
```

### Test Categories

| Category    | Focus                | Example                        |
| ----------- | -------------------- | ------------------------------ |
| Unit        | Individual functions | Schema validation logic        |
| Integration | API endpoints        | Upload → validate → store flow |
| Service     | Business logic       | DuckDB query building          |
| MCP         | Tool implementations | Tool input/output format       |

---

## Pull Request Process

### Before Submitting

1. ✅ Create an issue describing what you're working on
2. ✅ Branch from `main` with a descriptive branch name
3. ✅ Write tests for new functionality
4. ✅ Ensure all existing tests pass (`pytest tests/ -v`)
5. ✅ Update documentation if needed
6. ✅ Follow coding standards

### PR Template

When opening a PR, include:

```markdown
## Summary

Brief description of changes.

## Related Issue

Fixes #123

## Changes Made

- Added X feature
- Fixed Y bug
- Updated Z documentation

## Testing

- [ ] Added/updated unit tests
- [ ] All tests pass locally
- [ ] Tested manually in the Streamlit UI

## Screenshots (if UI changes)

Before | After
```

### Review Process

1. PRs require at least one reviewer approval
2. All CI checks must pass
3. No merge conflicts with `main`
4. Reviewer may request changes — iterate until approved
5. Squash merge preferred for feature branches

---

## Issue Guidelines

### Bug Report Template

```markdown
**Describe the bug**
Clear description of what went wrong.

**To Reproduce**

1. Go to '...'
2. Click on '...'
3. Upload file '...'
4. See error

**Expected behavior**
What you expected to happen.

**Environment**

- OS: [e.g., Windows 11, Ubuntu 22.04]
- Python: [e.g., 3.11.5]
- Browser: [e.g., Chrome 120]

**Logs/Screenshots**
Paste relevant error messages or attach screenshots.
```

### Feature Request Template

```markdown
**Is this related to a problem?**
Description of the problem or limitation.

**Proposed Solution**
Clear description of what you want to happen.

**Alternatives Considered**
Other approaches you've thought about.

**Additional Context**
Mockups, diagrams, examples.
```

---

## Release Process

### Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking API changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, documentation updates

### Release Checklist

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Create git tag: `git tag -a v1.x.x -m "Release v1.x.x"`
5. Push tag: `git push origin v1.x.x`
6. Create GitHub release with changelog

---

## Questions?

If you have questions about contributing:

1. Check existing [issues](https://github.com/your-org/supply-chain-analytics/issues)
2. Open a [discussion](https://github.com/your-org/supply-chain-analytics/discussions)
3. Reach out to maintainers

**Thank you for contributing! 🙏**
