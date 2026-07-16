from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QSplitter,
    QGroupBox, QTabWidget, QApplication, QMessageBox
)
from core.log_manager import LogManager
from core.tts_engine import TTSEngine
from core.config_manager import ConfigManager

class LogsPage(QWidget):
    """【独立日志页】实时流式展示运行日志、耗时统计、大模型识别历史与错误追踪"""
    detach_requested = Signal()
    attach_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("WindowPage")
        self.logger = LogManager()
        self.tts = TTSEngine()
        self.cfg = ConfigManager()
        self.is_detached = False

        self._init_ui()
        self._register_listeners()
        self.refresh_logs_view()
        self.refresh_history_view()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # 顶部操作栏
        top_bar = QHBoxLayout()
        title_lbl = QLabel("📋 实时运行日志与 AI 视觉识别历史数据库 (Logs & History)")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #60CDFF;")
        self.btn_detach = QPushButton("↗ 剥离为独立窗口")
        self.btn_detach.setMinimumHeight(32)
        self.btn_detach.clicked.connect(self._on_detach_toggle)

        top_bar.addWidget(title_lbl)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_detach)
        layout.addLayout(top_bar)

        # 选项卡控件：流式日志监控 vs 视觉识别历史
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_live_log_tab(), "⚡ 实时运行与控制日志")
        self.tabs.addTab(self._create_history_tab(), "🖼️ 视觉识别历史归类与分析")

        layout.addWidget(self.tabs, 1)

    def _create_live_log_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # 过滤控制条
        filter_bar = QHBoxLayout()
        filter_bar.addWidget(QLabel("级别筛查:"))
        self.combo_level = QComboBox()
        self.combo_level.addItems(["ALL", "INFO", "SUCCESS", "WARN", "ERROR"])
        self.combo_level.currentIndexChanged.connect(self.refresh_logs_view)

        filter_bar.addWidget(self.combo_level)
        filter_bar.addWidget(QLabel("分类归档:"))
        self.combo_category = QComboBox()
        self.combo_category.addItems(["ALL", "SYSTEM", "AI", "TTS", "CAPTURE", "USER"])
        self.combo_category.currentIndexChanged.connect(self.refresh_logs_view)
        filter_bar.addWidget(self.combo_category)

        self.btn_clear_logs = QPushButton("🗑️ 清空日志视图")
        self.btn_clear_logs.setProperty("class", "DangerButton")
        self.btn_clear_logs.clicked.connect(self._on_clear_logs)

        filter_bar.addStretch()
        filter_bar.addWidget(self.btn_clear_logs)
        layout.addLayout(filter_bar)

        # 日志输出文本框
        self.txt_logs = QTextEdit()
        self.txt_logs.setReadOnly(True)
        self.txt_logs.setStyleSheet("background-color: #161616; color: #E0E0E0; font-family: 'Consolas', 'Courier New', monospace; font-size: 13px;")
        layout.addWidget(self.txt_logs, 1)

        return widget

    def _create_history_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        tool_bar = QHBoxLayout()
        self.btn_refresh_hist = QPushButton("🔄 刷新数据库")
        self.btn_refresh_hist.clicked.connect(self.refresh_history_view)
        self.btn_clear_hist = QPushButton("⚠️ 清空全部识别记录")
        self.btn_clear_hist.setProperty("class", "DangerButton")
        self.btn_clear_hist.clicked.connect(self._on_clear_history)
        tool_bar.addWidget(self.btn_refresh_hist)
        tool_bar.addStretch()
        tool_bar.addWidget(self.btn_clear_hist)
        layout.addLayout(tool_bar)

        # 左右分割面板：左侧列表，右侧详细内容与操作
        splitter = QSplitter(Qt.Horizontal)

        self.table_hist = QTableWidget(0, 4)
        self.table_hist.setHorizontalHeaderLabels(["时间戳", "模型/供应商", "耗时(ms)", "文字摘要"])
        self.table_hist.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_hist.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_hist.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_hist.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table_hist.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_hist.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_hist.itemSelectionChanged.connect(self._on_history_row_selected)
        splitter.addWidget(self.table_hist)

        # 右侧详情卡片
        detail_group = QGroupBox("🔍 单次视觉分析详细输出 (Detail View)")
        detail_layout = QVBoxLayout(detail_group)
        self.txt_detail = QTextEdit()
        self.txt_detail.setReadOnly(True)
        detail_layout.addWidget(self.txt_detail, 1)

        action_layout = QHBoxLayout()
        self.btn_copy_detail = QPushButton("📋 复制详情")
        self.btn_copy_detail.clicked.connect(self._copy_selected_detail)
        self.btn_speak_detail = QPushButton("🔊 朗读此结果")
        self.btn_speak_detail.clicked.connect(self._speak_selected_detail)
        action_layout.addWidget(self.btn_copy_detail)
        action_layout.addWidget(self.btn_speak_detail)
        action_layout.addStretch()
        detail_layout.addLayout(action_layout)

        splitter.addWidget(detail_group)
        splitter.setStretchFactor(0, 5)
        splitter.setStretchFactor(1, 4)

        layout.addWidget(splitter, 1)
        return widget

    def _register_listeners(self):
        self.logger.add_listener(self._on_new_log_entry)
        self.logger.add_history_listener(lambda item: self.refresh_history_view())

    @Slot(dict)
    def _on_new_log_entry(self, entry: dict):
        # 如果符合当前的过滤，实时流式追加到日志框
        level_f = self.combo_level.currentText() if hasattr(self, "combo_level") else "ALL"
        cat_f = self.combo_category.currentText() if hasattr(self, "combo_category") else "ALL"

        if level_f != "ALL" and entry.get("level") != level_f:
            return
        if cat_f != "ALL" and entry.get("category") != cat_f:
            return

        time_str = entry.get("timestamp", "")
        level_str = entry.get("level", "INFO")
        cat_str = entry.get("category", "SYSTEM")
        msg = entry.get("message", "")

        color = "#CCCCCC"
        if level_str == "ERROR":
            color = "#FF6B6B"
        elif level_str == "SUCCESS":
            color = "#51CF66"
        elif level_str == "WARN":
            color = "#FCC419"

        html_line = f"""<div><span style='color:#888;'>[{time_str}]</span> <span style='color:{color}; font-weight:bold;'>[{level_str}]</span> <span style='color:#60CDFF;'>[{cat_str}]</span> {msg}</div>"""
        self.txt_logs.append(html_line)

    @Slot()
    def refresh_logs_view(self):
        if not hasattr(self, "combo_level") or not hasattr(self, "combo_category"):
            return
        level_f = self.combo_level.currentText()
        cat_f = self.combo_category.currentText()
        logs = self.logger.get_logs(limit=400, level_filter=level_f, category_filter=cat_f)
        self.txt_logs.clear()
        for entry in logs:
            self._on_new_log_entry(entry)

    @Slot()
    def refresh_history_view(self):
        if not hasattr(self, "table_hist"):
            return
        self.table_hist.setRowCount(0)
        history = self.logger.get_history(limit=100)
        self.table_hist.setRowCount(len(history))
        for r, item in enumerate(history):
            self.table_hist.setItem(r, 0, QTableWidgetItem(str(item.get("timestamp", ""))))
            self.table_hist.setItem(r, 1, QTableWidgetItem(f"{item.get('provider', '')} ({item.get('model', '')})"))
            self.table_hist.setItem(r, 2, QTableWidgetItem(str(item.get("elapsed_ms", 0))))
            res_str = str(item.get("result", "")).replace("\n", " ")[:60]
            self.table_hist.setItem(r, 3, QTableWidgetItem(res_str))

            # 把整条原始数据存在首列用户数据中
            self.table_hist.item(r, 0).setData(Qt.UserRole, item)

    @Slot()
    def _on_history_row_selected(self):
        items = self.table_hist.selectedItems()
        if not items:
            return
        row = items[0].row()
        item_data = self.table_hist.item(row, 0).setData(Qt.UserRole, None)
        item_data = self.table_hist.item(row, 0).data(Qt.UserRole)
        if isinstance(item_data, dict):
            detail_text = f"【时间】 {item_data.get('timestamp')}\n" \
                          f"【AI 服务商】 {item_data.get('provider')} | 模型: {item_data.get('model')} | 耗时: {item_data.get('elapsed_ms')} ms\n" \
                          f"【提示词 prompt】\n{item_data.get('prompt')}\n" \
                          f"--------------------------------------------------\n" \
                          f"【视觉识别与解说输出】\n{item_data.get('result')}"
            self.txt_detail.setPlainText(detail_text)

    @Slot()
    def _copy_selected_detail(self):
        text = self.txt_detail.toPlainText()
        if text:
            cb = QApplication.clipboard()
            if cb:
                cb.setText(text)

    @Slot()
    def _speak_selected_detail(self):
        items = self.table_hist.selectedItems()
        if items:
            item_data = self.table_hist.item(items[0].row(), 0).data(Qt.UserRole)
            if isinstance(item_data, dict) and item_data.get("result"):
                tts_cfg = self.cfg.get_active_tts_config()
                self.tts.speak(item_data["result"], tts_cfg)

    @Slot()
    def _on_clear_logs(self):
        self.logger.clear_logs()
        self.txt_logs.clear()

    @Slot()
    def _on_clear_history(self):
        self.logger.clear_history()
        self.table_hist.setRowCount(0)
        self.txt_detail.clear()

    @Slot()
    def _on_detach_toggle(self):
        if not self.is_detached:
            self.detach_requested.emit()
        else:
            self.attach_requested.emit()

    def set_detached_state(self, detached: bool):
        self.is_detached = detached
        if detached:
            self.btn_detach.setText("↙ 归位至主界面")
        else:
            self.btn_detach.setText("↗ 剥离为独立窗口")
