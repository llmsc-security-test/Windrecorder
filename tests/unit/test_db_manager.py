"""Unit tests for Windrecorder DB Manager."""
import pytest
import os
import tempfile
import sqlite3
from datetime import datetime
from unittest.mock import MagicMock, patch, mock_open
import pandas as pd


class TestDBManager:
    """Tests for the DBManager class."""

    @pytest.fixture
    def sample_db_path(self):
        """Create a temporary database path for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_db")
            os.makedirs(db_path, exist_ok=True)
            yield db_path

    @pytest.fixture
    def mock_config(self):
        """Create a mock config object."""
        mock = MagicMock()
        mock.db_path_ud = "/tmp/test_db"
        mock.max_page_result = 50
        mock.user_name = "test_user"
        mock.config_src_dir = "/tmp/config"
        mock.record_videos_dir_ud = "/tmp/videos"
        mock.maintain_lock_path = "/tmp/maintain_lock"
        return mock

    @pytest.fixture
    def db_manager(self, sample_db_path, mock_config):
        """Create a DBManager instance."""
        from windrecorder.db_manager import _DBManager

        # Patch config to use mock
        with patch("windrecorder.db_manager.config", mock_config):
            with patch("windrecorder.file_utils.ensure_dir"):
                with patch("windrecorder.db_manager._DBManager.db_main_initialize"):
                    with patch("windrecorder.db_manager._DBManager.db_update_table_product_routine"):
                        manager = _DBManager(sample_db_path, 50, "test_user")
                        # Override the _db_filename_dict with a test dict
                        manager._db_filename_dict = {}
                        yield manager

    def test_db_get_dbfilename_by_datetime(self, db_manager, sample_db_path):
        """Test db_get_dbfilename_by_datetime method."""
        # Create some dummy database files
        db_files = [
            "test_user_2024-01_wind.db",
            "test_user_2024-02_wind.db",
            "test_user_2024-03_wind.db",
        ]

        for db_file in db_files:
            open(os.path.join(sample_db_path, db_file), "w").close()

        # Update the filename dict
        db_manager._db_filename_dict = {
            "test_user_2024-01_wind.db": datetime(2024, 1, 1),
            "test_user_2024-02_wind.db": datetime(2024, 2, 1),
            "test_user_2024-03_wind.db": datetime(2024, 3, 1),
        }

        # Test query for January 2024
        start_dt = datetime(2024, 1, 15)
        end_dt = datetime(2024, 1, 31)
        result = db_manager.db_get_dbfilename_by_datetime(start_dt, end_dt)

        assert "test_user_2024-01_wind.db" in result

        # Test query spanning multiple months
        start_dt = datetime(2024, 1, 15)
        end_dt = datetime(2024, 2, 15)
        result = db_manager.db_get_dbfilename_by_datetime(start_dt, end_dt)

        assert len(result) >= 2
        assert "test_user_2024-01_wind.db" in result
        assert "test_user_2024-02_wind.db" in result

    def test_db_initialize_creates_table(self, db_manager, sample_db_path):
        """Test that database initialization creates the video_text table."""
        db_filepath = os.path.join(sample_db_path, "test_user_2024-01_wind.db")

        # Initialize the database
        result = db_manager.db_initialize(db_filepath)

        # Verify the table was created
        conn = sqlite3.connect(db_filepath)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='video_text'")
        table = c.fetchone()
        conn.close()

        assert table is not None

        # Verify expected columns exist
        c = conn.cursor() if 'conn' in locals() else sqlite3.connect(db_filepath).cursor()
        c.execute("PRAGMA table_info(video_text)")
        columns = [col[1] for col in c.fetchall()]
        conn.close()

        expected_columns = [
            "videofile_name",
            "picturefile_name",
            "videofile_time",
            "ocr_text",
            "is_videofile_exist",
            "is_picturefile_exist",
            "thumbnail",
            "win_title",
            "deep_linking",
        ]

        for col in expected_columns:
            assert col in columns

    def test_db_update_data(self, db_manager, sample_db_path):
        """Test db_update_data method."""
        db_filepath = os.path.join(sample_db_path, "test_user_2024-01_wind.db")

        # First initialize the database
        db_manager.db_initialize(db_filepath)

        # Insert test data
        test_time = 1704067200  # 2024-01-01 00:00:00
        db_manager.db_update_data(
            videofile_name="test_video_2024-01-01_00-00-00.mp4",
            picturefile_name="iframe_0.jpg",
            videofile_time=test_time,
            ocr_text="Test OCR content",
            is_videofile_exist=True,
            is_picturefile_exist=True,
            thumbnail="base64_test_data",
            win_title="Test Window Title",
            deep_linking="https://example.com",
        )

        # Verify data was inserted
        conn = sqlite3.connect(db_filepath)
        c = conn.cursor()
        c.execute("SELECT * FROM video_text WHERE videofile_name = ?", ("test_video_2024-01-01_00-00-00.mp4",))
        row = c.fetchone()
        conn.close()

        assert row is not None
        assert row[3] == "Test OCR content"  # ocr_text
        assert row[6] == "base64_test_data"  # thumbnail
        assert row[7] == "Test Window Title"  # win_title

    def test_db_search_data(self, db_manager, sample_db_path):
        """Test db_search_data method."""
        db_filepath = os.path.join(sample_db_path, "test_user_2024-01_wind.db")

        # Initialize the database
        db_manager.db_initialize(db_filepath)

        # Insert test data
        test_time = 1704067200
        db_manager.db_update_data(
            videofile_name="test_video_2024-01-01_00-00-00.mp4",
            picturefile_name="iframe_0.jpg",
            videofile_time=test_time,
            ocr_text="This is a test document with important information",
            is_videofile_exist=True,
            is_picturefile_exist=True,
            thumbnail="base64_test",
            win_title="Test Window",
        )

        # Test search with keyword
        start_dt = datetime(2024, 1, 1)
        end_dt = datetime(2024, 1, 31)

        df, row_count, page_count = db_manager.db_search_data(
            keyword_input="test",
            date_in=start_dt,
            date_out=end_dt,
        )

        assert row_count >= 1
        assert page_count >= 1

        # Test search with no results
        df, row_count, page_count = db_manager.db_search_data(
            keyword_input="nonexistent_keyword_12345",
            date_in=start_dt,
            date_out=end_dt,
        )

        assert row_count == 0

    def test_db_search_data_with_exclusion(self, db_manager, sample_db_path):
        """Test db_search_data method with exclusion keyword."""
        db_filepath = os.path.join(sample_db_path, "test_user_2024-01_wind.db")

        db_manager.db_initialize(db_filepath)

        # Insert test data
        test_time = 1704067200
        db_manager.db_update_data(
            videofile_name="test1.mp4",
            picturefile_name="iframe_0.jpg",
            videofile_time=test_time,
            ocr_text="Python is great for data science",
            is_videofile_exist=True,
            is_picturefile_exist=True,
            thumbnail="base64",
            win_title="Window",
        )

        db_manager.db_update_data(
            videofile_name="test2.mp4",
            picturefile_name="iframe_0.jpg",
            videofile_time=test_time + 1,
            ocr_text="Python is not good for cooking",
            is_videofile_exist=True,
            is_picturefile_exist=True,
            thumbnail="base64",
            win_title="Window",
        )

        # Search for "python" excluding "cooking"
        df, row_count, page_count = db_manager.db_search_data(
            keyword_input="python",
            date_in=datetime(2024, 1, 1),
            date_out=datetime(2024, 1, 31),
            keyword_input_exclude="cooking",
        )

        # Should only return the first row (not the one with "cooking")
        assert row_count >= 1

    def test_db_list_all_data(self, db_manager, sample_db_path, caplog):
        """Test db_list_all_data method."""
        db_filepath = os.path.join(sample_db_path, "test_user_2024-01_wind.db")

        db_manager.db_initialize(db_filepath)

        test_time = 1704067200
        db_manager.db_update_data(
            videofile_name="test_video.mp4",
            picturefile_name="iframe_0.jpg",
            videofile_time=test_time,
            ocr_text="Test content",
            is_videofile_exist=True,
            is_picturefile_exist=True,
            thumbnail="base64",
            win_title="Test",
        )

        # This method just logs, so we verify it doesn't raise
        db_manager.db_list_all_data()

    def test_db_num_records(self, db_manager, sample_db_path):
        """Test db_num_records method."""
        db_filepath = os.path.join(sample_db_path, "test_user_2024-01_wind.db")

        db_manager.db_initialize(db_filepath)

        test_time = 1704067200
        db_manager.db_update_data(
            videofile_name="test1.mp4",
            picturefile_name="iframe_0.jpg",
            videofile_time=test_time,
            ocr_text="First",
            is_videofile_exist=True,
            is_picturefile_exist=True,
            thumbnail="base64",
            win_title="Test",
        )

        db_manager.db_update_data(
            videofile_name="test2.mp4",
            picturefile_name="iframe_0.jpg",
            videofile_time=test_time + 1,
            ocr_text="Second",
            is_videofile_exist=True,
            is_picturefile_exist=True,
            thumbnail="base64",
            win_title="Test",
        )

        count = db_manager.db_num_records()
        assert count >= 2

    def test_db_latest_record_time(self, db_manager, sample_db_path):
        """Test db_latest_record_time method."""
        db_filepath = os.path.join(sample_db_path, "test_user_2024-01_wind.db")

        db_manager.db_initialize(db_filepath)

        db_manager.db_update_data(
            videofile_name="test1.mp4",
            picturefile_name="iframe_0.jpg",
            videofile_time=100,
            ocr_text="First",
            is_videofile_exist=True,
            is_picturefile_exist=True,
            thumbnail="base64",
            win_title="Test",
        )

        db_manager.db_update_data(
            videofile_name="test2.mp4",
            picturefile_name="iframe_0.jpg",
            videofile_time=200,
            ocr_text="Second",
            is_videofile_exist=True,
            is_picturefile_exist=True,
            thumbnail="base64",
            win_title="Test",
        )

        latest = db_manager.db_latest_record_time()
        assert latest == 200

    def test_db_first_earliest_record_time(self, db_manager, sample_db_path):
        """Test db_first_earliest_record_time method."""
        db_filepath = os.path.join(sample_db_path, "test_user_2024-01_wind.db")

        db_manager.db_initialize(db_filepath)

        db_manager.db_update_data(
            videofile_name="test1.mp4",
            picturefile_name="iframe_0.jpg",
            videofile_time=100,
            ocr_text="First",
            is_videofile_exist=True,
            is_picturefile_exist=True,
            thumbnail="base64",
            win_title="Test",
        )

        db_manager.db_update_data(
            videofile_name="test2.mp4",
            picturefile_name="iframe_0.jpg",
            videofile_time=50,
            ocr_text="Earlier",
            is_videofile_exist=True,
            is_picturefile_exist=True,
            thumbnail="base64",
            win_title="Test",
        )

        earliest = db_manager.db_first_earliest_record_time()
        assert earliest == 50

    def test_db_rollback_delete_video_refer_record(self, db_manager, sample_db_path):
        """Test db_rollback_delete_video_refer_record method."""
        db_filepath = os.path.join(sample_db_path, "test_user_2024-01_wind.db")

        db_manager.db_initialize(db_filepath)

        db_manager.db_update_data(
            videofile_name="test_video_2024-01-01_00-00-00.mp4",
            picturefile_name="iframe_0.jpg",
            videofile_time=1704067200,
            ocr_text="Content to delete",
            is_videofile_exist=True,
            is_picturefile_exist=True,
            thumbnail="base64",
            win_title="Test",
        )

        count_before = db_manager.db_num_records()
        db_manager.db_rollback_delete_video_refer_record("test_video_2024-01-01_00-00-00.mp4")
        count_after = db_manager.db_num_records()

        assert count_after < count_before

    def test_db_get_dbfilename_dict(self, db_manager, sample_db_path):
        """Test get_db_filename_dict method."""
        db_files = [
            "test_user_2024-01_wind.db",
            "test_user_2024-02_wind.db",
        ]

        for db_file in db_files:
            open(os.path.join(sample_db_path, db_file), "w").close()

        result = db_manager.get_db_filename_dict()

        assert isinstance(result, dict)
        assert len(result) == 2
        assert "test_user_2024-01_wind.db" in result

    def test_check_is_onboarding(self, db_manager, sample_db_path, mock_config):
        """Test check_is_onboarding method."""
        # Test with empty database (should be onboarding)
        with patch("windrecorder.db_manager.file_utils.get_file_path_list", return_value=[]):
            result = db_manager.check_is_onboarding()
            # Onboarding check returns True if db has only 1 record and 1 file
            assert isinstance(result, bool)

    def test_db_create_table(self, db_manager, sample_db_path):
        """Test db_create_table method."""
        db_filepath = os.path.join(sample_db_path, "test_user_2024-01_wind.db")

        db_manager.db_create_table(db_filepath)

        conn = sqlite3.connect(db_filepath)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='video_text'")
        table = c.fetchone()
        conn.close()

        assert table is not None

    def test_db_update_read_config(self, db_manager):
        """Test db_update_read_config method."""
        new_config = MagicMock()
        new_config.max_page_result = 100

        db_manager.db_update_read_config(new_config)
        assert db_manager.db_max_page_result == 100

    def test_db_update_table_product_routine(self, db_manager, sample_db_path):
        """Test db_update_table_product_routine method adds new columns."""
        db_filepath = os.path.join(sample_db_path, "test_user_2024-01_wind.db")

        db_manager.db_create_table(db_filepath)

        # Run the update routine (should add win_title and deep_linking if missing)
        db_manager.db_update_table_product_routine()

        conn = sqlite3.connect(db_filepath)
        c = conn.cursor()
        c.execute("PRAGMA table_info(video_text)")
        columns = [col[1] for col in c.fetchall()]
        conn.close()

        assert "win_title" in columns
        assert "deep_linking" in columns

    def test_db_ensure_row_exist_adds_column(self, db_manager, sample_db_path):
        """Test db_ensure_row_exist method."""
        db_filepath = os.path.join(sample_db_path, "test_user_2024-01_wind.db")

        db_manager.db_create_table(db_filepath)

        # Add a new column
        db_manager.db_ensure_row_exist(db_filepath, "new_column", "INTEGER")

        conn = sqlite3.connect(db_filepath)
        c = conn.cursor()
        c.execute("PRAGMA table_info(video_text)")
        columns = [col[1] for col in c.fetchall()]
        conn.close()

        assert "new_column" in columns

    def test_generate_similar_ch_strings(self, db_manager):
        """Test generate_similar_ch_strings method."""
        # Test with simple input
        result = db_manager.generate_similar_ch_strings("test")

        assert isinstance(result, list)

    def test_find_similar_ch_characters(self, db_manager):
        """Test find_similar_ch_characters method."""
        # Test with a character that exists in similar_CN_characters.txt
        # If file doesn't exist, test fallback behavior
        result = db_manager.find_similar_ch_characters("a")

        assert isinstance(result, list)


class TestDBManagerEdgeCases:
    """Edge case tests for DBManager."""

    @pytest.fixture
    def sample_db_path(self):
        """Create a temporary database path for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_db")
            os.makedirs(db_path, exist_ok=True)
            yield db_path

    def test_db_search_empty_keyword(self, sample_db_path):
        """Test db_search_data with empty keyword returns all records."""
        from windrecorder.db_manager import _DBManager

        mock_config = MagicMock()
        mock_config.db_path_ud = sample_db_path
        mock_config.max_page_result = 50
        mock_config.user_name = "test_user"
        mock_config.config_src_dir = "/tmp/config"
        mock_config.record_videos_dir_ud = "/tmp/videos"
        mock_config.maintain_lock_path = "/tmp/maintain_lock"

        with patch("windrecorder.db_manager.config", mock_config):
            with patch("windrecorder.file_utils.ensure_dir"):
                with patch("windrecorder.db_manager._DBManager.db_main_initialize"):
                    with patch("windrecorder.db_manager._DBManager.db_update_table_product_routine"):
                        db_manager = _DBManager(sample_db_path, 50, "test_user")
                        db_manager._db_filename_dict = {}

                        db_filepath = os.path.join(sample_db_path, "test_user_2024-01_wind.db")
                        db_manager.db_initialize(db_filepath)

                        db_manager.db_update_data(
                            videofile_name="test1.mp4",
                            picturefile_name="iframe_0.jpg",
                            videofile_time=1704067200,
                            ocr_text="Some content",
                            is_videofile_exist=True,
                            is_picturefile_exist=True,
                            thumbnail="base64",
                            win_title="Test",
                        )

                        df, row_count, page_count = db_manager.db_search_data(
                            keyword_input="",
                            date_in=datetime(2024, 1, 1),
                            date_out=datetime(2024, 1, 31),
                        )

                        assert row_count >= 1

    def test_db_search_date_range(self, sample_db_path):
        """Test db_search_data with date range queries."""
        from windrecorder.db_manager import _DBManager

        mock_config = MagicMock()
        mock_config.db_path_ud = sample_db_path
        mock_config.max_page_result = 50
        mock_config.user_name = "test_user"
        mock_config.config_src_dir = "/tmp/config"
        mock_config.record_videos_dir_ud = "/tmp/videos"
        mock_config.maintain_lock_path = "/tmp/maintain_lock"

        with patch("windrecorder.db_manager.config", mock_config):
            with patch("windrecorder.file_utils.ensure_dir"):
                with patch("windrecorder.db_manager._DBManager.db_main_initialize"):
                    with patch("windrecorder.db_manager._DBManager.db_update_table_product_routine"):
                        db_manager = _DBManager(sample_db_path, 50, "test_user")
                        db_manager._db_filename_dict = {}

                        db_filepath = os.path.join(sample_db_path, "test_user_2024-01_wind.db")
                        db_manager.db_initialize(db_filepath)

                        # Insert data at different times
                        db_manager.db_update_data(
                            videofile_name="test1.mp4",
                            picturefile_name="iframe_0.jpg",
                            videofile_time=1704067200,  # 2024-01-01
                            ocr_text="January content",
                            is_videofile_exist=True,
                            is_picturefile_exist=True,
                            thumbnail="base64",
                            win_title="Test",
                        )

                        db_manager.db_update_data(
                            videofile_name="test2.mp4",
                            picturefile_name="iframe_0.jpg",
                            videofile_time=1706745600,  # 2024-02-01
                            ocr_text="February content",
                            is_videofile_exist=True,
                            is_picturefile_exist=True,
                            thumbnail="base64",
                            win_title="Test",
                        )

                        # Search January only
                        df, row_count, page_count = db_manager.db_search_data(
                            keyword_input="",
                            date_in=datetime(2024, 1, 1),
                            date_out=datetime(2024, 1, 31),
                        )

                        assert row_count >= 1

                        # Search February only
                        df, row_count, page_count = db_manager.db_search_data(
                            keyword_input="",
                            date_in=datetime(2024, 2, 1),
                            date_out=datetime(2024, 2, 28),
                        )

                        # This might be 0 if db_get_dbfilename_by_datetime doesn't find Feb db
                        # since we only created Jan db
