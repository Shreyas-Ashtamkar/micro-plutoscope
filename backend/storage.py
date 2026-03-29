"""Code storage module for Micro Plutoscope."""

from typing import List, Dict, Any

from utils.hashing import generate_hash
from utils.database import (
    get_file_by_hash,
    add_file,
    update_file_content,
    delete_file,
    get_all_files,
)


def save_code(name: str, content: str, language: str) -> tuple[str, str]:
    """
    Save code to database.

    Args:
        name: Unique identifier for the code
        content: Code content as string
        language: Programming language (stored as purpose)

    Returns:
        tuple: (hash, status) where status is "created", "updated", or "unchanged"
    """
    file_hash = generate_hash(name)
    content_bytes = content.encode("utf-8")

    existing = get_file_by_hash(file_hash)

    if existing:
        if existing.get("content") == content_bytes:
            return (file_hash, "unchanged")
        else:
            update_file_content(file_hash, content_bytes)
            return (file_hash, "updated")
    else:
        add_file(
            filename=name,
            path="",
            purpose=language,
            content=content_bytes,
            storage="DB",
            important=0,
        )
        return (file_hash, "created")


def load_code(name: str) -> dict | None:
    """
    Load code content and language by name.

    Args:
        name: Unique identifier for the code

    Returns:
        Dictionary with 'content' and 'language' keys, or None if not found
    """
    file_hash = generate_hash(name)
    result = get_file_by_hash(file_hash)
    if result and result.get("content"):
        return {
            "content": result["content"].decode("utf-8"),
            "language": result.get("purpose", "python"),
        }
    return None


def list_codes(metadata_only: bool = True) -> List[Dict[str, Any]]:
    """
    List all saved codes from DB storage.

    Args:
        metadata_only: If True, exclude file content (faster)

    Returns:
        List of file dictionaries with storage='DB'
    """
    all_files = get_all_files(metadata_only=metadata_only)
    return [f for f in all_files if f.get("storage") == "DB"]


def delete_code(name: str) -> str:
    """
    Delete code by name.

    Args:
        name: Unique identifier for the code

    Returns:
        Status string: "deleted", "not_found", or "permission_denied"
    """
    file_hash = generate_hash(name)
    existing = get_file_by_hash(file_hash)

    if not existing:
        return "not_found"

    if existing.get("important") == 1:
        return "permission_denied"

    delete_file(file_hash)
    return "deleted"
