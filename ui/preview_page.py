import os
import io
import base64
from PIL import Image
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QPixmap, QImage, QFont, QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QFrame, QSplitter, QGroupBox, QApplication, QMainWindow
)
from core.config_manager import ConfigManager
from core.worker_thread import RecognitionWorker, AutoMonitorWorker
from core.tts_engine import TTSEngine

class PreviewPage(QWidget):
    """【独立预览页】负责展示实时屏幕截图画面、AI 实时分析输出与核心交互按钮"""
    detach_requested = Signal()
    attach_requested = Signal()
    floating_requested = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("WindowPage")
        self.cfg = ConfigManager()
        self.tts = TTSEngine()
        self.worker: Optional[RecognitionWorker] = None
        self.auto_worker: Optional[AutoMonitorWorker] = AutoMonitorWorker(self)
        self.is_detached = False

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # 顶部控制栏卡片
        toolbar_card = QFrame()
        toolbar_card.setProperty("class", "Card")
        toolbar_layout = QHBoxLayout(toolbar_card)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)

        self.btn_capture = QPushButton("🎯 立即抓屏识别 (Ctrl+Alt+S)")
        self.btn_capture.setProperty("class", "AccentButton")
        self.btn_capture.setMinimumHeight(34)

        self.btn_auto = QPushButton("⏳ 开启自动实时监测")
        self.btn_auto.setMinimumHeight(34)

        self.btn_stop_tts = QPushButton("🔇 停止朗读 (Ctrl+Alt+Q)")
        self.btn_stop_tts.setProperty("class", "DangerButton")
        self.btn_stop_tts.setMinimumHeight(34)

        self.btn_floating = QPushButton("🛸 悬浮极简条")
        self.btn_floating.setMinimumHeight(34)

        self.btn_detach = QPushButton("↗ 剥离为独立窗口")
        self.btn_detach.setMinimumHeight(34)

        toolbar_layout.addWidget(self.btn_capture)
        toolbar_layout.addWidget(self.btn_auto)
        toolbar_layout.addWidget(self.btn_stop_tts)
        toolbar_layout.addWidget(self.btn_floating)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_detach)

        main_layout.addWidget(toolbar_card)

        # 核心内容分割面板：左侧截图画面，右侧/下方识别结果
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：屏幕截图预览
        preview_group = QGroupBox("📺 实时屏幕捕获画面 (Live Preview)")
        preview_layout = QVBoxLayout(preview_group)
        self.lbl_preview = QLabel("等待执行屏幕捕捉...")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setMinimumSize(400, 300)
        self.lbl_preview.setStyleSheet("background-color: #161616; border: 1px dashed #3D3D3D; border-radius: 6px; color: #888888;")
        preview_layout.addWidget(self.lbl_preview)

        # 右侧：识别与解说输出
        result_group = QGroupBox("🤖 AI 实时视觉解说与文字分析 (Vision Result)")
        result_layout = QVBoxLayout(result_group)
        self.txt_result = QTextEdit()
        self.txt_result.setReadOnly(True)
        self.txt_result.setPlaceholderText("这里将实时流式展示大模型针对当前的屏幕截图产生的口语化读屏解说、排错建议与关键要点...")
        font = QFont("Microsoft YaHei UI", 11)
        self.txt_result.setFont(font)
        result_layout.addWidget(self.txt_result)

        # 结果操作小工具条
        res_tool_layout = QHBoxLayout()
        self.btn_copy = QPushButton("📋 复制分析内容")
        self.btn_replay_tts = QPushButton("🔊 重新播报此文本")
        self.lbl_status = QLabel("就绪 | 快捷键 Ctrl+Alt+S 触发")
        self.lbl_status.setStyleSheet("color: #888888;")

        res_tool_layout.addWidget(self.btn_copy)
        res_tool_layout.addWidget(self.btn_replay_tts)
        res_tool_layout.addStretch()
        res_tool_layout.addWidget(self.lbl_status)
        result_layout.addLayout(res_tool_layout)

        splitter.addWidget(preview_group)
        splitter.addWidget(result_group)
        splitter.setStretchFactor(0, 5)
        splitter.setStretchFactor(1, 4)

        main_layout.addWidget(splitter, 1)

    def _connect_signals(self):
        self.btn_capture.clicked.connect(self.trigger_single_capture)
        self.btn_auto.clicked.connect(self.toggle_auto_monitor)
        self.btn_stop_tts.clicked.connect(self.tts.stop)
        self.btn_floating.clicked.connect(lambda: self.floating_requested.emit(True))
        self.btn_detach.clicked.connect(self._on_detach_toggle)
        self.btn_copy.clicked.connect(self._copy_result_text)
        self.btn_replay_tts.clicked.connect(self._replay_result_tts)

        if self.auto_worker:
            self.auto_worker.trigger_task.connect(self.trigger_single_capture)
            self.auto_worker.status_changed.connect(self._on_auto_status_changed)

    @Slot()
    def trigger_single_capture(self, custom_prompt: str = ""):
        """启动单次后台工作线程捕获并识别"""
        if self.worker and self.worker.isRunning():
            self.lbl_status.setText("上一轮分析中，请稍候...")
            return

        self.lbl_status.setText("⚡ 正在截图并上传至 AI 视觉库...")
        self.btn_capture.setEnabled(False)

        self.worker = RecognitionWorker(self, custom_user_prompt=custom_prompt)
        self.worker.started_capture.connect(lambda: self.lbl_status.setText("📸 截图中..."))
        self.worker.capture_finished.connect(self._on_capture_finished)
        self.worker.started_ai.connect(lambda: self.lbl_status.setText("🧠 AI 正在实时视觉推理..."))
        self.worker.ai_finished.connect(self._on_ai_finished)
        self.worker.started_tts.connect(lambda txt: self.lbl_status.setText("🗣️ 正在语音解说..."))
        self.worker.tts_finished.connect(lambda ok, msg: self.lbl_status.setText(msg if not ok else "✅ 解说完成"))
        self.worker.worker_finished.connect(self._on_worker_finished)
        self.worker.start()

    @Slot(object, str)
    def _on_capture_finished(self, img_obj, b64_str):
        if img_obj and isinstance(img_obj, Image.Image):
            try:
                # 转成 QImage 并在 lbl_preview 中保持等比缩放缩略显示
                buffer = io.BytesIO()
                img_obj.save(buffer, format="JPEG", quality=85)
                qimg = QImage.fromData(buffer.getvalue())
                if not qimg.isNull():
                    pix = QPixmap.fromImage(qimg)
                    scaled_pix = pix.scaled(self.lbl_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.lbl_preview.setPixmap(scaled_pix)
            except Exception as e:
                print(f"[PreviewPage] 转换预览画面异常: {e}")

    @Slot(bool, str, dict)
    def _on_ai_finished(self, success, text, meta):
        if success:
            self.txt_result.setPlainText(text)
            self.lbl_status.setText(f"✅ AI 识别成功 | 耗时: {meta.get('elapsed_ms', 0)}ms | {meta.get('provider', '')}")
        else:
            self.txt_result.setPlainText(f"[视觉分析未完成或出错]\n{text}")
            self.lbl_status.setText("❌ 识别异常，请在设置中核查网络与 API 密钥。")

    @Slot()
    def _on_worker_finished(self):
        self.btn_capture.setEnabled(True)

    @Slot()
    def toggle_auto_monitor(self):
        if not self.auto_worker:
            return
        if self.auto_worker.is_running:
            self.auto_worker.stop_monitor()
        else:
            self.auto_worker.start_monitor()

    @Slot(bool, str)
    def _on_auto_status_changed(self, running, msg):
        if running:
            self.btn_auto.setText("⏹️ 停止自动实时监测")
            self.btn_auto.setProperty("class", "DangerButton")
            self.lbl_status.setText("⏳ 自动定频轮询已运行")
        else:
            self.btn_auto.setText("⏳ 开启自动实时监测")
            self.btn_auto.setProperty("class", "")
            self.lbl_status.setText("已停止定频轮询")
        self.btn_auto.style().unpolish(self.btn_auto)
        self.btn_auto.style().polish(self.btn_auto)

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

    @Slot()
    def _copy_result_text(self):
        text = self.txt_result.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(text)
                self.lbl_status.setText("📋 内容已复制到剪贴板")

    @Slot()
    def _replay_result_tts(self):
        text = self.txt_result.toPlainText()
        if text:
            tts_cfg = self.cfg.get_active_tts_config()
            self.lbl_status.setText("🗣️ 重新调用语音合成中...")
            ok, msg = self.tts.speak(text, tts_cfg)
            self.lbl_status.setText(msg)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 当窗口或分割条调整尺寸时重新调整图片的缩放
        if self.lbl_preview.pixmap() and not self.lbl_preview.pixmap().isNull():
            pass
