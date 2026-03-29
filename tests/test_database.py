"""Tests for database configuration and initialization."""

import pytest
import sqlite3
from pathlib import Path
from utils.database import get_connection, initialize_database, verify_schema


class TestDatabaseInitialization:
    """Test database initialization and schema setup."""

    def test_database_file_created(self, clean_db):
        """Test that database file is created."""
        assert clean_db.exists(), "Database file was not created"

    def test_schema_verification(self, clean_db):
        """Test that schema verification works."""
        assert verify_schema(), "Schema verification failed"

    def test_index_table_exists(self, clean_db):
        """Test that index table is created with correct columns."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('PRAGMA table_info("index")')
        columns = {row[1] for row in cursor.fetchall()}

        expected_columns = {
            "hash",
            "file",
            "purpose",
            "created",
            "modified",
            "storage",
            "important",
        }
        assert expected_columns.issubset(columns), f"Missing columns. Got: {columns}"
        conn.close()

    def test_files_table_exists(self, clean_db):
        """Test that files table is created with correct columns."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(files)")
        columns = {row[1] for row in cursor.fetchall()}

        expected_columns = {"hash", "path", "ispathabs", "content", "size"}
        assert expected_columns.issubset(columns), f"Missing columns. Got: {columns}"
        conn.close()

    def test_foreign_key_constraint(self, clean_db):
        """Test that foreign key constraint is enabled."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()[0]
        assert result == 1, "Foreign key constraints are not enabled"
        conn.close()


class TestFileOperations:
    """Test file-related database operations."""

    def test_add_file_success(self, clean_db):
        """Test successfully adding a file to database."""
        from utils.database import add_file

        file_hash = add_file(
            filename="test.txt",
            path="/path/to/test.txt",
            purpose="test file",
            content=b"test content",
            storage="FS",
            important=0,
        )

        assert isinstance(file_hash, str), "Hash should be a string"
        assert len(file_hash) == 64, (
            f"Hash should be 64 chars (SHA256), got {len(file_hash)}"
        )

    def test_add_file_with_empty_filename(self, clean_db):
        """Test that empty filename raises ValueError."""
        from utils.database import add_file

        with pytest.raises(ValueError, match="filename cannot be empty"):
            add_file(
                filename="",
                path="/path/to/file",
                storage="FS",
                important=0,
            )

    def test_add_file_with_invalid_storage(self, clean_db):
        """Test that invalid storage type raises ValueError."""
        from utils.database import add_file

        with pytest.raises(ValueError, match="storage must be 'FS' or 'DB'"):
            add_file(
                filename="test.txt",
                path="/path/to/test.txt",
                storage="INVALID",
                important=0,
            )

    def test_add_file_with_invalid_important(self, clean_db):
        """Test that invalid important value raises ValueError."""
        from utils.database import add_file

        with pytest.raises(ValueError, match="important must be 0 or 1"):
            add_file(
                filename="test.txt",
                path="/path/to/test.txt",
                storage="FS",
                important=2,
            )

    def test_add_duplicate_file_raises_error(self, clean_db):
        """Test that adding duplicate filename raises IntegrityError."""
        from utils.database import add_file
        import sqlite3

        # Add file first time
        add_file(
            filename="duplicate.txt",
            path="/path/to/file1.txt",
            storage="FS",
            important=0,
        )

        # Adding same filename should raise error (same hash)
        with pytest.raises(sqlite3.IntegrityError):
            add_file(
                filename="duplicate.txt",
                path="/path/to/file2.txt",
                storage="FS",
                important=0,
            )

    def test_get_file_by_hash(self, clean_db):
        """Test retrieving file by hash."""
        from utils.database import add_file, get_file_by_hash

        original_hash = add_file(
            filename=".env",
            path="/path/to/.env",
            purpose="Environment config",
            content=b"KEY=value",
            storage="FS",
            important=1,
        )

        file_data = get_file_by_hash(original_hash)

        assert file_data is not None, "File not found"
        assert file_data["hash"] == original_hash
        assert file_data["file"] == ".env"
        assert file_data["purpose"] == "Environment config"
        assert file_data["storage"] == "FS"
        assert file_data["important"] == 1
        assert file_data["path"] == "/path/to/.env"
        assert file_data["ispathabs"] == 1
        assert file_data["size"] == 9

    def test_get_nonexistent_file_returns_none(self, clean_db):
        """Test that getting nonexistent file returns None."""
        from utils.database import get_file_by_hash

        fake_hash = "a" * 64
        result = get_file_by_hash(fake_hash)

        assert result is None, "Should return None for nonexistent file"

    def test_update_file_metadata(self, clean_db):
        """Test updating file metadata."""
        from utils.database import add_file, update_file_metadata, get_file_by_hash

        original_hash = add_file(
            filename="update_test.txt",
            path="/path/to/update_test.txt",
            purpose="Original purpose",
            storage="FS",
            important=0,
        )

        success = update_file_metadata(
            original_hash,
            purpose="Updated purpose",
            important=1,
            storage="DB",
        )

        assert success, "Update failed"

        updated = get_file_by_hash(original_hash)
        assert updated["purpose"] == "Updated purpose"
        assert updated["important"] == 1
        assert updated["storage"] == "DB"

    def test_update_nonexistent_file(self, clean_db):
        """Test updating nonexistent file returns False."""
        from utils.database import update_file_metadata

        fake_hash = "b" * 64
        success = update_file_metadata(fake_hash, purpose="test")

        assert not success, "Should return False for nonexistent file"

    def test_update_file_content(self, clean_db):
        """Test updating file content."""
        from utils.database import add_file, update_file_content, get_file_by_hash

        original_hash = add_file(
            filename="content_test.txt",
            path="/path/to/content_test.txt",
            content=b"original content",
            storage="DB",
            important=0,
        )

        updated = get_file_by_hash(original_hash)
        assert updated["content"] == b"original content"
        assert updated["size"] == 16

        update_file_content(original_hash, b"updated content")

        updated = get_file_by_hash(original_hash)
        assert updated["content"] == b"updated content"
        assert updated["size"] == 15

    def test_update_file_content_nonexistent(self, clean_db):
        """Test updating content of nonexistent file returns False."""
        from utils.database import update_file_content

        fake_hash = "d" * 64
        success = update_file_content(fake_hash, b"new content")

        assert not success, "Should return False for nonexistent file"

    def test_delete_file(self, clean_db):
        """Test deleting a file."""
        from utils.database import add_file, delete_file, get_file_by_hash

        original_hash = add_file(
            filename="delete_test.txt",
            path="/path/to/delete_test.txt",
            storage="FS",
            important=0,
        )

        # Verify file exists
        assert get_file_by_hash(original_hash) is not None

        # Delete file
        success = delete_file(original_hash)
        assert success, "Delete should return True"

        # Verify file is gone
        assert get_file_by_hash(original_hash) is None

    def test_delete_nonexistent_file(self, clean_db):
        """Test deleting nonexistent file returns False."""
        from utils.database import delete_file

        fake_hash = "c" * 64
        success = delete_file(fake_hash)

        assert not success, "Should return False for nonexistent file"


class TestQueryOperations:
    """Test database query operations."""

    def test_get_all_files_empty(self, clean_db):
        """Test getting all files from empty database."""
        from utils.database import get_all_files

        files = get_all_files()

        assert isinstance(files, list)
        assert len(files) == 0

    def test_get_all_files_with_content(self, clean_db):
        """Test getting all files excludes content by default."""
        from utils.database import add_file, get_all_files

        add_file(
            filename="file1.txt",
            path="/path/to/file1.txt",
            content=b"large content",
            storage="FS",
            important=0,
        )

        files = get_all_files(metadata_only=True)

        assert len(files) == 1
        assert "content" not in files[0] or files[0]["content"] is None

    def test_get_all_files_include_content(self, clean_db):
        """Test getting all files with content included."""
        from utils.database import add_file, get_all_files

        test_content = b"test file content"
        add_file(
            filename="file_with_content.txt",
            path="/path/to/file_with_content.txt",
            content=test_content,
            storage="FS",
            important=0,
        )

        files = get_all_files(metadata_only=False)

        assert len(files) == 1
        assert files[0]["content"] == test_content

    def test_get_important_files(self, clean_db):
        """Test getting only important files."""
        from utils.database import add_file, get_important_files

        # Add multiple files
        add_file("important1.txt", "/path/1", storage="FS", important=1)
        add_file("important2.txt", "/path/2", storage="FS", important=1)
        add_file("normal.txt", "/path/3", storage="FS", important=0)

        important = get_important_files()

        assert len(important) == 2
        assert all(f["important"] == 1 for f in important)

    def test_get_important_files_empty(self, clean_db):
        """Test getting important files when none exist."""
        from utils.database import add_file, get_important_files

        add_file("normal.txt", "/path/1", storage="FS", important=0)

        important = get_important_files()

        assert len(important) == 0


class TestHashingFunctions:
    """Test hashing utility functions."""

    def test_generate_hash_deterministic(self):
        """Test that hash is deterministic for same filename."""
        from utils.hashing import generate_hash

        hash1 = generate_hash(".env")
        hash2 = generate_hash(".env")

        assert hash1 == hash2, "Hash should be deterministic"

    def test_generate_hash_different_filenames(self):
        """Test that different filenames produce different hashes."""
        from utils.hashing import generate_hash

        hash1 = generate_hash("file1.txt")
        hash2 = generate_hash("file2.txt")

        assert hash1 != hash2, "Different filenames should have different hashes"

    def test_generate_hash_format(self):
        """Test that generated hash is valid SHA256."""
        from utils.hashing import generate_hash, verify_hash_format

        hash_result = generate_hash("test.txt")

        assert verify_hash_format(hash_result), "Generated hash should be valid SHA256"
        assert len(hash_result) == 64, "SHA256 should be 64 characters"

    def test_verify_hash_format_valid(self):
        """Test verifying valid hash format."""
        from utils.hashing import verify_hash_format

        valid_hash = "a" * 64  # Valid hex string
        assert verify_hash_format(valid_hash), "Should validate valid hash"

    def test_verify_hash_format_invalid_length(self):
        """Test rejecting hash with invalid length."""
        from utils.hashing import verify_hash_format

        invalid_hash = "a" * 63
        assert not verify_hash_format(invalid_hash), "Should reject wrong length"

    def test_verify_hash_format_invalid_characters(self):
        """Test rejecting hash with invalid characters."""
        from utils.hashing import verify_hash_format

        invalid_hash = "z" * 64  # 'z' is invalid in hex
        assert not verify_hash_format(invalid_hash), "Should reject invalid hex"

    def test_verify_hash_format_wrong_type(self):
        """Test rejecting non-string hash."""
        from utils.hashing import verify_hash_format

        assert not verify_hash_format(123), "Should reject non-string"
        assert not verify_hash_format(None), "Should reject None"


class TestEnvironmentIntegration:
    """Integration test with real .env file."""

    def test_env_file_integration(self, clean_db, test_env_path):
        """Test adding real .env file to database."""
        from utils.database import add_file, get_file_by_name
        from utils.file_io import read_file_from_disk

        # Read the test env file
        content = read_file_from_disk(str(test_env_path))

        # Add to database
        file_hash = add_file(
            filename=".env",
            path=str(test_env_path),
            purpose="Environment configuration file",
            content=content,
            storage="FS",
            important=1,
        )

        # Retrieve and verify
        file_data = get_file_by_name(".env")

        assert file_data is not None
        assert file_data["file"] == ".env"
        assert file_data["purpose"] == "Environment configuration file"
        assert file_data["storage"] == "FS"
        assert file_data["important"] == 1
        assert file_data["size"] == len(content)
        assert file_data["content"] == content

    def test_multiple_files_integration(
        self, clean_db, test_env_path, test_config_file
    ):
        """Test adding and retrieving multiple files."""
        from utils.database import add_file, get_all_files, get_important_files
        from utils.file_io import read_file_from_disk

        # Add .env (important)
        env_content = read_file_from_disk(str(test_env_path))
        add_file(
            filename=".env",
            path=str(test_env_path),
            purpose="Environment config",
            content=env_content,
            storage="FS",
            important=1,
        )

        # Add config (not important)
        config_content = read_file_from_disk(str(test_config_file))
        add_file(
            filename="config.json",
            path=str(test_config_file),
            purpose="Application config",
            content=config_content,
            storage="FS",
            important=0,
        )

        # Verify all files
        all_files = get_all_files()
        assert len(all_files) == 2

        # Verify important files
        important = get_important_files()
        assert len(important) == 1
        assert important[0]["file"] == ".env"
