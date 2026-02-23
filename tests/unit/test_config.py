"""Unit tests for Windrecorder config module."""
import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock


class TestConfig:
    """Tests for the Config class."""

    @pytest.fixture
    def sample_config_data(self):
        """Sample config data for testing."""
        return {
            "config_src_dir": "windrecorder/config_src",
            "db_path": "db/record.db",
            "vdb_img_path": "userdata/vdb_img",
            "record_videos_dir": "userdata/videos",
            "record_seconds": 30,
            "record_framerate": 10,
            "record_bitrate": "4M",
            "lang": "en",
            "ocr_lang": "en",
            "third_party_engine_ocr_lang": "",
            "ocr_engine": "windows_ocr",
            "ocr_short_size": 1500,
            "max_page_result": 50,
            "target_screen_res": 1080,
            "exclude_words": [],
            "wordcloud_user_stop_words": [],
            "vid_store_day": 30,
            "vid_compress_day": 15,
            "OCR_index_strategy": 0,
            "wordcloud_result_dir": "userdata/wordcloud",
            "screentime_not_change_to_pause_record": 5,
            "timeline_result_dir": "userdata/timeline",
            "user_name": "test_user",
            "use_similar_ch_char_to_search": True,
            "ocr_image_crop_URBL": [0, 0, 0, 0],
            "lightbox_result_dir": "userdata/lightbox",
            "wintitle_result_dir": "userdata/wintitle",
            "date_state_dir": "userdata/stat",
            "ai_extract_tag_result_dir": "userdata/ai_tag",
            "ai_day_poem_result_dir": "userdata/ai_poem",
            "release_ver": False,
            "video_compress_rate": 0.5,
            "oneday_timeline_pic_num": 12,
            "compress_encoder": "libx264",
            "compress_accelerator": "auto",
            "compress_quality": 23,
            "day_begin_minutes": 480,
            "lock_file_dir": "lock_files",
            "maintain_lock_subdir": "maintain",
            "record_lock_name": "record.lock",
            "tray_lock_name": "tray.lock",
            "img_emb_lock_name": "img_emb.lock",
            "last_idle_maintain_file_path": "last_maintain.json",
            "iframe_dir": "userdata/iframe",
            "log_dir": "logs",
            "win_title_dir": "userdata/wintitle",
            "start_recording_on_startup": False,
            "userdata_dir": "userdata",
            "flag_mark_note_filename": "flag_mark.txt",
            "search_history_note_filename": "search_history.txt",
            "thumbnail_generation_size_width": 200,
            "thumbnail_generation_jpg_quality": 85,
            "webui_access_password_md5": "",
            "enable_img_embed_search": True,
            "img_embed_search_recall_result_per_db": 100,
            "img_embed_module_install": True,
            "enable_search_history_record": True,
            "batch_size_embed_video_in_idle": 5,
            "batch_size_remove_video_in_idle": 10,
            "batch_size_compress_video_in_idle": 5,
            "enable_3_columns_in_oneday": True,
            "enable_synonyms_recommend": False,
            "multi_display_record_strategy": "all",
            "record_single_display_index": 1,
            "record_encoder": "h264_nvenc",
            "record_crf": 23,
            "index_reduce_same_content_at_different_time": True,
            "record_screenshot_method_capture_foreground_window_only": False,
            "screenshot_interval_second": 1,
            "screenshot_interrupt_recording_count": 3,
            "record_mode": "ffmpeg",
            "screenshot_compare_similarity": 0.9,
            "ocr_compare_similarity": 0.8,
            "ocr_compare_similarity_in_table": 0.9,
            "foreground_window_video_background_color": "#000000",
            "is_record_system_sound": False,
            "record_foreground_window_process_name": "",
            "record_deep_linking": True,
            "support_ocr_lst": ["en", "ch"],
            "TesseractOCR_filepath": "/usr/bin/tesseract",
            "open_ai_base_url": "https://api.openai.com/v1",
            "open_ai_api_key": "test-key",
            "open_ai_modelname": "gpt-4",
            "enable_ai_extract_tag": False,
            "ai_api_endpoint_type": "openai",
            "ai_api_endpoint_selected": 0,
            "ai_extract_tag_wintitle_limit": 3,
            "enable_ai_extract_tag_in_idle": True,
            "ai_extract_tag_in_idle_batch_size": 3,
            "ai_extract_max_tag_num": 10,
            "enable_ai_day_poem": False,
            "ai_extract_tag_filter_words": [],
            "enable_month_lightbox_watermark": False,
            "custom_background_filepath": "",
            "custom_background_opacity": 0.5,
            "convert_screenshots_to_vid_energy_saving_mode": 0,
            "enable_ocr_str_highlight_indicator": True,
            "recycle_deleted_files": True,
        }

    def test_config_initialization(self, sample_config_data):
        """Test Config class initialization."""
        from windrecorder.config import Config

        config = Config(**sample_config_data)
        assert config.record_seconds == 30
        assert config.max_page_result == 50
        assert config.user_name == "test_user"

    def test_config_set_and_save(self, sample_config_data):
        """Test Config set_and_save method."""
        from windrecorder.config import Config

        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(**sample_config_data)
            config.userdata_dir = tmpdir
            config.config_src_dir = os.path.join(tmpdir, "config_src")
            os.makedirs(config.config_src_dir, exist_ok=True)

            # Test setting a new value
            config.set_and_save_config("record_seconds", 60)
            assert config.record_seconds == 60

    def test_config_filter_unwanted_field(self, sample_config_data):
        """Test Config filter_unwanted_field method."""
        from windrecorder.config import Config

        config = Config(**sample_config_data)
        test_dict = {"keep": "value", "config_src_dir": "should_remove"}
        result = config.filter_unwanted_field(test_dict)
        assert "keep" in result
