import json
import os
import subprocess
import sys
import re
import string
import time

from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox, QPushButton, QSystemTrayIcon, QMenu
from ui_main import Ui_Form


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.row = 13
        self.column = 4
        self.ui.btn_folder.clicked.connect(self.open_folder_dialog)
        self.mode="view"
        self.disable_btn:list[QPushButton]=[]
        self.completed=[]
        for row_num in range(self.row):
            for column_num in range(self.column):
                btn = QPushButton(f"{string.ascii_uppercase[column_num]}{row_num + 1:02d}", self)
                btn.clicked.connect(lambda click,b=btn:self.btn_click(b))
                btn.setVisible(False)
                self.ui.grid_buttons.addWidget(btn, row_num, column_num)
        self.ui.progress_bar.setVisible(False)
        self.ui.progress_label.setVisible(False)
        self.ui.btn_load_config.clicked.connect(self.btn_select_config)
        self.ui.btn_reset_default.clicked.connect(self.btn_reset_default)
        self.ui.btn_switch_mode.clicked.connect(self.btn_switch_mode)
        self.ui.btn_save_config.clicked.connect(self.btn_save_config)
        self.check_progress()
        self.tray_icon = QSystemTrayIcon(self)
        self.create_tray_icon()

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()

    def create_tray_icon(self):
        self.tray_icon.setIcon(QIcon("任务进程.png"))
        tray_menu = QMenu(self)
        action_show = QAction("显示窗口", self)
        action_show.triggered.connect(self.show)
        action_exit = QAction("退出", self)
        action_exit.triggered.connect(app.quit)
        tray_menu.addAction(action_show)
        tray_menu.addAction(action_exit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def find_button(self,name):
        layout = self.ui.grid_buttons
        for index in range(layout.count()):
            item = layout.itemAt(index)
            if not item:
                continue
            btn = item.widget()
            if isinstance(btn, QPushButton):
                if btn.text()==name:
                    return btn
        return False

    def set_button_completed(self,name,color):
        btn=self.find_button(name)
        if btn and btn not in self.disable_btn:
            btn.setStyleSheet(f"QPushButton {{background-color:{color};}}")
            return True
        else:
            return False

    def check_progress(self):
        if self.mode=="view":
            n=0
            path=self.ui.label_path.text()
            now_completed=[]
            if os.path.isdir(path):
                for dir_ in os.listdir(path):
                    match = re.fullmatch(r"^[A-Z](\d{2})$", dir_)
                    if match:
                        if self.set_button_completed(dir_,"#2ECC71"):
                            now_completed.append(dir_)
                            n+=1
            if now_completed!=self.completed:
                for last in self.completed:
                    if last not in now_completed:
                        self.find_button(last).setStyleSheet("")
                self.completed=now_completed
            if n!=0:
                self.ui.progress_bar.setVisible(True)
                self.ui.progress_label.setVisible(True)
                self.ui.progress_bar.setValue(n/(self.row*self.column-len(self.disable_btn))*100)
            else:
                self.ui.progress_bar.setVisible(False)
                self.ui.progress_label.setVisible(False)
        QTimer.singleShot(100, self.check_progress)


    def set_visible(self,visible):
        layout = self.ui.grid_buttons
        for index in range(layout.count()):
            item = layout.itemAt(index)
            if not item:
                continue
            btn = item.widget()
            if isinstance(btn, QPushButton):
                btn.setVisible(visible)

    def btn_click(self,btn:QPushButton):
        if self.mode == "view":
            path=f"{self.ui.label_path.text()}/{btn.text()}".replace("/","\\")
            if os.path.isdir(path):
                subprocess.Popen(f'explorer /select,"{path}"')
        if self.mode == "edit":
            if btn in self.disable_btn:
                self.disable_btn.remove(btn)
                btn.setStyleSheet("")
            else:
                self.disable_btn.append(btn)
                btn.setStyleSheet("QPushButton {width: 181px;height: 19px;background-color: #CCCCCC;border: 1px solid #ADADAD;color: #787878;}QPushButton:hover {border: 1px solid #0078D7;}")

    def btn_save_config(self):
        save_path, _ = QFileDialog.getSaveFileName(self,"保存配置文件","","JSON 文件 (*.json)")
        if save_path:
            save_json={}
            btn_name=[]
            for btn in self.disable_btn:
                btn_name.append(btn.text())
            save_json["disable"]=btn_name
            with open(save_path,"w",encoding="utf-8") as f:
                f.write(json.dumps(save_json))
        else:
            QMessageBox.information(self, "信息", "你没有选择任何保存路径!")

    def btn_switch_mode(self):
        self.ui.progress_bar.setVisible(False)
        self.ui.progress_label.setVisible(False)
        for name in self.completed:
            self.find_button(name).setStyleSheet("")
        btn=self.ui.btn_switch_mode
        if self.mode == "view":
            btn.setText("查看模式")
            btn.setStyleSheet("QPushButton {background-color: #E74C3C;border: 1px solid #ADADAD;}QPushButton:hover {border: 1px solid #0078D7;}")
            self.mode = "edit"
            for disable_btn in self.disable_btn:
                disable_btn.setStyleSheet("QPushButton {width: 181px;height: 19px;background-color: #CCCCCC;border: 1px solid #ADADAD;color: #787878;}QPushButton:hover {border: 1px solid #0078D7;}")
                disable_btn.setEnabled(True)

        else:
            btn.setText("编辑模式")
            btn.setStyleSheet("QPushButton {background-color: #4CAF50;border: 1px solid #ADADAD;}QPushButton:hover {border: 1px solid #0078D7;}")
            self.mode = "view"
            for disable_btn in self.disable_btn:
                disable_btn.setEnabled(False)

    def btn_reset_default(self):
        for btn in self.disable_btn:
            btn.setStyleSheet("")
            btn.setEnabled(True)
        self.disable_btn.clear()

    def btn_select_config(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择配置文件", "", "配置文件 (*.json)")
        if file_path:
            if os.path.isfile(file_path):
                try:
                    with open(file_path,"r",encoding="utf-8") as json_file:
                        config = json.load(json_file)
                    self.btn_reset_default()
                    if "disable" in config:
                        layout = self.ui.grid_buttons
                        for name in config["disable"]:
                            for index in range(layout.count()):
                                item = layout.itemAt(index)
                                if not item:
                                    continue
                                btn = item.widget()
                                if isinstance(btn, QPushButton):
                                    if btn.text() == name:
                                        self.disable_btn.append(btn)
                                        btn.setEnabled(False)

                except json.JSONDecodeError:
                    QMessageBox.critical(self, "错误", "JSON文件格式错误!")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"加载失败：\n{str(e)}")
            else:
                QMessageBox.warning(self, "选择无效", "你选择的不是文件")
        else:
            QMessageBox.information(self, "信息", "你没有选择任何文件夹!")

    def open_folder_dialog(self):
        self.set_visible(False)
        self.ui.label_path.setText("暂未选择...")
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹路径")
        if folder_path:
            if os.path.isdir(folder_path):
                listdir = os.listdir(folder_path)
                if len(listdir) > self.row * self.column:
                    QMessageBox.critical(self, "选择无效", "文件夹文件过多")
                else:
                    for dir_ in listdir:
                        if not os.path.isdir(os.path.join(folder_path, dir_)):
                            QMessageBox.warning(self, "选择无效", f"存在非文件夹的文件{dir_}")
                            break
                        match = re.fullmatch(r"^[A-Z](\d{2})$", dir_)
                        if match:
                            num = int(match.group(1))
                            if num > self.row * self.column:
                                QMessageBox.warning(self, "选择无效", f"存在非法文件夹{dir_}")
                                break
                        else:
                            QMessageBox.warning(self, "选择无效", f"存在非法文件夹{dir_}")
                            break
                    else:
                        self.ui.label_path.setText(folder_path)
                        self.set_visible(True)
            else:
                QMessageBox.critical(self, "选择无效", "文件夹不存在!")
        else:
            QMessageBox.information(self, "信息", "你没有选择任何文件夹!")


time.sleep(5)
app = QApplication(sys.argv)
app.setWindowIcon(QIcon("任务进程.png"))

window = MainWindow()
window.show()
sys.exit(app.exec())

