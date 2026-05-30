# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'playlist.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(373, 610)
        self.titlebar = QFrame(Form)
        self.titlebar.setObjectName(u"titlebar")
        self.titlebar.setGeometry(QRect(0, 0, 371, 35))
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
        font = QFont()
        font.setPointSize(10)
        self.text.setFont(font)
        self.png = QPushButton(self.titlebar)
        self.png.setObjectName(u"png")
        self.png.setGeometry(QRect(320, 3, 30, 30))
        self.png.setStyleSheet(u"QPushButton { \n"
"	border-radius:3px;\n"
"	padding: 50px; \n"
"	background: transparent; \n"
"	border: none; \n"
"}\n"
"QPushButton:hover { \n"
"	background-color: #f0f0f0; \n"
"}")
        self.root = QFrame(Form)
        self.root.setObjectName(u"root")
        self.root.setGeometry(QRect(0, 30, 371, 571))
        self.root.setStyleSheet(u"#root{\n"
"	background-color:#F0F0F0;\n"
"    border-bottom-left-radius: 15px;\n"
"    border-bottom-right-radius: 15px;\n"
"    border-top-left-radius: 0px;\n"
"    border-top-right-radius: 0px;\n"
"}")
        self.root.setFrameShape(QFrame.Shape.StyledPanel)
        self.root.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.root)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.root.raise_()
        self.titlebar.raise_()

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u64ad\u653e\u5217\u8868", None))
        self.text.setText(QCoreApplication.translate("Form", u"\u64ad\u653e\u5217\u8868", None))
        self.png.setText("")
    # retranslateUi

