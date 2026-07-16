from PySide6.QtCore import Qt, Signal, Slot, QPoint
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QGraphicsDropShadowEffect

class FloatingWidget(QWidget):
    """【Windows 11 桌面悬浮极简窗】可自由拖动、实时展示读屏状态并触发抓屏操作"""
    capture_triggered = Signal()
    toggle_monitor_triggered = Signal()
    stop_tts_triggered = Signal()
    restore_main_triggered = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_pos = QPoint()
        self._init_ui()

    def _init_ui(self):
        # 窗口无边框、顶层悬浮、透明背景
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # 内部卡片容器 (承载阴影和圆角)
        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(36, 38, 44, 240);
                border: 1px solid rgba(96, 205, 255, 120);
                border-radius: 18px;
            }
            QPushButton {
                background-color: rgba(60, 64, 75, 180);
                border: 1px solid rgba(120, 125, 140, 100);
                border-radius: 12px;
                padding: 6px 12px;
                color: #FFFFFF;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(96, 205, 255, 200);
                color: #000000;
            }
        """)

        # 阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

        inner_layout = QHBoxLayout(self.container)
        inner_layout.setContentsMargins(16, 6, 16, 6)
        inner_layout.setSpacing(8)

        self.lbl_icon = QLabel("🛸 AI Look")
        self.lbl_icon.setStyleSheet("color: #60CDFF; font-weight: bold; font-size: 13px; border: none; background: transparent;")

        self.btn_cap = QPushButton("🎯 立即识别")
        self.btn_auto = QPushButton("⏳ 自动开启")
        self.btn_stop = QPushButton("🔇 停止朗读")
        self.btn_restore = QPushButton("📂 主面板")

        inner_layout.addWidget(self.lbl_icon)
        inner_layout.addWidget(self.btn_cap)
        inner_layout.addWidget(self.btn_auto)
        inner_layout.addWidget(self.btn_stop)
        inner_layout.addWidget(self.btn_restore)

        layout.addWidget(self.container)
        self.resize(460, 68)

        self.btn_cap.clicked.connect(self.capture_triggered.emit)
        self.btn_auto.clicked.connect(self.toggle_monitor_triggered.emit)
        self.btn_stop.clicked.connect(self.stop_tts_triggered.emit)
        self.btn_restore.clicked.connect(self.restore_main_triggered.emit)

    def set_monitor_status(self, running: bool):
        if running:
            self.btn_auto.setText("⏹️ 停止监测")
            self.btn_auto.setStyleSheet("background-color: rgba(220, 53, 69, 220); color: #FFF;")
        else:
            self.btn_auto.setText("⏳ 自动开启")
            self.btn_auto.setStyleSheet("")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()
