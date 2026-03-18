"""Tests for shared common utilities."""

from pathlib import Path

from utils.common import ensure_sqlite_db_path, get_database_path


def test_get_database_path_with_override(tmp_path: Path):
    """Return the provided override path unchanged."""
    custom_path = tmp_path / "custom" / "db.sqlite3"
    assert get_database_path(custom_path) == custom_path


def test_ensure_sqlite_db_path_creates_directories_and_file(tmp_path: Path):
    """Create parent directories and database file when missing."""
    db_path = tmp_path / "nested" / "Storage" / "plutoscope.db"

    assert not db_path.exists()
    resolved_path = ensure_sqlite_db_path(db_path)

    assert resolved_path == db_path
    assert db_path.parent.exists()
    assert db_path.exists()

