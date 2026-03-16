"""Test configuration and fixtures for Micro Plutoscope."""
import pytest
import sqlite3
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_storage_dir():
    """Create a temporary storage directory for testing."""
    temp_dir = tempfile.mkdtemp(prefix="plutoscope_test_")
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_db_path(temp_storage_dir, monkeypatch):
    """Mock the database path to use temporary directory."""
    mock_path = Path(temp_storage_dir) / "plutoscope.db"
    
    # Patch the DB_PATH in database module
    import utils.database
    monkeypatch.setattr(utils.database, "DB_PATH", mock_path)
    
    yield mock_path


@pytest.fixture
def clean_db(mock_db_path):
    """Provide a clean initialized database for each test."""
    from utils.database import initialize_database, verify_schema
    
    initialize_database()
    assert verify_schema(), "Database schema verification failed"
    
    yield mock_db_path
    
    # Cleanup happens automatically via temp_storage_dir fixture


@pytest.fixture
def test_env_path(temp_storage_dir):
    """Create a test .env file."""
    env_file = Path(temp_storage_dir) / ".env"
    env_content = "DATABASE_URL=postgresql://localhost/test\nAPI_KEY=test123secret\n"
    env_file.write_text(env_content)
    return env_file


@pytest.fixture
def test_config_file(temp_storage_dir):
    """Create a test configuration file."""
    config_file = Path(temp_storage_dir) / "config.json"
    config_file.write_text('{"setting": "value"}')
    return config_file
