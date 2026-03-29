# Agent Guidelines for micro-plutoscope

## Project Overview

A Streamlit-based web application for writing, executing, and managing code snippets with multi-language support (Python, SQL, JavaScript, JSON, Java).

## Build & Development Commands

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure ruff is installed (linting/formatting)
pip install ruff
```

### Running the Application

```bash
# Start Streamlit app
streamlit run streamlit_app.py
```

### Testing

```bash
pytest                     # run all tests
pytest tests/test_common.py  # run single file
pytest tests/test_common.py::test_get_database_path_with_override  # run single test
pytest -v -k "test_database"  # run filtered verbose
```

### Linting & Formatting

```bash
ruff check .                # lint all Python files
ruff check --fix .          # lint with auto-fix
ruff format .               # format all Python files (line length 88)
ruff format --check .       # check formatting without changes
```

## Code Style Guidelines

### Imports

- **Order**: Standard library → third-party → local modules.
- **Grouping**: Separate groups with a blank line.
- **Ruff automatically sorts imports according to isort conventions.**
- **Relative imports**: Use relative imports within packages (e.g., `from .common import ...`).
- **Absolute imports**: Use absolute imports for top-level modules.
- **Example**:
  ```python
  import os
  import sqlite3
  from typing import Optional, List, Dict

  import streamlit as st

  from utils.common import get_database_path
  from .hashing import generate_hash
  ```

### Formatting

- Use **ruff format** (default line length 88).
- Trailing commas in multi-line function signatures and calls.
- Double quotes for strings.
- No trailing whitespace.

### Type Hints

- **Required** for all function parameters and return types.
- Use `typing` module for complex types (`Optional`, `List`, `Dict`, `Any`, `Generator`, `Union`).
- Prefer built-in types (`list`, `dict`) for Python 3.9+; use `typing` for compatibility.
- Example: `def get_file_by_hash(file_hash: str) -> Optional[Dict[str, Any]]:`

### Naming Conventions

- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private functions/variables**: prefix with `_`
- **Module-level constants**: `UPPER_CASE`

### Docstrings

- **Style**: Google‑style for all public functions, classes, and modules.
- **Sections**: Use `Args:`, `Returns:`, `Raises:` where appropriate.
- **Example**:
  ```python
  def add_file(filename: str, path: str) -> str:
      """Add a file to the database.

      Args:
          filename: Original filename.
          path: Filesystem path to the file.

      Returns:
          The generated hash of the file.

      Raises:
          ValueError: If filename is empty.
      """
  ```

### Error Handling

- Raise specific exceptions (`ValueError`, `TypeError`, `sqlite3.IntegrityError`).
- Use `try...except` with `rollback()` for database operations.
- Provide clear, actionable error messages.
- Validate inputs early (e.g., `if not filename: raise ValueError(...)`).

### No Comments

- Avoid adding comments unless explicitly requested by the user.
- Code should be self‑documenting through clear naming and docstrings.

## Key Patterns

### Singleton Pattern
The `CodeExecutor` uses a singleton metaclass to ensure only one instance exists:
```python
from backend._base import SingletonMeta

class CodeExecutor(metaclass=SingletonMeta):
    pass
```

### Database Pattern
Use context manager for database connections:
```python
from utils.database import get_db

with get_db() as conn:
    # operations
```

### Hash‑based File Identification
Files are identified by SHA256 hash of their filename (deterministic):
```python
from utils.hashing import generate_hash
file_hash = generate_hash(filename)
```

### Path Handling
Always use `pathlib.Path` for filesystem paths:
```python
from pathlib import Path

def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent
```

## Important Notes

- **Storage**: SQLite database at `Storage/plutoscope.db` (gitignored)
- **SQL execution**: Currently requires external PostgreSQL connection (not fully integrated)
- **Code editor**: Uses `streamlit-code-editor` (Monaco‑based)
- **Session state**: Streamlit uses `st.session_state` for state management
- **Linting**: Ruff is configured via default settings; no `.ruff.toml` present
- **Type checking**: No strict type checker enforced, but type hints are required

