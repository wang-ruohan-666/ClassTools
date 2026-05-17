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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QPushButton, QRadioButton, QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1006, 174)
        Form.setStyleSheet(u"")
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(280, 0, 411, 45))
        self.frame.setMinimumSize(QSize(0, 45))
        self.frame.setStyleSheet(u"QWidget#Form > QFrame#frame{\n"
"    border: 2px solid rgb(119, 136, 153);\n"
"	background-color:#ebebeb; \n"
"	border-radius:15px;\n"
"}")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_2 = QFrame(self.frame)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setGeometry(QRect(10, 4, 991, 41))
        self.frame_2.setStyleSheet(u"")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.frame_2)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(0, 0))

        self.horizontalLayout.addWidget(self.label)

        self.radioButton = QRadioButton(self.frame_2)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setEnabled(True)
        self.radioButton.setMouseTracking(True)
        self.radioButton.setTabletTracking(False)
        self.radioButton.setAcceptDrops(False)
        self.radioButton.setAutoFillBackground(False)
        self.radioButton.setStyleSheet(u"QRadioButton::indicator {\n"
"    width: 10px;\n"
"    height: 10px;\n"
"    border-radius: 6px;\n"
"	border: 2px solid rgb(226, 226, 226);\n"
"    background: rgb(242, 255, 0);\n"
"}")

        self.horizontalLayout.addWidget(self.radioButton, 0, Qt.AlignmentFlag.AlignRight)

        self.options = QFrame(self.frame)
        self.options.setObjectName(u"options")
        self.options.setGeometry(QRect(90, 30, 831, 41))
        self.options.setFrameShape(QFrame.Shape.StyledPanel)
        self.options.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.options)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.allow = QPushButton(self.options)
        self.allow.setObjectName(u"allow")
        self.allow.setMinimumSize(QSize(91, 31))
        self.allow.setMaximumSize(QSize(198, 31))
        self.allow.setSizeIncrement(QSize(28, 0))
        self.allow.setBaseSize(QSize(32, 0))
        self.allow.setStyleSheet(u"QPushButton{\n"
"	background-color:rgb(255, 255, 255); \n"
"	border-radius:8px;\n"
"}")

        self.horizontalLayout_2.addWidget(self.allow)

        self.refuse = QPushButton(self.options)
        self.refuse.setObjectName(u"refuse")
        self.refuse.setMinimumSize(QSize(197, 31))
        self.refuse.setMaximumSize(QSize(197, 31))
        self.refuse.setStyleSheet(u"QPushButton{\n"
"	background-color:rgb(255, 255, 255); \n"
"	border-radius:8px;\n"
"}")
        self.refuse.setFlat(False)

        self.horizontalLayout_2.addWidget(self.refuse)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle("")
        self.label.setText(QCoreApplication.translate("Form", u"Hello Word!", None))
        self.radioButton.setText("")
        self.allow.setText(QCoreApplication.translate("Form", u"\u5141\u8bb8", None))
        self.refuse.setText(QCoreApplication.translate("Form", u"\u62d2\u7edd", None))
    # retranslateUi

