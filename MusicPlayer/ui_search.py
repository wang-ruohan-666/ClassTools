# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'search.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1016, 652)
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(10, 20, 1001, 631))
        self.frame.setMinimumSize(QSize(0, 45))
        self.frame.setStyleSheet(u"QWidget#Form > QFrame#frame{\n"
"    border: 2px solid rgb(159, 159, 159);\n"
"	background-color:#ebebeb; \n"
"	border-bottom-left-radius: 15px;\n"
"    border-bottom-right-radius: 15px;\n"
"    border-top-left-radius: 0px;\n"
"    border-top-right-radius: 0px;\n"
"}")
        self.inputFrame = QFrame(self.frame)
        self.inputFrame.setObjectName(u"inputFrame")
        self.inputFrame.setGeometry(QRect(10, 20, 981, 45))
        self.inputFrame.setMinimumSize(QSize(0, 45))
        self.inputFrame.setStyleSheet(u"QWidget#frame > QFrame#inputFrame{\n"
"    border: 2px solid rgb(159, 159, 159);\n"
"	background-color:rgb(244, 244, 244); \n"
"	border-radius:15px;\n"
"}")
        self.inputFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.inputFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.searchLineEdit = QLineEdit(self.inputFrame)
        self.searchLineEdit.setObjectName(u"searchLineEdit")
        self.searchLineEdit.setGeometry(QRect(10, 7, 961, 30))
        self.searchLineEdit.setStyleSheet(u"QLineEdit{\n"
"	background-color:rgb(244, 244, 244); \n"
"}")
        self.searchLineEdit.setFrame(False)
        self.titlebar = QFrame(Form)
        self.titlebar.setObjectName(u"titlebar")
        self.titlebar.setGeometry(QRect(10, 0, 1001, 31))
        self.titlebar.setStyleSheet(u"QFrame{\n"
"	background-color:rgb(255, 255, 255); \n"
" 	border-bottom-left-radius: 0px;\n"
"    border-bottom-right-radius: 0px;\n"
"    border-top-left-radius: 15px;\n"
"    border-top-right-radius: 15px;\n"
"}")
        self.titlebar.setFrameShape(QFrame.Shape.StyledPanel)
        self.titlebar.setFrameShadow(QFrame.Shadow.Raised)
        self.text = QLabel(self.titlebar)
        self.text.setObjectName(u"text")
        self.text.setGeometry(QRect(10, 10, 61, 16))
        self.text.setMinimumSize(QSize(0, 0))
        font = QFont()
        font.setPointSize(10)
        self.text.setFont(font)
        self.quit = QPushButton(self.titlebar)
        self.quit.setObjectName(u"quit")
        self.quit.setGeometry(QRect(940, 0, 45, 29))
        self.quit.setMinimumSize(QSize(0, 0))
        self.quit.setMaximumSize(QSize(16777215, 16777215))
        self.quit.setStyleSheet(u"QPushButton {\n"
"    background: transparent;\n"
"    border: none;\n"
"    font-size: 18px;\n"
"    padding: 4px 8px;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #e81123;\n"
"    color: #ffffff;\n"
"}")

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u6b4c\u66f2\u641c\u7d22", None))
        self.searchLineEdit.setPlaceholderText(QCoreApplication.translate("Form", u"\u8fd9\u91cc\u62e5\u6709\u4e00\u5207......", None))
        self.text.setText(QCoreApplication.translate("Form", u"\u6b4c\u66f2\u641c\u7d22", None))
        self.quit.setText(QCoreApplication.translate("Form", u"\u2715", None))
    # retranslateUi

