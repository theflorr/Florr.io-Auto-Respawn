print("[*] LOGS WILL BE DISPLAYED HERE [*]"); print()

import sys, os, json, threading, time, requests
import cv2 as c, numpy as n, pyautogui as p
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QGridLayout
from PyQt6.QtGui import QFont, QPainter, QBrush, QColor, QRegion, QBitmap
from PyQt6.QtCore import Qt, QRect, QEvent

class AutoClickerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = None
        self.initUI()
        self.load_settings()
        self.running = False

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(100, 100, 320, 275)
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #E0E0E0;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #39FF14;
            }
            QPushButton {
                background-color: #1F1F1F;
                border: 2px solid #39FF14;
                border-radius: 8px;
                padding: 6px 12px;
                color: #E0E0E0;
            }
            QPushButton:hover {
                border-color: #FF073A;
            }
            QPushButton:pressed {
                background-color: #2C2C2C;
            }
            QLineEdit {
                background-color: #1F1F1F;
                border: 1px solid #39FF14;
                border-radius: 5px;
                padding: 4px;
                color: #E0E0E0;
            }
        """)
        self.set_rounded_corners()

        self.gui_title = QLabel(" Auto Respawn by Crysiox", self)
        self.gui_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.gui_title.move(15, 15)
        self.gui_title.installEventFilter(self)

        self.close_btn = QPushButton("X", self)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF073A;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF4D4D;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.resize(30, 30)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 45, 15, 15)

        self.status_label = QLabel("Status: Stopped")
        self.status_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignTop)

        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_clicker)
        layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_clicker)
        layout.addWidget(self.stop_btn)

        grid = QGridLayout()
        grid.addWidget(QLabel("Red X X:"), 0, 0)
        self.redx_x = QLineEdit()
        grid.addWidget(self.redx_x, 0, 1)
        grid.addWidget(QLabel("Red X Y:"), 0, 2)
        self.redx_y = QLineEdit()
        grid.addWidget(self.redx_y, 0, 3)
        grid.addWidget(QLabel("Ready X:"), 1, 0)
        self.ready_x = QLineEdit()
        grid.addWidget(self.ready_x, 1, 1)
        grid.addWidget(QLabel("Ready Y:"), 1, 2)
        self.ready_y = QLineEdit()
        grid.addWidget(self.ready_y, 1, 3)
        layout.addLayout(grid)

        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def eventFilter(self, obj, event):
        if obj == self.gui_title:
            if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
                return True
            elif event.type() == QEvent.Type.MouseMove and event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
                self.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()
                return True
        return super().eventFilter(obj, event)

    def resizeEvent(self, e):
        margin = 10
        bw = self.close_btn.width()
        self.close_btn.move(self.width() - bw - margin, margin)
        self.gui_title.adjustSize()
        self.gui_title.move(margin, margin)
        super().resizeEvent(e)

    def set_rounded_corners(self):
        mask = QBitmap(self.size())
        mask.fill(Qt.GlobalColor.color0)
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(Qt.GlobalColor.color1)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)
        painter.end()
        self.setMask(QRegion(mask))

    def load_settings(self):
        sf = 'settings.json'
        if os.path.exists(sf):
            with open(sf, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = {"redx_button": {"X": 473, "Y": 186},
                             "ready_button": {"X": 1058, "Y": 613}}
            with open(sf, 'w') as f:
                json.dump(self.settings, f)
        self.redx_x.setText(str(self.settings['redx_button']['X']))
        self.redx_y.setText(str(self.settings['redx_button']['Y']))
        self.ready_x.setText(str(self.settings['ready_button']['X']))
        self.ready_y.setText(str(self.settings['ready_button']['Y']))

    def save_settings(self):
        self.settings['redx_button']['X'] = int(self.redx_x.text())
        self.settings['redx_button']['Y'] = int(self.redx_y.text())
        self.settings['ready_button']['X'] = int(self.ready_x.text())
        self.settings['ready_button']['Y'] = int(self.ready_y.text())
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)
        self.status_label.setText("Settings Saved")

    def start_clicker(self):
        if not self.running:
            self.running = True
            self.status_label.setText("Status: Running")
            threading.Thread(target=self.auto_clicker, daemon=True).start()

    def stop_clicker(self):
        self.running = False
        self.status_label.setText("Status: Stopped")

    def auto_clicker(self):
        redx = c.imread("assets/redx.png", 0)
        ready = c.imread("assets/ready.png", 0)
        while self.running:
            ss = n.array(p.screenshot().convert('L'), dtype=n.uint8)
            if c.minMaxLoc(c.matchTemplate(ss, redx, c.TM_CCOEFF_NORMED))[1] >= 0.8:
                p.click(self.settings["redx_button"]["X"], self.settings["redx_button"]["Y"])
            if c.minMaxLoc(c.matchTemplate(ss, ready, c.TM_CCOEFF_NORMED))[1] >= 0.8:
                p.click(self.settings["ready_button"]["X"], self.settings["ready_button"]["Y"])
            time.sleep(0.5)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = AutoClickerGUI()
    w.show()
    sys.exit(app.exec())
