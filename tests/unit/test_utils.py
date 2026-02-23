"""Unit tests for Windrecorder utility functions."""
import pytest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestTimeUtils:
    """Tests for time-related utility functions."""

    def test_seconds_to_datetime(self):
        """Test seconds to datetime conversion."""
        from windrecorder.utils import seconds_to_datetime

        timestamp = 1704067200  # 2024-01-01 00:00:00 UTC
        dt = seconds_to_datetime(timestamp)

        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 1

    def test_datetime_to_seconds(self):
        """Test datetime to seconds conversion."""
        from windrecorder.utils import datetime_to_seconds

        dt = datetime(2024, 1, 1, 12, 0, 0)
        timestamp = datetime_to_seconds(dt)

        assert isinstance(timestamp, int)
        assert timestamp > 0

    def test_dtstr_to_seconds(self):
        """Test datetime string to seconds conversion."""
        from windrecorder.utils import dtstr_to_seconds

        dt_str = "2024-01-01_12-00-00"
        timestamp = dtstr_to_seconds(dt_str)

        assert isinstance(timestamp, int)
        assert timestamp > 0

    def test_seconds_to_datetime_string(self):
        """Test seconds to datetime string conversion."""
        from windrecorder.utils import seconds_to_datetime

        timestamp = 1704067200
        dt = seconds_to_datetime(timestamp)

        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 1

    def test_convert_seconds_to_hhmmss(self):
        """Test seconds to HH:MM:SS format conversion."""
        from windrecorder.utils import convert_seconds_to_hhmmss

        # Test 1 hour
        result = convert_seconds_to_hhmmss(3600)
        assert result == "01:00:00"

        # Test 1 hour 30 minutes
        result = convert_seconds_to_hhmmss(5400)
        assert result == "01:30:00"

        # Test 1 hour 30 minutes 45 seconds
        result = convert_seconds_to_hhmmss(5445)
        assert result == "01:30:45"

    def test_convert_seconds_to_hhmmss_zero(self):
        """Test seconds to HH:MM:SS format with zero."""
        from windrecorder.utils import convert_seconds_to_hhmmss

        result = convert_seconds_to_hhmmss(0)
        assert result == "00:00:00"


class TestDateUtils:
    """Tests for date-related utility functions."""

    def test_set_full_datetime_to_YYYY_MM(self):
        """Test datetime to YYYY-MM format conversion."""
        from windrecorder.utils import set_full_datetime_to_YYYY_MM

        dt = datetime(2024, 1, 15, 12, 30, 45)
        result = set_full_datetime_to_YYYY_MM(dt)

        assert result == "2024-01"

    def test_get_datetime_in_day_range_pole_by_config_day_begin(self):
        """Test day range pole calculation."""
        from windrecorder.utils import get_datetime_in_day_range_pole_by_config_day_begin

        # Test with 8AM day begin (480 minutes)
        dt = datetime(2024, 1, 15, 14, 0, 0)  # 2 PM
        start = get_datetime_in_day_range_pole_by_config_day_begin(dt, range="start")

        assert start.hour == 8  # Day begins at 8 AM
        assert start.minute == 0

    def test_days_between_dates(self):
        """Test days between dates calculation."""
        from windrecorder.utils import get_day_from_datetime

        dt1 = datetime(2024, 1, 1)
        dt2 = datetime(2024, 1, 15)

        # Just verify the functions exist and return expected types
        result1 = get_day_from_datetime(dt1)
        result2 = get_day_from_datetime(dt2)

        assert isinstance(result1, int)
        assert isinstance(result2, int)


class TestFileUtils:
    """Tests for file-related utility functions."""

    def test_get_file_path_list(self):
        """Test file path listing."""
        from windrecorder import file_utils
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some test files
            open(os.path.join(tmpdir, "file1.txt"), "w").close()
            open(os.path.join(tmpdir, "file2.txt"), "w").close()

            result = file_utils.get_file_path_list(tmpdir)

            assert isinstance(result, list)
            assert len(result) == 2

    def test_ensure_dir(self):
        """Test directory creation."""
        from windrecorder import file_utils
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = os.path.join(tmpdir, "new_subdir")
            file_utils.ensure_dir(new_dir)

            assert os.path.isdir(new_dir)


class TestConfigUtils:
    """Tests for config-related utility functions."""

    def test_get_text(self):
        """Test get_text function exists."""
        from windrecorder.utils import get_text

        # Test with a simple key
        result = get_text("main_title")

        # The result should be a string
        assert isinstance(result, str)
        assert len(result) > 0
