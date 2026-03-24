"""Database operations and configuration for Micro Plutoscope."""
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import PurePosixPath, PureWindowsPath
from typing import Optional, List, Dict, Any, Generator

from .common import ensure_sqlite_db_path, get_database_path
from .hashing import generate_hash, verify_hash_format

# Database configuration
DB_PATH = get_database_path()


# Context managers and connection management
@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Get a database connection as a context manager.
    
    Yields:
        sqlite3.Connection with proper settings and cleanup
    """
    conn = sqlite3.connect(str(ensure_sqlite_db_path(DB_PATH)))
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    # Enable WAL mode for better concurrency with multiple users
    conn.execute("PRAGMA journal_mode=WAL;")
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys=ON;")
    try:
        yield conn
    finally:
        conn.close()


def get_connection() -> sqlite3.Connection:
    """
    Get a database connection with proper settings.
    
    Note: Prefer using get_db() context manager for automatic cleanup.
    
    Returns:
        sqlite3.Connection with WAL mode and foreign keys enabled
    """
    conn = sqlite3.connect(str(ensure_sqlite_db_path(DB_PATH)))
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    # Enable WAL mode for better concurrency with multiple users
    conn.execute("PRAGMA journal_mode=WAL;")
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


# Schema initialization
def initialize_database() -> None:
    """Initialize the database with schema if it doesn't exist."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Create index table (metadata) - escape "index" keyword with backticks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "index" (
                hash TEXT PRIMARY KEY NOT NULL,
                file TEXT NOT NULL,
                purpose TEXT,
                created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                modified DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                storage TEXT NOT NULL CHECK(storage IN ('FS', 'DB')),
                important INTEGER NOT NULL DEFAULT 0 CHECK(important IN (0, 1))
            )
        """)
        
        # Create files table (content storage)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                hash TEXT PRIMARY KEY NOT NULL,
                path TEXT NOT NULL,
                ispathabs INTEGER NOT NULL DEFAULT 0 CHECK(ispathabs IN (0, 1)),
                content BLOB,
                size INTEGER NOT NULL,
                FOREIGN KEY (hash) REFERENCES "index"(hash) ON DELETE CASCADE
            )
        """)

        # Backfill schema for existing databases created before ispathabs existed.
        cursor.execute("PRAGMA table_info(files)")
        files_columns = {row[1] for row in cursor.fetchall()}
        if "ispathabs" not in files_columns:
            cursor.execute("ALTER TABLE files ADD COLUMN ispathabs INTEGER NOT NULL DEFAULT 0")
        
        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_important ON "index"(important)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created ON "index"(created)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_file ON "index"(file)
        """)
        
        conn.commit()


def verify_schema() -> bool:
    """
    Verify that the database schema is correctly initialized.
    
    Returns:
        True if both index and files tables exist, False otherwise
    """
    with get_db() as conn:
        cursor = conn.cursor()

        # Check if tables exist.
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('index', 'files')"
        )
        tables = {row[0] for row in cursor.fetchall()}
        if tables != {"index", "files"}:
            return False

        # Ensure files table contains required path metadata columns.
        cursor.execute("PRAGMA table_info(files)")
        files_columns = {row[1] for row in cursor.fetchall()}

    return {"hash", "path", "ispathabs", "content", "size"}.issubset(files_columns)


# Helper functions for validation and data mapping
def _validate_hash(file_hash: str) -> None:
    """
    Validate hash format.
    
    Raises:
        ValueError: If hash format is invalid
    """
    if not verify_hash_format(file_hash):
        raise ValueError(f"Invalid hash format: {file_hash}")


def _validate_storage(storage: str) -> None:
    """
    Validate storage type.
    
    Raises:
        ValueError: If storage type is invalid
    """
    if storage not in ("FS", "DB"):
        raise ValueError("storage must be 'FS' or 'DB'")


def _validate_important(important: int) -> None:
    """
    Validate important flag.
    
    Raises:
        ValueError: If important value is invalid
    """
    if important not in (0, 1):
        raise ValueError("important must be 0 or 1")


def _is_path_absolute(path: str) -> bool:
    """Return True for absolute paths in either POSIX or Windows syntax."""
    return (
        os.path.isabs(path)
        or PurePosixPath(path).is_absolute()
        or PureWindowsPath(path).is_absolute()
    )


def _row_to_dict(row: sqlite3.Row, include_content: bool = True) -> Dict[str, Any]:
    """
    Convert a database row to a dictionary.
    
    Args:
        row: sqlite3.Row object from query
        include_content: If True, include file content in result
        
    Returns:
        Dictionary with file data
    """
    result = dict(row)
    if not include_content:
        result.pop("content", None)
    return result


def _execute_file_query(
    query: str, 
    params: tuple = (), 
    fetch_all: bool = False,
    include_content: bool = True
) -> Optional[Dict[str, Any]] | List[Dict[str, Any]]:
    """
    Execute a file query and return mapped results.
    
    Args:
        query: SQL query string
        params: Query parameters
        fetch_all: If True, return list of results; if False, return single result
        include_content: If True, include file content in results
        
    Returns:
        Single dict, list of dicts, or None if no results
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if fetch_all:
            rows = cursor.fetchall()
            return [_row_to_dict(row, include_content) for row in rows]
        else:
            row = cursor.fetchone()
            return _row_to_dict(row, include_content) if row else None


# CRUD operations
def add_file(
    filename: str,
    path: str,
    purpose: Optional[str] = None,
    content: Optional[bytes] = None,
    storage: str = "FS",
    important: int = 0,
) -> str:
    """
    Add a file to the database.
    
    Args:
        filename: Original filename
        path: Filesystem path to the file
        purpose: Description/purpose of the file
        content: Optional file content (for small files)
        storage: Storage type, 'FS' (default) or 'DB'
        important: 1 for important, 0 (default) for not important
        
    Returns:
        The generated hash of the file
        
    Raises:
        ValueError: If parameters are invalid
        sqlite3.IntegrityError: If hash already exists
    """
    if not filename:
        raise ValueError("filename cannot be empty")
    if not path:
        raise ValueError("path cannot be empty")
    
    _validate_storage(storage)
    _validate_important(important)
    
    file_hash = generate_hash(filename)
    is_path_abs = 1 if _is_path_absolute(path) else 0
    size = len(content) if content else 0
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        try:
            # Insert into index table
            cursor.execute(
                """
                INSERT INTO "index" (hash, file, purpose, storage, important)
                VALUES (?, ?, ?, ?, ?)
                """,
                (file_hash, filename, purpose, storage, important)
            )
            
            # Insert into files table
            cursor.execute(
                """
                INSERT INTO files (hash, path, ispathabs, content, size)
                VALUES (?, ?, ?, ?, ?)
                """,
                (file_hash, path, is_path_abs, content, size)
            )
            
            conn.commit()
            return file_hash
        except sqlite3.IntegrityError as e:
            conn.rollback()
            raise sqlite3.IntegrityError(f"File with hash {file_hash} already exists") from e


def get_file_by_hash(file_hash: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a file by its hash.
    
    Args:
        file_hash: The SHA256 hash of the file
        
    Returns:
        Dictionary with file metadata and content, or None if not found
    """
    _validate_hash(file_hash)
    
    query = """
        SELECT i.hash, i.file, i.purpose, i.created, i.modified, 
               i.storage, i.important, f.path, f.ispathabs, f.content, f.size
        FROM "index" i
        JOIN files f ON i.hash = f.hash
        WHERE i.hash = ?
    """
    
    return _execute_file_query(query, (file_hash,), fetch_all=False, include_content=True)


def update_file_metadata(file_hash: str, **kwargs) -> bool:
    """
    Update file metadata (only index table fields).
    
    Args:
        file_hash: The hash of the file to update
        **kwargs: Fields to update (purpose, storage, important, modified)
        
    Returns:
        True if successful, False if file not found
        
    Raises:
        ValueError: If invalid field or value provided
    """
    _validate_hash(file_hash)
    
    allowed_fields = {"purpose", "storage", "important"}
    invalid_fields = set(kwargs.keys()) - allowed_fields
    if invalid_fields:
        raise ValueError(f"Invalid fields: {invalid_fields}")
    
    if "storage" in kwargs:
        _validate_storage(kwargs["storage"])
    if "important" in kwargs:
        _validate_important(kwargs["important"])
    
    if not kwargs:
        return True  # Nothing to update
    
    # Always update modified timestamp
    update_fields = list(kwargs.keys()) + ["modified"]
    update_values = list(kwargs.values()) + [datetime.now().isoformat()]
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{field} = ?" for field in update_fields])
        query = f'UPDATE "index" SET {set_clause} WHERE hash = ?'
        
        cursor.execute(query, update_values + [file_hash])
        conn.commit()
        
        success = cursor.rowcount > 0
    
    return success


def delete_file(file_hash: str) -> bool:
    """
    Delete a file from the database (both tables).
    
    Args:
        file_hash: The hash of the file to delete
        
    Returns:
        True if successful, False if file not found
    """
    _validate_hash(file_hash)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM "index" WHERE hash = ?', (file_hash,))
        conn.commit()
        
        success = cursor.rowcount > 0
    
    return success


def get_all_files(metadata_only: bool = True) -> List[Dict[str, Any]]:
    """
    Get all files from the database.
    
    Args:
        metadata_only: If True, exclude file content (faster for large files)
        
    Returns:
        List of file dictionaries
    """
    if metadata_only:
        query = """
            SELECT i.hash, i.file, i.purpose, i.created, i.modified, 
                   i.storage, i.important, f.path, f.ispathabs, f.size
            FROM "index" i
            JOIN files f ON i.hash = f.hash
            ORDER BY i.created DESC
        """
    else:
        query = """
            SELECT i.hash, i.file, i.purpose, i.created, i.modified, 
                   i.storage, i.important, f.path, f.ispathabs, f.content, f.size
            FROM "index" i
            JOIN files f ON i.hash = f.hash
            ORDER BY i.created DESC
        """
    
    return _execute_file_query(query, fetch_all=True, include_content=not metadata_only)


def get_important_files() -> List[Dict[str, Any]]:
    """
    Get all files marked as important (metadata only).
    
    Returns:
        List of important file dictionaries
    """
    query = """
        SELECT i.hash, i.file, i.purpose, i.created, i.modified, 
             i.storage, i.important, f.path, f.ispathabs, f.size
        FROM "index" i
        JOIN files f ON i.hash = f.hash
        WHERE i.important = 1
        ORDER BY i.created DESC
    """
    
    return _execute_file_query(query, fetch_all=True, include_content=False)


def get_file_by_name(filename: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a file by its filename (since filename determines hash).
    
    Args:
        filename: The filename to search for
        
    Returns:
        File dictionary or None if not found
    """
    file_hash = generate_hash(filename)
    return get_file_by_hash(file_hash)


# Module initialization
if __name__ == "__main__":
    initialize_database()
    if verify_schema():
        print("✓ Database schema initialized successfully")
    else:
        print("✗ Database schema initialization failed")
