# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFontComboBox,
    QFrame, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QSizePolicy, QSlider,
    QTreeWidget, QTreeWidgetItem, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(620, 385)
        Form.setStyleSheet(u"")
        self.titlebar = QFrame(Form)
        self.titlebar.setObjectName(u"titlebar")
        self.titlebar.setGeometry(QRect(0, 0, 621, 30))
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
        self.text.setGeometry(QRect(10, 10, 30, 15))
        self.text.setMinimumSize(QSize(0, 0))
        font = QFont()
        font.setPointSize(10)
        self.text.setFont(font)
        self.quit = QPushButton(self.titlebar)
        self.quit.setObjectName(u"quit")
        self.quit.setGeometry(QRect(560, 0, 45, 29))
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
        self.root = QFrame(Form)
        self.root.setObjectName(u"root")
        self.root.setGeometry(QRect(0, 30, 621, 351))
        self.root.setStyleSheet(u"#root{\n"
"	background-color:#F0F0F0;\n"
"    border-bottom-left-radius: 15px;\n"
"    border-bottom-right-radius: 15px;\n"
"    border-top-left-radius: 0px;\n"
"    border-top-right-radius: 0px;\n"
"}")
        self.root.setFrameShape(QFrame.Shape.StyledPanel)
        self.root.setFrameShadow(QFrame.Shadow.Raised)
        self.treeWidget = QTreeWidget(self.root)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setTextAlignment(0, Qt.AlignLeading|Qt.AlignVCenter)
        self.treeWidget.setHeaderItem(__qtreewidgetitem)
        __qtreewidgetitem1 = QTreeWidgetItem(self.treeWidget)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(self.treeWidget)
        self.treeWidget.setObjectName(u"treeWidget")
        self.treeWidget.setGeometry(QRect(10, 0, 151, 331))
        self.treeWidget.setStyleSheet(u"QTreeWidget {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #c0c0c0;\n"
"    border-radius: 6px;\n"
"    padding: 4px;\n"
"    outline: none;\n"
"    color: #000000;\n"
"}")
        self.treeWidget.setIndentation(10)
        self.treeWidget.setColumnCount(1)
        self.treeWidget.header().setVisible(False)
        self.settingsFrame = QFrame(self.root)
        self.settingsFrame.setObjectName(u"settingsFrame")
        self.settingsFrame.setGeometry(QRect(170, 0, 441, 321))
        self.settingsFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.settingsFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayoutWidget_2 = QWidget(self.settingsFrame)
        self.gridLayoutWidget_2.setObjectName(u"gridLayoutWidget_2")
        self.gridLayoutWidget_2.setGeometry(QRect(0, 10, 431, 135))
        self.settingsGrid = QGridLayout(self.gridLayoutWidget_2)
        self.settingsGrid.setObjectName(u"settingsGrid")
        self.settingsGrid.setContentsMargins(0, 0, 0, 0)
        self.labelFontSize = QLabel(self.gridLayoutWidget_2)
        self.labelFontSize.setObjectName(u"labelFontSize")
        self.labelFontSize.setMaximumSize(QSize(16777215, 34))

        self.settingsGrid.addWidget(self.labelFontSize, 2, 1, 1, 1)

        self.sliderGroup = QHBoxLayout()
        self.sliderGroup.setObjectName(u"sliderGroup")
        self.sliderSlider = QSlider(self.gridLayoutWidget_2)
        self.sliderSlider.setObjectName(u"sliderSlider")
        self.sliderSlider.setMaximumSize(QSize(372, 16777215))
        self.sliderSlider.setStyleSheet(u"QSlider::groove:horizontal {\n"
"    height: 6px;\n"
"    background: #e0e0e0;\n"
"    border-radius: 3px;\n"
"    margin: 2px 0;\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"    width: 16px;\n"
"    height: 16px;\n"
"    margin: -6px 0;\n"
"    background: #ffffff;\n"
"    border: 2px solid #c0c0c0;\n"
"    border-radius: 8px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal:hover {\n"
"    border-color: #888888;\n"
"}\n"
"\n"
"QSlider::handle:horizontal:pressed {\n"
"    background: #f0f0f0;\n"
"    border-color: #555555;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal {\n"
"    background: #448aff;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QSlider::add-page:horizontal {\n"
"    background: #e0e0e0;\n"
"    border-radius: 3px;\n"
"}")
        self.sliderSlider.setMinimum(25)
        self.sliderSlider.setMaximum(100)
        self.sliderSlider.setValue(50)
        self.sliderSlider.setOrientation(Qt.Orientation.Horizontal)
        self.sliderSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sliderSlider.setTickInterval(1)

        self.sliderGroup.addWidget(self.sliderSlider)

        self.labelSize = QLabel(self.gridLayoutWidget_2)
        self.labelSize.setObjectName(u"labelSize")

        self.sliderGroup.addWidget(self.labelSize)


        self.settingsGrid.addLayout(self.sliderGroup, 2, 2, 1, 1)

        self.fontComboBox = QFontComboBox(self.gridLayoutWidget_2)
        self.fontComboBox.setObjectName(u"fontComboBox")
        self.fontComboBox.setStyleSheet(u"QComboBox {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #c0c0c0;\n"
"    border-radius: 6px;\n"
"    padding: 4px 8px;\n"
"    min-height: 24px;\n"
"    color: #000000;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 24px;\n"
"    border-left: 1px solid #e0e0e0;\n"
"    border-top-right-radius: 6px;\n"
"    border-bottom-right-radius: 6px;\n"
"}\n"
"\n"
"QComboBox::down-arrow {\n"
"    width: 8px;\n"
"    height: 8px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #c0c0c0;\n"
"    border-radius: 4px;\n"
"    selection-background-color: #e0e0e0;\n"
"    selection-color: #000000;\n"
"    padding: 4px;\n"
"    outline: none;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView::item {\n"
"    min-height: 24px;\n"
"    padding: 4px 8px;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView::item:hover {\n"
"    background-color: #f0f0f0;\n"
"}")

        self.settingsGrid.addWidget(self.fontComboBox, 1, 2, 1, 1)

        self.labelTopic = QLabel(self.gridLayoutWidget_2)
        self.labelTopic.setObjectName(u"labelTopic")
        self.labelTopic.setMaximumSize(QSize(16777215, 16777215))

        self.settingsGrid.addWidget(self.labelTopic, 0, 1, 1, 1)

        self.comboBox = QComboBox(self.gridLayoutWidget_2)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setStyleSheet(u"QComboBox {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #c0c0c0;\n"
"    border-radius: 6px;\n"
"    padding: 4px 8px;\n"
"    min-height: 24px;\n"
"    color: #000000;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 24px;\n"
"    border-left: 1px solid #e0e0e0;\n"
"    border-top-right-radius: 6px;\n"
"    border-bottom-right-radius: 6px;\n"
"}\n"
"\n"
"QComboBox::down-arrow {\n"
"    width: 8px;\n"
"    height: 8px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #c0c0c0;\n"
"    border-radius: 4px;\n"
"    selection-background-color: #e0e0e0;\n"
"    selection-color: #000000;\n"
"    padding: 4px;\n"
"    outline: none;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView::item {\n"
"    min-height: 24px;\n"
"    padding: 4px 8px;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView::item:hover {\n"
"    background-color: #f0f0f0;\n"
"}")

        self.settingsGrid.addWidget(self.comboBox, 0, 2, 1, 1)

        self.labelFont = QLabel(self.gridLayoutWidget_2)
        self.labelFont.setObjectName(u"labelFont")

        self.settingsGrid.addWidget(self.labelFont, 1, 1, 1, 1)

        self.checkBox = QCheckBox(self.gridLayoutWidget_2)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setStyleSheet(u"QCheckBox {\n"
"    spacing: 8px;\n"
"    color: #000000;\n"
"}\n"
"\n"
"QCheckBox::indicator {\n"
"    width: 10px;\n"
"    height: 10px;\n"
"    border: 2px solid #c0c0c0;\n"
"    border-radius: 4px;\n"
"    background-color: #ffffff;\n"
"}\n"
"\n"
"QCheckBox::indicator:checked {\n"
"    background-color: #448aff;        /* \u9009\u4e2d\u65f6\u84dd\u8272\u80cc\u666f */\n"
"    border-color: #448aff;\n"
"}\n"
"\n"
"QCheckBox::indicator:checked:hover {\n"
"    background-color: #5c9dff;\n"
"    border-color: #5c9dff;\n"
"}\n"
"\n"
"QCheckBox::indicator:unchecked:hover {\n"
"    border-color: #888888;\n"
"}\n"
"\n"
"QCheckBox::indicator:disabled {\n"
"    border-color: #d0d0d0;\n"
"    background-color: #f5f5f5;\n"
"}\n"
"\n"
"QCheckBox::indicator:checked:disabled {\n"
"    background-color: #a0c4ff;        /* \u9009\u4e2d\u4f46\u7981\u7528\u65f6\u7528\u6de1\u84dd\u8272 */\n"
"    border-color: #a0c4ff;\n"
"}")
        self.checkBox.setChecked(True)

        self.settingsGrid.addWidget(self.checkBox, 3, 2, 1, 1)

        self.animSpeedFrame = QFrame(self.root)
        self.animSpeedFrame.setObjectName(u"animSpeedFrame")
        self.animSpeedFrame.setGeometry(QRect(170, 10, 431, 31))
        self.layoutWidget = QWidget(self.animSpeedFrame)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(1, 1, 429, 31))
        self.animHBox = QHBoxLayout(self.layoutWidget)
        self.animHBox.setObjectName(u"animHBox")
        self.animHBox.setContentsMargins(0, 0, 0, 0)
        self.labelSpeedSize = QLabel(self.layoutWidget)
        self.labelSpeedSize.setObjectName(u"labelSpeedSize")
        self.labelSpeedSize.setMaximumSize(QSize(16777215, 34))

        self.animHBox.addWidget(self.labelSpeedSize)

        self.sliderAnimGroup = QHBoxLayout()
        self.sliderAnimGroup.setObjectName(u"sliderAnimGroup")
        self.sliderSliderSpeed = QSlider(self.layoutWidget)
        self.sliderSliderSpeed.setObjectName(u"sliderSliderSpeed")
        self.sliderSliderSpeed.setMaximumSize(QSize(372, 16777215))
        self.sliderSliderSpeed.setStyleSheet(u"QSlider::groove:horizontal {\n"
"    height: 6px;\n"
"    background: #e0e0e0;\n"
"    border-radius: 3px;\n"
"    margin: 2px 0;\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"    width: 16px;\n"
"    height: 16px;\n"
"    margin: -6px 0;\n"
"    background: #ffffff;\n"
"    border: 2px solid #c0c0c0;\n"
"    border-radius: 8px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal:hover {\n"
"    border-color: #888888;\n"
"}\n"
"\n"
"QSlider::handle:horizontal:pressed {\n"
"    background: #f0f0f0;\n"
"    border-color: #555555;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal {\n"
"    background: #448aff;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QSlider::add-page:horizontal {\n"
"    background: #e0e0e0;\n"
"    border-radius: 3px;\n"
"}")
        self.sliderSliderSpeed.setMinimum(1)
        self.sliderSliderSpeed.setMaximum(50)
        self.sliderSliderSpeed.setValue(10)
        self.sliderSliderSpeed.setOrientation(Qt.Orientation.Horizontal)
        self.sliderSliderSpeed.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sliderSliderSpeed.setTickInterval(1)

        self.sliderAnimGroup.addWidget(self.sliderSliderSpeed)

        self.labelSpeed = QLabel(self.layoutWidget)
        self.labelSpeed.setObjectName(u"labelSpeed")

        self.sliderAnimGroup.addWidget(self.labelSpeed)


        self.animHBox.addLayout(self.sliderAnimGroup)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u8bbe\u7f6e", None))
        self.text.setText(QCoreApplication.translate("Form", u"\u8bbe\u7f6e", None))
        self.quit.setText(QCoreApplication.translate("Form", u"\u2715", None))
        ___qtreewidgetitem = self.treeWidget.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("Form", u"\u8bbe\u7f6e", None))

        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        ___qtreewidgetitem1 = self.treeWidget.topLevelItem(0)
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("Form", u"\u4e2a\u6027\u5316", None))
        ___qtreewidgetitem2 = ___qtreewidgetitem1.child(0)
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("Form", u"\u5916\u89c2", None))
        ___qtreewidgetitem3 = ___qtreewidgetitem1.child(1)
        ___qtreewidgetitem3.setText(0, QCoreApplication.translate("Form", u"\u52a8\u753b", None))
        ___qtreewidgetitem4 = self.treeWidget.topLevelItem(1)
        ___qtreewidgetitem4.setText(0, QCoreApplication.translate("Form", u"\u5173\u4e8e", None))
        self.treeWidget.setSortingEnabled(__sortingEnabled)

        self.labelFontSize.setText(QCoreApplication.translate("Form", u"\u5927\u5c0f:", None))
        self.labelSize.setText(QCoreApplication.translate("Form", u"10", None))
        self.labelTopic.setText(QCoreApplication.translate("Form", u"\u4e3b\u9898:", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Form", u"\u8ddf\u968f\u7cfb\u7edf", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("Form", u"\u6d45\u8272", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("Form", u"\u6df1\u8272", None))

        self.labelFont.setText(QCoreApplication.translate("Form", u"\u5b57\u4f53:", None))
        self.checkBox.setText(QCoreApplication.translate("Form", u"\u4fdd\u6301\u7f6e\u9876", None))
        self.labelSpeedSize.setText(QCoreApplication.translate("Form", u"\u901f\u5ea6:", None))
        self.labelSpeed.setText(QCoreApplication.translate("Form", u"1", None))
    # retranslateUi

