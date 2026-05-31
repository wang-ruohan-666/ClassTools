# views/settings_window.py
from PySide6.QtCore import Qt,QPropertyAnimation, QEvent
from PySide6.QtGui import QFont, QMouseEvent
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect

from MusicPlayer.ui_settings import Ui_Form as Settings


class SettingsWindow(QWidget):
    def __init__(self, settings_mgr, theme_mgr):
        super().__init__()
        self.settings_mgr = settings_mgr
        self.theme_mgr = theme_mgr
        self.settings = Settings()
        self.settings.setupUi(self)

        # 动画相关
        self.anim_speed = settings_mgr.anim_speed
        self._settings_drag_pos = None
        self.opacity_effect = QGraphicsOpacityEffect()
        self.settings_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_effect.setOpacity(0.0)

        self.init_settings()
        self.init_settings_anim()
        self.load_initial_values()
        self.connect_signals()


    def init_settings(self):
        self.settings.settingsFrame.hide()
        self.settings.animSpeedFrame.hide()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.settings.treeWidget.itemClicked.connect(self.tree_item_change)
        self.settings.quit.clicked.connect(self.close)
        self.settings.titlebar.installEventFilter(self)
        # 字体下拉框的编辑框点击事件
        self.settings.fontComboBox.lineEdit().installEventFilter(self)
        self.theme_mgr.theme_applied.connect(self._on_theme)

    def init_settings_anim(self):
        self.settings_anim.setDuration(int(300 / self.anim_speed))
        self.settings_anim.setStartValue(0.0)
        self.settings_anim.setEndValue(1.0)
        self.setGraphicsEffect(self.opacity_effect)

    def load_initial_values(self):
        """从 SettingsManager 加载当前值到控件"""
        self.settings.comboBox.setCurrentText(self.settings_mgr.theme)
        self.settings.fontComboBox.setCurrentFont(self.settings_mgr.font)
        # 字体大小滑动条：假设滑块范围 0~100，映射到字体大小 1~20
        self.settings.sliderSlider.setValue(self.settings_mgr.font_size * 5)
        self.settings.labelSize.setText(str(self.settings_mgr.font_size))
        # 动画速度：滑块 0~20，映射到 0.0~2.0
        self.settings.sliderSliderSpeed.setValue(int(self.settings_mgr.anim_speed * 10))
        self.settings.labelSpeed.setText(str(self.settings_mgr.anim_speed))
        self.settings.checkBox.setChecked(self.settings_mgr.stay_on_top)

    def connect_signals(self):
        # 主题下拉框变化 -> 直接修改 SettingsManager.theme
        self.settings.comboBox.currentTextChanged.connect(self._on_theme_combobox_changed)
        # 字体变化 -> 修改 SettingsManager.font
        self.settings.fontComboBox.currentFontChanged.connect(self._on_font_changed)
        # 字体大小滑动条 -> 修改 SettingsManager.font_size
        self.settings.sliderSlider.valueChanged.connect(self._on_font_size_slider)
        # 动画速度滑动条 -> 修改 SettingsManager.anim_speed
        self.settings.sliderSliderSpeed.valueChanged.connect(self._on_anim_speed_slider)
        # 置顶复选框 -> 修改 SettingsManager.stay_on_top
        self.settings.checkBox.toggled.connect(self._on_stay_on_top_toggled)

    def _on_theme(self, theme: str):
        if theme == "dark":
            self._dark()
        elif theme == "light":
            self._light()

    def _dark(self):
        self.setStyleSheet("""
                QWidget 
                {
                    color: #ffffff;
                }
                QMenu {
                    background-color: #2d2d2d;
                    border: 1px solid #5a5a5a;
                    border-radius: 6px;
                    padding: 4px;
                }
                QMenu::item {
                    background-color: transparent;
                    color: #ffffff;
                    padding: 6px 24px 6px 12px;
                    border-radius: 4px;
                    min-width: 120px;
                }
                QMenu::item:selected {
                    background-color: #3c3c3c;
                }
                QMenu::item:disabled {
                    color: #6c6c6c;
                    background-color: transparent;
                }
                QMenu::separator {
                    height: 1px;
                    background: #5a5a5a;
                    margin: 4px 8px;
                }
                QMenu::indicator {
                    width: 14px;
                    height: 14px;
                    margin-left: 4px;
                }
                QMenu::indicator:checked {
                    background-color: #448aff;
                    border-radius: 3px;
                }""")
        self.settings.root.setStyleSheet("""
    #root{
    background-color:#2d2d2d;
    border-bottom-left-radius: 15px;
    border-bottom-right-radius: 15px;
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
    }""")
        self.settings.titlebar.setStyleSheet("""
    QFrame{
    background-color:#1C1B22; 
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
    border-top-left-radius: 15px;
    border-top-right-radius: 15px;
    }""")
        self.settings.treeWidget.setStyleSheet("""
    QTreeWidget {
    color: #ffffff;
    background-color: #2d2d2d;
    border: 1px solid #c0c0c0;
    border-radius: 6px;
    padding: 4px;
    outline: none;
    }""")
        for i in [self.settings.comboBox, self.settings.fontComboBox]:
            i.setStyleSheet("""
    QComboBox {
    background-color: #2d2d2d;
    border: 1px solid #5a5a5a;
    border-radius: 6px;
    padding: 4px 8px;
    min-height: 24px;
    color: #ffffff;
    }
    
    QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #4a4a4a;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
    }
    
    QComboBox::down-arrow {
    width: 8px;
    height: 8px;
    }
    
    QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    border: 1px solid #5a5a5a;
    border-radius: 4px;
    selection-background-color: #3c3c3c;
    selection-color: #ffffff;
    padding: 4px;
    outline: none;
    }
    
    QComboBox QAbstractItemView::item {
    min-height: 24px;
    padding: 4px 8px;
    border-radius: 3px;
    }
    
    QComboBox QAbstractItemView::item:hover {
    background-color: #3c3c3c;
    }""")
        self.settings.sliderSlider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #3c3c3c;
                border-radius: 3px;
                margin: 2px 0;
            }
    
            QSlider::handle:horizontal {
                width: 16px;
                height: 16px;
                margin: -6px 0;
                background: #2d2d2d;
                border: 2px solid #5a5a5a;
                border-radius: 8px;
            }
    
            QSlider::handle:horizontal:hover {
                border-color: #888888;
            }
    
            QSlider::handle:horizontal:pressed {
                background: #4a4a4a;
                border-color: #aaaaaa;
            }
    
            QSlider::sub-page:horizontal {
                background: #448aff;
                border-radius: 3px;
            }
    
            QSlider::add-page:horizontal {
                background: #3c3c3c;
                border-radius: 3px;
            }""")
        self.settings.checkBox.setStyleSheet("""
    QCheckBox {
    spacing: 8px;
    color: #ffffff;
    }
    
    QCheckBox::indicator {
    width: 10px;
    height: 10px;
    border: 2px solid #5a5a5a;
    border-radius: 4px;
    background-color: #2d2d2d;
    }
    
    QCheckBox::indicator:checked {
    background-color: #448aff;
    border-color: #448aff;
    }
    
    QCheckBox::indicator:checked:hover {
    background-color: #5c9dff;
    border-color: #5c9dff;
    }
    
    QCheckBox::indicator:unchecked:hover {
    border-color: #888888;
    }
    
    QCheckBox::indicator:disabled {
    border-color: #4a4a4a;
    background-color: #3c3c3c;
    }
    
    QCheckBox::indicator:checked:disabled {
    background-color: #2a4a8a;
    border-color: #2a4a8a;
    }""")

    def _light(self):
        self.setStyleSheet("""
QMenu {
    background-color: #ffffff;
    border: 1px solid #c0c0c0;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    background-color: transparent;
    color: #000000;
    padding: 6px 24px 6px 12px;
    border-radius: 0px;
    min-width: 120px;
}

QMenu::item:selected {
    background-color: #e0e0e0;
    border-radius: 4px;
}

QMenu::item:disabled {
    color: #a0a0a0;
    background-color: transparent;
}

QMenu::separator {
    height: 1px;
    background: #c0c0c0;
    margin: 4px 8px;
}

QMenu::indicator {
    width: 14px;
    height: 14px;
    margin-left: 4px;
}

QMenu::indicator:checked {
    background-color: #448aff;
    border-radius: 3px;
}""")
        self.settings.root.setStyleSheet("""
#root{
    background-color:#F0F0F0;
    border-bottom-left-radius: 15px;
    border-bottom-right-radius: 15px;
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
}""")
        self.settings.treeWidget.setStyleSheet("""
QTreeWidget {
    background-color: #ffffff;
    border: 1px solid #c0c0c0;
    border-radius: 6px;
    padding: 4px;
    outline: none;
    color: #000000;
}""")
        self.settings.titlebar.setStyleSheet("""
QFrame{
    background-color:rgb(255, 255, 255); 
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
    border-top-left-radius: 15px;
    border-top-right-radius: 15px;
}""")
        for i in [self.settings.comboBox, self.settings.fontComboBox]:
            i.setStyleSheet("""
QComboBox {
    background-color: #ffffff;
    border: 1px solid #c0c0c0;
    border-radius: 6px;
    padding: 4px 8px;
    min-height: 24px;
    color: #000000;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #e0e0e0;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
}

QComboBox::down-arrow {
    width: 8px;
    height: 8px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #c0c0c0;
    border-radius: 4px;
    selection-background-color: #e0e0e0;
    selection-color: #000000;
    padding: 4px;
    outline: none;
}

QComboBox QAbstractItemView::item {
    min-height: 24px;
    padding: 4px 8px;
    border-radius: 3px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #f0f0f0;
}""")
        self.settings.sliderSlider.setStyleSheet("""
        QSlider::groove:horizontal {
            height: 6px;
            background: #e0e0e0;
            border-radius: 3px;
            margin: 2px 0;
        }

        QSlider::handle:horizontal {
            width: 16px;
            height: 16px;
            margin: -6px 0;
            background: #ffffff;
            border: 2px solid #c0c0c0;
            border-radius: 8px;
        }

        QSlider::handle:horizontal:hover {
            border-color: #888888;
        }

        QSlider::handle:horizontal:pressed {
            background: #f0f0f0;
            border-color: #555555;
        }

        QSlider::sub-page:horizontal {
            background: #448aff;
            border-radius: 3px;
        }

        QSlider::add-page:horizontal {
            background: #e0e0e0;
            border-radius: 3px;
        }

        /* 可选：刻度线 */
        QSlider::tick:horizontal {
            background: #c0c0c0;
            width: 1px;
        }""")
        self.settings.checkBox.setStyleSheet("""
QCheckBox {
    spacing: 8px;
    color: #000000;
}

QCheckBox::indicator {
    width: 10px;
    height: 10px;
    border: 2px solid #c0c0c0;
    border-radius: 4px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #448aff;
    border-color: #448aff;
}

QCheckBox::indicator:checked:hover {
    background-color: #5c9dff;
    border-color: #5c9dff;
}

QCheckBox::indicator:unchecked:hover {
    border-color: #888888;
}

QCheckBox::indicator:disabled {
    border-color: #d0d0d0;
    background-color: #f5f5f5;
}

QCheckBox::indicator:checked:disabled {
    background-color: #a0c4ff;
    border-color: #a0c4ff;
}""")

    def _on_theme_combobox_changed(self, text: str):
        if text in ("深色", "浅色", "跟随系统"):
            self.settings_mgr.theme = text

    def _on_font_changed(self, font: QFont):
        self.settings_mgr.font = font
        self.theme_mgr.theme_applied.emit(self.theme_mgr.get_current_theme_name())

    def _on_font_size_slider(self, value: int):
        font_size = round(value / 5.0)
        self.settings.labelSize.setText(str(font_size))
        self.settings_mgr.font_size = font_size
        self.theme_mgr.theme_applied.emit(self.theme_mgr.get_current_theme_name())

    def _on_anim_speed_slider(self, value: int):
        speed = value / 10.0
        self.settings.labelSpeed.setText(f"{speed:.1f}")
        self.settings_mgr.anim_speed = speed
        self.theme_mgr.theme_applied.emit(self.theme_mgr.get_current_theme_name())
        # 更新窗口自身动画时长
        self.anim_speed = speed
        self.settings_anim.setDuration(int(300 / speed))

    def _on_stay_on_top_toggled(self, checked: bool):
        self.settings_mgr.stay_on_top = checked
        if checked:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.show()

        # 窗口置顶标志的视觉更新由 ThemeManager 或主窗口处理，这里仅修改标志

    def tree_item_change(self, item, column):
        self.settings.settingsFrame.hide()
        self.settings.animSpeedFrame.hide()
        text = item.text(column)
        if text == "外观":
            self.settings.settingsFrame.show()
        elif text == "动画":
            self.settings.animSpeedFrame.show()

    def eventFilter(self, watched, event: QEvent | QMouseEvent, /):
        if watched == self.settings.fontComboBox.lineEdit() and event.type() == QEvent.Type.MouseButtonPress:
            self.settings.fontComboBox.showPopup()
            return True
        if watched == self.settings.titlebar:
            if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self._settings_drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                return True
            elif event.type() == QEvent.Type.MouseMove and self._settings_drag_pos is not None:
                new_pos = event.globalPosition().toPoint() - self._settings_drag_pos
                self.move(new_pos)
                return True
            elif event.type() == QEvent.Type.MouseButtonRelease:
                self._settings_drag_pos = None
                return True
        return super().eventFilter(watched, event)

    def showEvent(self, event):
        super().showEvent(event)
        # 确保动画时长与当前动画速度同步
        self.settings_anim.setDuration(int(300 / self.anim_speed))
        self.settings_anim.start()