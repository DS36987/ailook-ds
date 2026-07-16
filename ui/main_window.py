from typing import Optional, Dict
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QStackedWidget, QFrame, QGridLayout, QApplication, QSystemTrayIcon, QMenu
)
from core.config_manager import ConfigManager
from ui.preview_page import PreviewPage
from ui.settings_page import SettingsPage
from ui.logs_page import LogsPage
from ui.floating_widget import FloatingWidget
from utils.shortcut_handler import ShortcutHandler

class DetachedWindow(QMainWindow):
    """【独立分离原生窗口】用于承载从主框架剥离出来的单个功能视图，支持 Windows 11 自由拖转与多显示器排布"""
    closed_signal = Signal()

    def __init__(self, title: str, child_widget: QWidget, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(1000, 700)
        self.child_widget = child_widget
        self.setCentralWidget(self.child_widget)

    def closeEvent(self, event):
        self.closed_signal.emit()
        event.accept()


class MainWindow(QMainWindow):
    """【主控应用容器】集成侧边导航、多标签视图管理、悬浮窗控制及一键独立窗口剥离架构"""

    def __init__(self):
        super().__init__()
        self.cfg = ConfigManager()
        self.shortcuts = ShortcutHandler(self)
        self.floating_bar: Optional[FloatingWidget] = None
        self.detached_windows: Dict[str, DetachedWindow] = {}

        self.setWindowTitle("AI Look Desktop System - 智能视觉实时识别与语音读屏 (Windows 11 现代架构)")
        self.resize(1240, 800)
        self.setMinimumSize(900, 600)

        self._init_pages()
        self._init_ui()
        self._init_floating_bar()
        self._setup_shortcuts()
        self._init_tray()

    def _init_pages(self):
        # 实例化三个独立功能模块
        self.preview_page = PreviewPage(self)
        self.settings_page = SettingsPage(self)
        self.logs_page = LogsPage(self)

        # 挂载剥离请求信号
        self.preview_page.detach_requested.connect(lambda: self.detach_page("preview"))
        self.preview_page.attach_requested.connect(lambda: self.attach_page("preview"))
        self.preview_page.floating_requested.connect(self.show_floating_bar)

        self.settings_page.detach_requested.connect(lambda: self.detach_page("settings"))
        self.settings_page.attach_requested.connect(lambda: self.attach_page("settings"))
        self.settings_page.settings_changed.connect(self._on_settings_updated)

        self.logs_page.detach_requested.connect(lambda: self.detach_page("logs"))
        self.logs_page.attach_requested.connect(lambda: self.attach_page("logs"))

    def _init_ui(self):
        self.main_container = QWidget()
        self.main_container.setObjectName("MainContainer")
        self.setCentralWidget(self.main_container)

        main_layout = QHBoxLayout(self.main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 左侧边栏 (Sidebar)
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(12, 20, 12, 16)
        sidebar_layout.setSpacing(8)

        # 品牌头条
        logo_lbl = QLabel("🛸 AI Look DS")
        logo_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #60CDFF; padding-left: 6px;")
        sub_lbl = QLabel("Windows 11 AI 视觉平台")
        sub_lbl.setStyleSheet("font-size: 12px; color: #888888; padding-left: 6px; padding-bottom: 12px;")
        sidebar_layout.addWidget(logo_lbl)
        sidebar_layout.addWidget(sub_lbl)

        # 导航按键
        self.btn_nav_preview = QPushButton("🎯 实时预览面板")
        self.btn_nav_preview.setProperty("class", "NavButton")
        self.btn_nav_preview.setProperty("active", "true")

        self.btn_nav_settings = QPushButton("⚙️ 系统与 AI 设置")
        self.btn_nav_settings.setProperty("class", "NavButton")

        self.btn_nav_logs = QPushButton("📋 日志与历史记录")
        self.btn_nav_logs.setProperty("class", "NavButton")

        sidebar_layout.addWidget(self.btn_nav_preview)
        sidebar_layout.addWidget(self.btn_nav_settings)
        sidebar_layout.addWidget(self.btn_nav_logs)
        sidebar_layout.addStretch()

        # 分离/合并操作工具区
        self.btn_detach_all = QPushButton("✨ 全部分离为独立窗口")
        self.btn_detach_all.setToolTip("将预览页、设置页和日志页同时分离为各自独立的原生窗口，便于多屏并发与拖移")
        self.btn_attach_all = QPushButton("📦 全部合并至主界面")
        self.btn_attach_all.setVisible(False)

        sidebar_layout.addWidget(self.btn_detach_all)
        sidebar_layout.addWidget(self.btn_attach_all)

        # 右侧内容堆叠面板 (StackedWidget)
        self.stack = QStackedWidget()
        
        # 为了应对剥离后原来的 Stack 位置占位，我们为每一页设置或保留位置
        self.placeholder_preview = self._create_placeholder("预览页已分离为独立窗口运行中", lambda: self.attach_page("preview"))
        self.placeholder_settings = self._create_placeholder("系统设置页已分离为独立窗口运行中", lambda: self.attach_page("settings"))
        self.placeholder_logs = self._create_placeholder("日志与识别历史页已在独立窗口运行中", lambda: self.attach_page("logs"))

        self.stack.addWidget(self.preview_page)     # Index 0
        self.stack.addWidget(self.settings_page)    # Index 1
        self.stack.addWidget(self.logs_page)        # Index 2

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack, 1)

        # 绑定点击
        self.btn_nav_preview.clicked.connect(lambda: self.switch_nav(0))
        self.btn_nav_settings.clicked.connect(lambda: self.switch_nav(1))
        self.btn_nav_logs.clicked.connect(lambda: self.switch_nav(2))

        self.btn_detach_all.clicked.connect(self.detach_all_pages)
        self.btn_attach_all.clicked.connect(self.attach_all_pages)

    def _create_placeholder(self, text: str, attach_func) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignCenter)
        lbl = QLabel(f"↗ {text}")
        lbl.setStyleSheet("font-size: 16px; color: #60CDFF; font-weight: bold;")
        btn = QPushButton("↙ 将此视图归位至主界面")
        btn.setProperty("class", "AccentButton")
        btn.setFixedSize(220, 40)
        btn.clicked.connect(attach_func)
        lay.addWidget(lbl, 0, Qt.AlignCenter)
        lay.addSpacing(16)
        lay.addWidget(btn, 0, Qt.AlignCenter)
        return w

    def switch_nav(self, index: int):
        self.stack.setCurrentIndex(index)
        self.btn_nav_preview.setProperty("active", "true" if index == 0 else "false")
        self.btn_nav_settings.setProperty("active", "true" if index == 1 else "false")
        self.btn_nav_logs.setProperty("active", "true" if index == 2 else "false")
        for btn in [self.btn_nav_preview, self.btn_nav_settings, self.btn_nav_logs]:
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def detach_page(self, page_key: str):
        """将选定视图剥离为独立 Windows 11 原生圆角窗口"""
        if page_key in self.detached_windows:
            win = self.detached_windows[page_key]
            win.show()
            win.raise_()
            win.activateWindow()
            return

        if page_key == "preview":
            page = self.preview_page
            title = "AI Look - 实时预览面板 [独立窗口]"
            idx = 0
            placeholder = self.placeholder_preview
        elif page_key == "settings":
            page = self.settings_page
            title = "AI Look - 系统与 AI 引擎设置 [独立窗口]"
            idx = 1
            placeholder = self.placeholder_settings
        else:
            page = self.logs_page
            title = "AI Look - 日志与历史分析 [独立窗口]"
            idx = 2
            placeholder = self.placeholder_logs

        # 用占位符替换原来在 stack 里的位置
        self.stack.removeWidget(page)
        self.stack.insertWidget(idx, placeholder)
        self.stack.setCurrentIndex(idx)

        # 封装进原生窗口
        win = DetachedWindow(title, page, self)
        page.set_detached_state(True)
        self.detached_windows[page_key] = win

        def on_win_close():
            self.attach_page(page_key)

        win.closed_signal.connect(on_win_close)
        win.show()

        self._check_detach_all_status()

    def attach_page(self, page_key: str):
        """将从独立窗口中剥离出来的视图重新吸附并归位到主界面"""
        if page_key not in self.detached_windows:
            return

        win = self.detached_windows.pop(page_key)
        # 暂时断开 close 信号以防死循环
        try:
            win.closed_signal.disconnect()
        except Exception:
            pass

        if page_key == "preview":
            page = self.preview_page
            idx = 0
            placeholder = self.placeholder_preview
        elif page_key == "settings":
            page = self.settings_page
            idx = 1
            placeholder = self.placeholder_settings
        else:
            page = self.logs_page
            idx = 2
            placeholder = self.placeholder_logs

        win.setCentralWidget(QWidget())
        win.close()

        self.stack.removeWidget(placeholder)
        self.stack.insertWidget(idx, page)
        page.set_detached_state(False)
        self.switch_nav(idx)

        self._check_detach_all_status()

    def detach_all_pages(self):
        for k in ["preview", "settings", "logs"]:
            self.detach_page(k)

    def attach_all_pages(self):
        for k in list(self.detached_windows.keys()):
            self.attach_page(k)

    def _check_detach_all_status(self):
        if len(self.detached_windows) == 3:
            self.btn_detach_all.setVisible(False)
            self.btn_attach_all.setVisible(True)
        else:
            self.btn_detach_all.setVisible(True)
            self.btn_attach_all.setVisible(False)

    def _init_floating_bar(self):
        self.floating_bar = FloatingWidget(self)
        self.floating_bar.capture_triggered.connect(self.preview_page.trigger_single_capture)
        self.floating_bar.toggle_monitor_triggered.connect(self.preview_page.toggle_auto_monitor)
        self.floating_bar.stop_tts_triggered.connect(self.preview_page.tts.stop)
        self.floating_bar.restore_main_triggered.connect(self._restore_from_floating)

        # 同步自动监测状态改变
        if self.preview_page.auto_worker:
            self.preview_page.auto_worker.status_changed.connect(
                lambda running, msg: self.floating_bar.set_monitor_status(running) if self.floating_bar else None
            )

    @Slot(bool)
    def show_floating_bar(self, minimize_main: bool = True):
        if self.floating_bar:
            self.floating_bar.show()
            if minimize_main:
                self.hide()

    @Slot()
    def _restore_from_floating(self):
        if self.floating_bar:
            self.floating_bar.hide()
        self.showNormal()
        self.activateWindow()

    def _setup_shortcuts(self):
        cfg = self.cfg.get("shortcuts", {})
        if cfg.get("enable", True):
            self.shortcuts.setup_shortcuts(
                capture_key=cfg.get("capture_trigger", "Ctrl+Alt+S"),
                stop_key=cfg.get("stop_tts", "Ctrl+Alt+Q"),
                monitor_key=cfg.get("toggle_monitor", "Ctrl+Alt+M")
            )
            self.shortcuts.triggered_capture.connect(self.preview_page.trigger_single_capture)
            self.shortcuts.triggered_stop_tts.connect(self.preview_page.tts.stop)
            self.shortcuts.triggered_toggle_monitor.connect(self.preview_page.toggle_auto_monitor)

    @Slot()
    def _on_settings_updated(self):
        self._setup_shortcuts()

    def _init_tray(self):
        try:
            self.tray = QSystemTrayIcon(self)
            # 加载或创建图标
            pix = QPixmap(32, 32)
            pix.fill(Qt.transparent)
            from PySide6.QtGui import QPainter, QColor
            painter = QPainter(pix)
            painter.setBrush(QColor("#0078D4"))
            painter.drawEllipse(2, 2, 28, 28)
            painter.end()

            self.tray.setIcon(QIcon(pix))
            self.tray.setToolTip("AI Look Windows 11 视觉识别系统")

            menu = QMenu()
            act_show = menu.addAction("🎯 打开主操作面板")
            act_show.triggered.connect(self.showNormal)
            act_float = menu.addAction("🛸 打开悬浮极简条")
            act_float.triggered.connect(lambda: self.show_floating_bar(True))
            act_cap = menu.addAction("📸 立即截图读屏")
            act_cap.triggered.connect(self.preview_page.trigger_single_capture)
            menu.addSeparator()
            act_quit = menu.addAction("❌ 退出系统")
            act_quit.triggered.connect(QApplication.instance().quit)

            self.tray.setContextMenu(menu)
            self.tray.show()
        except Exception as e:
            print(f"[MainWindow] 初始化托盘图表异常: {e}")

    def closeEvent(self, event):
        # 退出前停掉轮询和播放器
        try:
            if self.preview_page.auto_worker:
                self.preview_page.auto_worker.stop_monitor()
            self.preview_page.tts.stop()
            for win in list(self.detached_windows.values()):
                win.close()
            if self.floating_bar:
                self.floating_bar.close()
        except Exception:
            pass
        event.accept()
