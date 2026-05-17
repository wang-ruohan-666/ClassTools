# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QProgressBar, QPushButton, QSizePolicy,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(780, 539)
        self.gridLayoutWidget = QWidget(Form)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(10, 90, 761, 371))
        self.grid_buttons = QGridLayout(self.gridLayoutWidget)
        self.grid_buttons.setObjectName(u"grid_buttons")
        self.grid_buttons.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(280, 20, 191, 16))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setTextFormat(Qt.TextFormat.AutoText)
        self.label.setScaledContents(False)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(False)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.layoutWidget = QWidget(Form)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(41, 35, 701, 41))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.btn_folder = QPushButton(self.layoutWidget)
        self.btn_folder.setObjectName(u"btn_folder")
        self.btn_folder.setMaximumSize(QSize(100, 35))

        self.horizontalLayout.addWidget(self.btn_folder)

        self.label_path = QLabel(self.layoutWidget)
        self.label_path.setObjectName(u"label_path")

        self.horizontalLayout.addWidget(self.label_path)

        self.horizontalLayoutWidget = QWidget(Form)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(10, 470, 581, 41))
        self.horizontalLayout_2 = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.btn_switch_mode = QPushButton(self.horizontalLayoutWidget)
        self.btn_switch_mode.setObjectName(u"btn_switch_mode")
        self.btn_switch_mode.setMinimumSize(QSize(126, 31))
        self.btn_switch_mode.setStyleSheet(u"QPushButton {\n"
"        background-color: #4CAF50;\n"
"		border: 1px solid #ADADAD;\n"
"}\n"
"QPushButton:hover {\n"
"    border: 1px solid #0078D7;\n"
"}")

        self.horizontalLayout_2.addWidget(self.btn_switch_mode)

        self.btn_save_config = QPushButton(self.horizontalLayoutWidget)
        self.btn_save_config.setObjectName(u"btn_save_config")
        self.btn_save_config.setMinimumSize(QSize(126, 31))

        self.horizontalLayout_2.addWidget(self.btn_save_config)

        self.btn_load_config = QPushButton(self.horizontalLayoutWidget)
        self.btn_load_config.setObjectName(u"btn_load_config")
        self.btn_load_config.setMinimumSize(QSize(126, 31))

        self.horizontalLayout_2.addWidget(self.btn_load_config)

        self.btn_reset_default = QPushButton(self.horizontalLayoutWidget)
        self.btn_reset_default.setObjectName(u"btn_reset_default")
        self.btn_reset_default.setMinimumSize(QSize(126, 31))

        self.horizontalLayout_2.addWidget(self.btn_reset_default)

        self.btn_save_config.raise_()
        self.btn_load_config.raise_()
        self.btn_reset_default.raise_()
        self.btn_switch_mode.raise_()
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(0, 460, 771, 20))
        self.frame.setFrameShape(QFrame.Shape.HLine)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.layoutWidget1 = QWidget(Form)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(110, 510, 541, 25))
        self.horizontalLayout_3 = QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.progress_label = QLabel(self.layoutWidget1)
        self.progress_label.setObjectName(u"progress_label")

        self.horizontalLayout_3.addWidget(self.progress_label)

        self.progress_bar = QProgressBar(self.layoutWidget1)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setValue(0)
        self.progress_bar.setTextDirection(QProgressBar.Direction.TopToBottom)

        self.horizontalLayout_3.addWidget(self.progress_bar)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u5b8c\u6210\u8fdb\u5ea6", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u9009\u62e9\u6587\u4ef6\u5939\u8def\u5f84", None))
        self.btn_folder.setText(QCoreApplication.translate("Form", u"\u9009\u62e9\u6587\u4ef6\u5939", None))
        self.label_path.setText(QCoreApplication.translate("Form", u"\u6682\u672a\u9009\u62e9......", None))
        self.btn_switch_mode.setText(QCoreApplication.translate("Form", u"\u7f16\u8f91\u6a21\u5f0f", None))
        self.btn_save_config.setText(QCoreApplication.translate("Form", u"\u4fdd\u5b58\u914d\u7f6e", None))
        self.btn_load_config.setText(QCoreApplication.translate("Form", u"\u52a0\u8f7d\u914d\u7f6e", None))
        self.btn_reset_default.setText(QCoreApplication.translate("Form", u"\u8fd8\u539f\u9ed8\u8ba4", None))
        self.progress_label.setText(QCoreApplication.translate("Form", u"\u5b8c\u6210\u8fdb\u5ea6", None))
    # retranslateUi

