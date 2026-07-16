import threading
from typing import Callable, Dict, Optional
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QKeySequence, QShortcut

class ShortcutHandler(QObject):
    """快捷键绑定与调度器，支持界面内 QShortcut 响应以及跨窗口安全调用"""
    triggered_capture = Signal()
    triggered_stop_tts = Signal()
    triggered_toggle_monitor = Signal()

    def __init__(self, parent_window=None):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.shortcuts: Dict[str, QShortcut] = {}

    def setup_shortcuts(self, capture_key: str = "Ctrl+Alt+S", stop_key: str = "Ctrl+Alt+Q", monitor_key: str = "Ctrl+Alt+M"):
        """绑定快捷键到主窗口及所有继承此处理器的视图"""
        if not self.parent_window:
            return

        self.clear_shortcuts()
        try:
            if capture_key:
                s1 = QShortcut(QKeySequence(capture_key), self.parent_window)
                s1.activated.connect(self.triggered_capture.emit)
                self.shortcuts["capture"] = s1

            if stop_key:
                s2 = QShortcut(QKeySequence(stop_key), self.parent_window)
                s2.activated.connect(self.triggered_stop_tts.emit)
                self.shortcuts["stop"] = s2

            if monitor_key:
                s3 = QShortcut(QKeySequence(monitor_key), self.parent_window)
                s3.activated.connect(self.triggered_toggle_monitor.emit)
                self.shortcuts["monitor"] = s3
        except Exception as e:
            print(f"[ShortcutHandler] 绑定窗口快捷键发生异常: {e}")

    def clear_shortcuts(self):
        for k, sc in self.shortcuts.items():
            try:
                sc.deleteLater()
            except Exception:
                pass
        self.shortcuts.clear()
