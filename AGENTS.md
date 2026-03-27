# Agent Guidelines for micro-plutoscope

## Project Overview

A Streamlit-based web application for writing, executing, and managing code snippets with multi-language support (Python, SQL, JavaScript, JSON, Java).

## Running Tests

```bash
pytest
```

## Code Conventions

- **Python**: Use `snake_case` for functions/variables, `PascalCase` for classes
- **Type hints**: Required for function parameters and return types
- **Docstrings**: Google-style docstrings for all public functions/classes
- **No comments**: Avoid adding comments unless explicitly requested by the user

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

### Hash-based File Identification
Files are identified by SHA256 hash of their filename (deterministic):
```python
from utils.hashing import generate_hash
file_hash = generate_hash(filename)
```

## Important Notes

- **Storage**: SQLite database at `Storage/plutoscope.db` (gitignored)
- **SQL execution**: Currently requires external PostgreSQL connection (not fully integrated)
- **Code editor**: Uses `streamlit-code-editor` (Monaco-based)
- **Session state**: Streamlit uses `st.session_state` for state management
