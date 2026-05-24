from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class AppConfig:
    frame_option_offset_x: int = -280
    frame_option_expand_width: int = 300
    frame_option_expand_height: int = 40
    frame_login_expand_height: int = 180
    anim_duration_show_text: int = 500
    anim_duration_options: int = 250
    anim_duration_login_img_show: int = 300
    anim_duration_login_img_hide: int = 300
    netease_api_base: str = "http://api.ncm.qzz.io/"
    http_timeout: tuple = (3.0, 10.0)
    http_retry: int = 2
    data_dir: Path = Path("data")
    settings_file: Path = data_dir / "settings.json"
    task_queue_poll_interval: int = 100

    def __post_init__(self):
        self.data_dir.mkdir(exist_ok=True)