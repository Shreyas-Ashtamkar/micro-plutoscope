# micro-plutoscope

A Streamlit-based web application for **writing, executing, and managing code snippets** with multi-language support.

## Features

- **Multi-Language Code Editor** - Write code in SQL, Python, JavaScript, JSON, or Java with syntax highlighting and theme customization
- **Code Execution** - Run Python code directly in the browser or execute SQL queries against PostgreSQL databases
- **Code Management** - Save, organize, and retrieve code snippets with hash-based indexing
- **SQLite Storage** - Local database for persisting code snippets and file metadata

## Tech Stack

- **Frontend**: Streamlit + streamlit-code-editor (Monaco-based)
- **Backend**: Python code execution engine + psycopg2 (PostgreSQL)
- **Storage**: SQLite for snippet metadata, filesystem for file storage

## Project Structure

```
micro-plutoscope/
├── frontend/
│   ├── __init__.py
│   ├── streamlit_app.py       # Main Streamlit app
│   └── components/
│       ├── sidebar.py         # Navigation and code management
│       └── editor.py          # Code editor and output display
├── backend/
│   ├── __init__.py
│   ├── _base.py               # Singleton metaclass
│   └── code_executor.py       # Python/SQL code execution
├── utils/
│   ├── database.py            # SQLite operations
│   ├── file_io.py             # File read/write utilities
│   ├── hashing.py             # SHA256 file hashing
│   └── common.py              # Path and config helpers
├── Storage/
│   └── plutoscope.db          # SQLite database
├── streamlit_app.py           # Entry point
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run streamlit_app.py
```

## Configuration

Create a `.env` file for database connection settings:

```
DB_STRING=postgresql://user:pass@localhost/dbname
```
