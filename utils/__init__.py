"""Utility functions for Micro Plutoscope."""
from .database import (
    get_connection,
    initialize_database,
    verify_schema,
    add_file,
    get_file_by_hash,
    get_file_by_name,
    update_file_metadata,
    delete_file,
    get_all_files,
    get_important_files,
)
from .hashing import generate_hash, verify_hash_format
from .file_io import (
    read_file_from_disk,
    write_file_to_disk,
    get_file_metadata,
    file_exists,
    get_file_size,
)
from .common import (
    DEFAULT_DB_FILENAME,
    get_project_root,
    get_storage_dir,
    get_database_path,
    ensure_sqlite_db_path,
)

__all__ = [
    # Database
    "get_connection",
    "initialize_database",
    "verify_schema",
    # Database operations
    "add_file",
    "get_file_by_hash",
    "get_file_by_name",
    "update_file_metadata",
    "delete_file",
    "get_all_files",
    "get_important_files",
    # Hashing
    "generate_hash",
    "verify_hash_format",
    # File I/O
    "read_file_from_disk",
    "write_file_to_disk",
    "get_file_metadata",
    "file_exists",
    "get_file_size",
    # Common
    "DEFAULT_DB_FILENAME",
    "get_project_root",
    "get_storage_dir",
    "get_database_path",
    "ensure_sqlite_db_path",
]
