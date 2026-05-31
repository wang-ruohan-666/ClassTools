# main.pu
import logging
import sys
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow
from common.logger import setup_logger, get_logger
from managers.settings_manager import SettingsManager
from managers.theme_manager import ThemeManager

LOG_LEVEL = logging.DEBUG if "--debug" in sys.argv else logging.INFO
setup_logger(level=LOG_LEVEL,log_to_console=True,log_to_file=True)
logger = get_logger(__name__)

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon.fromTheme("computer"))
    settings_mgr = SettingsManager()
    theme_mgr = ThemeManager(settings_mgr)
    window = MainWindow(settings_mgr, theme_mgr)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()