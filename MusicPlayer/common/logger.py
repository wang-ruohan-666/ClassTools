import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

_LOGGER_CONFIGURED = False

DEFAULT_LOG_DIR = Path.home()/"MusicPlayer"/"logs"

LOG_FORMAT = "%(asctime)s-%(name)s-%(levelname)s-[%(threadName)s] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(
        level:int = logging.INFO,
        log_dir:Optional[Path] = None,
        log_to_console:bool = True,
        log_to_file:bool = True,
        max_bytes:int = 10*1024*1024,
        backup_count:int = 5,
)->None:
    """
        全局日志配置，应在应用启动时调用一次。
        :param level: 全局日志级别
        :param log_dir: 日志文件目录，默认为用户目录下的 MusicPlayer/logs
        :param log_to_console: 是否输出到控制台
        :param log_to_file: 是否输出到文件
        :param max_bytes: 单个日志文件最大字节数
        :param backup_count: 保留的日志文件数量
    """
    global _LOGGER_CONFIGURED
    if _LOGGER_CONFIGURED:
        return
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    formatter = logging.Formatter(LOG_FORMAT,DATE_FORMAT)

    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    if log_to_file:
        if log_dir is None:
            log_dir = DEFAULT_LOG_DIR
        log_dir.mkdir(parents=True,exist_ok=True)
        file_path = log_dir / "app.log"
        file_handler = logging.handlers.TimedRotatingFileHandler(
            file_path, backupCount=backup_count,encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        _LOGGER_CONFIGURED = True
        logging.info("日志系统初始化完成，日志目录: %s", log_dir)

def get_logger(name:str)->logging.Logger:
    """
        获取指定名称的 logger。
        建议使用模块的 __name__ 作为参数。
    """
    return logging.getLogger(name)