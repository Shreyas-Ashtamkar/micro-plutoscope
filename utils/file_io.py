"""File I/O operations for Micro Plutoscope."""
import os
from pathlib import Path
from typing import Optional, Tuple


def read_file_from_disk(path: str) -> bytes:
    """
    Read a file from disk.
    
    Args:
        path: Filesystem path to the file
        
    Returns:
        File content as bytes
        
    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
    """
    try:
        with open(path, "rb") as f:
            return f.read()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {path}") from e
    except IOError as e:
        raise IOError(f"Cannot read file: {path}") from e


def write_file_to_disk(path: str, content: bytes) -> None:
    """
    Write content to a file on disk.
    
    Args:
        path: Filesystem path where to write
        content: File content as bytes
        
    Raises:
        IOError: If file cannot be written
    """
    try:
        # Create parent directories if needed
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "wb") as f:
            f.write(content)
    except IOError as e:
        raise IOError(f"Cannot write file: {path}") from e


def get_file_metadata(path: str) -> Tuple[int, float]:
    """
    Get file metadata (size and modification time).
    
    Args:
        path: Filesystem path to the file
        
    Returns:
        Tuple of (size in bytes, modification timestamp)
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    try:
        stat = os.stat(path)
        return (stat.st_size, stat.st_mtime)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {path}") from e


def file_exists(path: str) -> bool:
    """
    Check if a file exists.
    
    Args:
        path: Filesystem path to check
        
    Returns:
        True if file exists, False otherwise
    """
    return os.path.isfile(path)


def get_file_size(path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        path: Filesystem path to the file
        
    Returns:
        File size in bytes
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    try:
        return os.path.getsize(path)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {path}") from e
