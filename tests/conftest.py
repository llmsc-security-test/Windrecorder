"""pytest configuration for Windrecorder tests."""
import pytest
import os
import tempfile


@pytest.fixture
def sample_config():
    """Sample configuration fixture."""
    return {
        "test_key": "test_value",
        "number": 42,
    }


@pytest.fixture
def sample_data():
    """Sample data fixture."""
    return [1, 2, 3, 4, 5]


@pytest.fixture
def sample_db_path():
    """Create a temporary database path for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_db")
        os.makedirs(db_path, exist_ok=True)
        yield db_path


@pytest.fixture
def mock_config():
    """Create a mock config object for testing."""
    from unittest.mock import MagicMock

    mock = MagicMock()
    mock.db_path_ud = "/tmp/test_db"
    mock.max_page_result = 50
    mock.user_name = "test_user"
    mock.config_src_dir = "/tmp/config"
    mock.record_videos_dir_ud = "/tmp/videos"
    mock.maintain_lock_path = "/tmp/maintain_lock"
    return mock
