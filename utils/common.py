"""Common helpers shared across app entry points and utility modules."""

from pathlib import Path


DEFAULT_DB_FILENAME = "plutoscope.db"


def get_project_root() -> Path:
	"""Return the project root directory."""
	return Path(__file__).resolve().parent.parent


def get_storage_dir(storage_dir: str | Path | None = None) -> Path:
	"""Resolve the storage directory path."""
	if storage_dir is not None:
		return Path(storage_dir)
	return get_project_root() / "Storage"


def get_database_path(db_path: str | Path | None = None) -> Path:
	"""Resolve the SQLite database file path."""
	if db_path is not None:
		return Path(db_path)
	return get_storage_dir() / DEFAULT_DB_FILENAME


def ensure_sqlite_db_path(db_path: str | Path | None = None) -> Path:
	"""Ensure database parent directories and file exist, then return the path."""
	resolved_path = get_database_path(db_path)
	resolved_path.parent.mkdir(parents=True, exist_ok=True)
	if not resolved_path.exists():
		resolved_path.touch()
	return resolved_path


__all__ = [
	"DEFAULT_DB_FILENAME",
	"get_project_root",
	"get_storage_dir",
	"get_database_path",
	"ensure_sqlite_db_path",
]

