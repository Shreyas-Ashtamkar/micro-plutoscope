"""Hashing utilities for file identification."""
import hashlib


def generate_hash(filename: str) -> str:
    """
    Generate a deterministic SHA256 hash based on filename.
    
    Same filename will always produce the same hash, making it useful
    for identifying files and enabling updates.
    
    Args:
        filename: The filename to hash
        
    Returns:
        Hexadecimal SHA256 hash string
    """
    return hashlib.sha256(filename.encode()).hexdigest()


def verify_hash_format(hash_string: str) -> bool:
    """
    Verify that a hash string is a valid SHA256 hash.
    
    Args:
        hash_string: The hash to verify
        
    Returns:
        True if valid SHA256 hex string (64 chars), False otherwise
    """
    if not isinstance(hash_string, str):
        return False
    if len(hash_string) != 64:
        return False
    try:
        int(hash_string, 16)  # Verify it's valid hex
        return True
    except ValueError:
        return False
