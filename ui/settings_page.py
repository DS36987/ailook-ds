from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QSlider, QTabWidget,
    QFormLayout, QGroupBox, QCheckBox, QMessageBox, QScrollArea, QFrame
)
from core.config_manager import ConfigManager
from core.tts_engine import TTSEngine

class SettingsPage(QWidget):
    """【独立设置页】管理 AI 视觉接口、TTS 语音引擎、自定义提示词库与实时截屏参数"""
    detach_requested = Signal()
    attach_requested = Signal()
    settings_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("WindowPage")
        self.cfg = ConfigManager()
        self.tts = TTSEngine()
        self.is_detached = False

        self._init_ui()
        self.load_from_config()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # 顶部操作栏
        top_bar = QHBoxLayout()
        title_lbl = QLabel("⚙️ 系统与 AI 视觉处理参数设置 (Settings)")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #60CDFF;")
        self.btn_detach = QPushButton("↗ 剥离为独立窗口")
        self.btn_detach.setMinimumHeight(32)
        self.btn_detach.clicked.connect(self._on_detach_toggle)

        self.btn_save_all = QPushButton("💾 保存并立即生效")
        self.btn_save_all.setProperty("class", "AccentButton")
        self.btn_save_all.setMinimumHeight(32)
        self.btn_save_all.clicked.connect(self.save_all_settings)

        top_bar.addWidget(title_lbl)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_detach)
        top_bar.addWidget(self.btn_save_all)
        layout.addLayout(top_bar)

        # 选项卡控件 (AI设置 / TTS设置 / 提示词自定义 / 截屏与热键)
        self.tabs = QTabWidget()

        self.tabs.addTab(self._create_ai_tab(), "🤖 AI 视觉大模型配置")
        self.tabs.addTab(self._create_tts_tab(), "🗣️ TTS 语音合成接入")
        self.tabs.addTab(self._create_prompts_tab(), "✏️ 自定义提示词与场景")
        self.tabs.addTab(self._create_capture_tab(), "🖥️ 截屏参数与快捷键")

        layout.addWidget(self.tabs, 1)

    def _create_ai_tab(self) -> QWidget:
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        # 1. 运行模式切换
        mode_group = QGroupBox("运行与推理接口模式选择")
        mode_layout = QHBoxLayout(mode_group)
        mode_layout.addWidget(QLabel("选择 AI 接入源:"))
        self.combo_ai_mode = QComboBox()
        self.combo_ai_mode.addItems(["云端大模型 API (Cloud API)", "本地 AI 部署 (Local Ollama / LocalAI)"])
        mode_layout.addWidget(self.combo_ai_mode, 1)
        layout.addWidget(mode_group)

        # 2. 云端 API 设置
        self.group_cloud = QGroupBox("☁️ 云端视觉 API 参数 (支持 OpenAI/阿里云/智谱/Claude等通用协议)")
        cloud_layout = QFormLayout(self.group_cloud)
        cloud_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)

        self.combo_cloud_provider = QComboBox()
        self.combo_cloud_provider.addItems(["openai", "aliyun", "zhipu", "anthropic", "custom"])
        self.input_cloud_url = QLineEdit()
        self.input_cloud_url.setPlaceholderText("例如: https://api.openai.com/v1 或 https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.input_cloud_key = QLineEdit()
        self.input_cloud_key.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.input_cloud_key.setPlaceholderText("在此处粘贴 API Key (Bearer Token)")
        self.input_cloud_model = QLineEdit("gpt-4o-mini")
        self.input_cloud_model.setPlaceholderText("例如: gpt-4o-mini, qwen-vl-max, glm-4v, claude-3-5-sonnet")

        cloud_layout.addRow("云端服务平台:", self.combo_cloud_provider)
        cloud_layout.addRow("接口 Base URL:", self.input_cloud_url)
        cloud_layout.addRow("API Key (密钥):", self.input_cloud_key)
        cloud_layout.addRow("视觉模型名称:", self.input_cloud_model)
        layout.addWidget(self.group_cloud)

        # 3. 本地 AI 设置
        self.group_local = QGroupBox("🏠 本地 AI 部署设置 (本地无 Key 隐私运行，支持 Ollama LLm/LLaVA/Qwen2-VL)")
        local_layout = QFormLayout(self.group_local)
        self.combo_local_provider = QComboBox()
        self.combo_local_provider.addItems(["ollama", "localai", "custom_http"])
        self.input_local_url = QLineEdit("http://localhost:11434/v1")
        self.input_local_url.setPlaceholderText("Ollama 默认地址: http://localhost:11434/v1 或 /api/generate")
        self.input_local_model = QLineEdit("llava:13b")
        self.input_local_model.setPlaceholderText("例如: llava:13b, qwen2-vl:7b, bakllava")

        local_layout.addRow("本地推理引擎:", self.combo_local_provider)
        local_layout.addRow("本地服务端网址:", self.input_local_url)
        local_layout.addRow("本地视觉模型名:", self.input_local_model)
        layout.addWidget(self.group_local)

        # 4. 通用生成参数
        common_group = QGroupBox("⚙️ 模型推理通用参数")
        common_layout = QFormLayout(common_group)
        self.spin_temp = QDoubleSpinBox()
        self.spin_temp.setRange(0.0, 2.0)
        self.spin_temp.setSingleStep(0.1)
        self.spin_temp.setValue(0.5)

        self.spin_tokens = QSpinBox()
        self.spin_tokens.setRange(100, 4096)
        self.spin_tokens.setValue(800)

        common_layout.addRow("Temperature (创造度):", self.spin_temp)
        common_layout.addRow("Max Tokens (最大回答字数):", self.spin_tokens)
        layout.addWidget(common_group)
        layout.addStretch()

        self.combo_ai_mode.currentIndexChanged.connect(self._on_ai_mode_changed)
        return scroll

    def _create_tts_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        # 开关
        self.chk_tts_enable = QCheckBox("✔ 启用 TTS 语音合成回放 (当识别完成后自动发音播报)")
        self.chk_tts_enable.setChecked(True)
        layout.addWidget(self.chk_tts_enable)

        # 模式与提供者
        mode_group = QGroupBox("语音合成引擎选择")
        mode_layout = QFormLayout(mode_group)
        self.combo_tts_provider = QComboBox()
        self.combo_tts_provider.addItems([
            "edge-tts (微软云端自然人声 - 免费且高音质，强烈推荐)",
            "pyttsx3 (Windows 本地离线语音 - SAPI5 零延时离线发声)",
            "openai-tts (OpenAI 官方高质量语音)",
            "custom-http (第三方或本地自建 HTTP 接口)"
        ])
        mode_layout.addRow("语音驱动接入:", self.combo_tts_provider)
        layout.addWidget(mode_group)

        # 参数配置卡片
        params_group = QGroupBox("🔊 发音音色与播放调整")
        params_layout = QFormLayout(params_group)

        self.combo_edge_voice = QComboBox()
        self.combo_edge_voice.addItems([
            "zh-CN-XiaoxiaoNeural (中文 - 晓晓 / 亲切自然女声)",
            "zh-CN-YunxiNeural (中文 - 云希 / 沉稳活力男声)",
            "zh-CN-YunjianNeural (中文 - 云健 / 纪录片播音腔男声)",
            "zh-CN-XiaoyiNeural (中文 - 晓伊 / 活泼年轻女声)",
            "zh-TW-HsiaoChenNeural (台湾 - 晓臻 / 柔和自然)",
            "en-US-JennyNeural (英文 - Jenny / 标准美国女声)",
            "en-US-GuyNeural (英文 - Guy / 标准美国男声)",
            "ja-JP-NanamiNeural (日文 - Nanami)"
        ])

        self.slider_rate = QSlider(Qt.Horizontal)
        self.slider_rate.setRange(-50, 50)
        self.slider_rate.setValue(0)
        self.lbl_rate_val = QLabel("0% (标准语速)")
        self.slider_rate.valueChanged.connect(lambda v: self.lbl_rate_val.setText(f"{'+' if v>0 else ''}{v}%"))

        self.slider_volume = QSlider(Qt.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(100)
        self.lbl_vol_val = QLabel("100%")
        self.slider_volume.valueChanged.connect(lambda v: self.lbl_vol_val.setText(f"{v}%"))

        self.input_custom_tts_url = QLineEdit()
        self.input_custom_tts_url.setPlaceholderText("仅 custom-http 模式填写，如 http://localhost:9880/tts")

        params_layout.addRow("Edge-TTS 音色选择:", self.combo_edge_voice)
        params_layout.addRow("语速调整 (-50% ~ +50%):", QHBoxLayout())
        params_layout.itemAt(1, QFormLayout.FieldRole).layout().addWidget(self.slider_rate)
        params_layout.itemAt(1, QFormLayout.FieldRole).layout().addWidget(self.lbl_rate_val)

        params_layout.addRow("音量大小 (0 ~ 100):", QHBoxLayout())
        params_layout.itemAt(2, QFormLayout.FieldRole).layout().addWidget(self.slider_volume)
        params_layout.itemAt(2, QFormLayout.FieldRole).layout().addWidget(self.lbl_vol_val)

        params_layout.addRow("自定义 TTS 网址:", self.input_custom_tts_url)
        layout.addWidget(params_group)

        # 试听测试按钮
        test_bar = QHBoxLayout()
        self.input_test_tts = QLineEdit("你好，这里是 AI Look Windows 11 桌面智能视觉读屏辅助系统。")
        self.btn_test_tts = QPushButton("🔈 立即试听此语音")
        self.btn_test_tts.clicked.connect(self._test_tts_playback)
        test_bar.addWidget(self.input_test_tts, 1)
        test_bar.addWidget(self.btn_test_tts)
        layout.addLayout(test_bar)
        layout.addStretch()

        return widget

    def _create_prompts_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        # 预设模板卡片
        preset_group = QGroupBox("📂 快速加载场景预设提示词库")
        preset_layout = QHBoxLayout(preset_group)
        self.combo_presets = QComboBox()
        self.btn_load_preset = QPushButton("🚀 填入上方预设")
        self.btn_load_preset.clicked.connect(self._load_selected_preset)
        preset_layout.addWidget(QLabel("内置场景:"))
        preset_layout.addWidget(self.combo_presets, 1)
        preset_layout.addWidget(self.btn_load_preset)
        layout.addWidget(preset_group)

        # 系统提示词
        sys_group = QGroupBox("🛡️ 系统提示词 (System Prompt - 定义 AI 角色立场与输出约束)")
        sys_layout = QVBoxLayout(sys_group)
        self.txt_sys_prompt = QTextEdit()
        self.txt_sys_prompt.setMinimumHeight(120)
        sys_layout.addWidget(self.txt_sys_prompt)
        layout.addWidget(sys_group)

        # 用户提示词
        user_group = QGroupBox("💬 默认每次截屏带入的用户提示词 (User Prompt)")
        user_layout = QVBoxLayout(user_group)
        self.txt_user_prompt = QTextEdit()
        self.txt_user_prompt.setMinimumHeight(80)
        user_layout.addWidget(self.txt_user_prompt)
        layout.addWidget(user_group)

        return widget

    def _create_capture_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        cap_group = QGroupBox("🖥️ 屏幕捕捉与多显示器参数")
        cap_layout = QFormLayout(cap_group)

        self.combo_cap_mode = QComboBox()
        self.combo_cap_mode.addItems(["fullscreen (捕获指定显示器全屏)", "region (选定固定区域 [left, top, width, height])"])
        self.spin_monitor = QSpinBox()
        self.spin_monitor.setRange(0, 8)
        self.spin_monitor.setValue(1)
        self.spin_monitor.setToolTip("0 为所有物理显示器合并，1 为 Windows 主屏幕，2... 为附加屏幕")

        self.input_region = QLineEdit("0, 0, 1920, 1080")
        self.input_region.setPlaceholderText("用逗号分隔 left, top, width, height")

        self.spin_interval = QDoubleSpinBox()
        self.spin_interval.setRange(1.0, 120.0)
        self.spin_interval.setSingleStep(0.5)
        self.spin_interval.setValue(6.0)

        self.spin_max_width = QSpinBox()
        self.spin_max_width.setRange(320, 3840)
        self.spin_max_width.setValue(1280)
        self.spin_max_width.setToolTip("过大图片会极大地增加 AI Token 消耗与网络推理耗时，建议 1280 ~ 1600")

        self.spin_quality = QSpinBox()
        self.spin_quality.setRange(30, 100)
        self.spin_quality.setValue(80)

        cap_layout.addRow("抓屏模式:", self.combo_cap_mode)
        cap_layout.addRow("物理显示器索引:", self.spin_monitor)
        cap_layout.addRow("自定义区域坐标:", self.input_region)
        cap_layout.addRow("自动实时定频间隔 (秒):", self.spin_interval)
        cap_layout.addRow("图片压缩最大宽度 (px):", self.spin_max_width)
        cap_layout.addRow("JPEG 保存压缩质量:", self.spin_quality)
        layout.addWidget(cap_group)

        # 快捷键设置
        key_group = QGroupBox("⌨️ Windows 11 全局快捷键热键配置")
        key_layout = QFormLayout(key_group)
        self.input_hotkey_cap = QLineEdit("Ctrl+Alt+S")
        self.input_hotkey_stop = QLineEdit("Ctrl+Alt+Q")
        self.input_hotkey_mon = QLineEdit("Ctrl+Alt+M")
        key_layout.addRow("触发单次截图识别:", self.input_hotkey_cap)
        key_layout.addRow("立即停止当前 TTS 朗读:", self.input_hotkey_stop)
        key_layout.addRow("切换定频自动监测:", self.input_hotkey_mon)
        layout.addWidget(key_group)
        layout.addStretch()

        return widget

    def load_from_config(self):
        """从 ConfigManager 加载数据渲染到界面"""
        cfg = self.cfg.get_all()

        # AI
        vision = cfg.get("vision_ai", {})
        if vision.get("mode", "cloud") == "cloud":
            self.combo_ai_mode.setCurrentIndex(0)
        else:
            self.combo_ai_mode.setCurrentIndex(1)
        self._on_ai_mode_changed(self.combo_ai_mode.currentIndex())

        cloud_prov = vision.get("cloud_provider", "openai")
        for i in range(self.combo_cloud_provider.count()):
            if self.combo_cloud_provider.itemText(i).lower() == cloud_prov.lower():
                self.combo_cloud_provider.setCurrentIndex(i)
                break
        self.input_cloud_url.setText(vision.get("base_url", "https://api.openai.com/v1"))
        self.input_cloud_key.setText(vision.get("api_key", ""))
        self.input_cloud_model.setText(vision.get("model", "gpt-4o-mini"))

        local_prov = vision.get("local_provider", "ollama")
        for i in range(self.combo_local_provider.count()):
            if self.combo_local_provider.itemText(i).lower() == local_prov.lower():
                self.combo_local_provider.setCurrentIndex(i)
                break
        self.input_local_url.setText(vision.get("local_base_url", "http://localhost:11434/v1"))
        self.input_local_model.setText(vision.get("local_model", "llava:13b"))

        self.spin_temp.setValue(float(vision.get("temperature", 0.5)))
        self.spin_tokens.setValue(int(vision.get("max_tokens", 800)))

        # TTS
        tts = cfg.get("tts", {})
        self.chk_tts_enable.setChecked(tts.get("enabled", True))
        prov = tts.get("provider", "edge-tts")
        if prov == "edge-tts":
            self.combo_tts_provider.setCurrentIndex(0)
        elif prov == "pyttsx3":
            self.combo_tts_provider.setCurrentIndex(1)
        elif prov == "openai-tts":
            self.combo_tts_provider.setCurrentIndex(2)
        else:
            self.combo_tts_provider.setCurrentIndex(3)

        voice = tts.get("voice", "zh-CN-XiaoxiaoNeural")
        for i in range(self.combo_edge_voice.count()):
            if voice in self.combo_edge_voice.itemText(i):
                self.combo_edge_voice.setCurrentIndex(i)
                break
        rate_val = tts.get("rate", 0)
        try:
            self.slider_rate.setValue(int(rate_val))
        except Exception:
            self.slider_rate.setValue(0)
        self.slider_volume.setValue(int(tts.get("volume", 100)))
        self.input_custom_tts_url.setText(tts.get("custom_tts_url", "http://localhost:9880/tts"))

        # Prompts
        prompts = cfg.get("prompts", {})
        self.txt_sys_prompt.setPlainText(prompts.get("system_prompt", ""))
        self.txt_user_prompt.setPlainText(prompts.get("user_prompt", ""))
        self.combo_presets.clear()
        templates = prompts.get("templates", [])
        for t in templates:
            self.combo_presets.addItem(t.get("name", "未命名场景"), t)

        # Capture
        capture = cfg.get("capture", {})
        if capture.get("mode", "fullscreen") == "fullscreen":
            self.combo_cap_mode.setCurrentIndex(0)
        else:
            self.combo_cap_mode.setCurrentIndex(1)
        self.spin_monitor.setValue(int(capture.get("monitor_index", 1)))
        reg = capture.get("region", [0, 0, 1920, 1080])
        if isinstance(reg, list) and len(reg) == 4:
            self.input_region.setText(f"{reg[0]}, {reg[1]}, {reg[2]}, {reg[3]}")
        self.spin_interval.setValue(float(capture.get("interval_seconds", 6.0)))
        self.spin_max_width.setValue(int(capture.get("max_width", 1280)))
        self.spin_quality.setValue(int(capture.get("image_quality", 80)))

        # Shortcuts
        shortcuts = cfg.get("shortcuts", {})
        self.input_hotkey_cap.setText(shortcuts.get("capture_trigger", "Ctrl+Alt+S"))
        self.input_hotkey_stop.setText(shortcuts.get("stop_tts", "Ctrl+Alt+Q"))
        self.input_hotkey_mon.setText(shortcuts.get("toggle_monitor", "Ctrl+Alt+M"))

    @Slot()
    def save_all_settings(self):
        """保存所改动参数到磁盘 ConfigManager"""
        # AI
        mode = "cloud" if self.combo_ai_mode.currentIndex() == 0 else "local"
        self.cfg.set_section("vision_ai", {
            "mode": mode,
            "cloud_provider": self.combo_cloud_provider.currentText(),
            "base_url": self.input_cloud_url.text().strip(),
            "api_key": self.input_cloud_key.text().strip(),
            "model": self.input_cloud_model.text().strip(),
            "local_provider": self.combo_local_provider.currentText(),
            "local_base_url": self.input_local_url.text().strip(),
            "local_model": self.input_local_model.text().strip(),
            "temperature": self.spin_temp.value(),
            "max_tokens": self.spin_tokens.value()
        })

        # TTS
        prov_idx = self.combo_tts_provider.currentIndex()
        if prov_idx == 0:
            prov = "edge-tts"
        elif prov_idx == 1:
            prov = "pyttsx3"
        elif prov_idx == 2:
            prov = "openai-tts"
        else:
            prov = "custom-http"
        
        raw_voice = self.combo_edge_voice.currentText()
        voice_clean = raw_voice.split(" ")[0] if " " in raw_voice else raw_voice

        self.cfg.set_section("tts", {
            "enabled": self.chk_tts_enable.isChecked(),
            "provider": prov,
            "voice": voice_clean,
            "rate": self.slider_rate.value(),
            "volume": self.slider_volume.value(),
            "custom_tts_url": self.input_custom_tts_url.text().strip()
        })

        # Prompts
        self.cfg.set("prompts", "system_prompt", self.txt_sys_prompt.toPlainText().strip())
        self.cfg.set("prompts", "user_prompt", self.txt_user_prompt.toPlainText().strip())

        # Capture
        cap_mode = "fullscreen" if self.combo_cap_mode.currentIndex() == 0 else "region"
        reg_parts = [int(p.strip()) for p in self.input_region.text().split(",") if p.strip().lstrip("-").isdigit()]
        if len(reg_parts) != 4:
            reg_parts = [0, 0, 1920, 1080]

        self.cfg.set_section("capture", {
            "mode": cap_mode,
            "monitor_index": self.spin_monitor.value(),
            "region": reg_parts,
            "interval_seconds": self.spin_interval.value(),
            "max_width": self.spin_max_width.value(),
            "image_quality": self.spin_quality.value()
        })

        # Shortcuts
        self.cfg.set_section("shortcuts", {
            "enable": True,
            "capture_trigger": self.input_hotkey_cap.text().strip(),
            "stop_tts": self.input_hotkey_stop.text().strip(),
            "toggle_monitor": self.input_hotkey_mon.text().strip()
        })

        self.settings_changed.emit()
        try:
            QMessageBox.information(self, "保存成功", "✅ 所有参数和配置已经持久化并立即在全系统生效！")
        except Exception:
            pass

    @Slot(int)
    def _on_ai_mode_changed(self, idx: int):
        if idx == 0:
            self.group_cloud.setVisible(True)
            self.group_local.setVisible(False)
        else:
            self.group_cloud.setVisible(False)
            self.group_local.setVisible(True)

    @Slot()
    def _load_selected_preset(self):
        item_data = self.combo_presets.currentData()
        if isinstance(item_data, dict):
            if "system_prompt" in item_data:
                self.txt_sys_prompt.setPlainText(item_data["system_prompt"])
            if "user_prompt" in item_data:
                self.txt_user_prompt.setPlainText(item_data["user_prompt"])

    @Slot()
    def _test_tts_playback(self):
        text = self.input_test_tts.text().strip()
        if not text:
            return
        prov_idx = self.combo_tts_provider.currentIndex()
        prov = ["edge-tts", "pyttsx3", "openai-tts", "custom-http"][prov_idx]
        raw_voice = self.combo_edge_voice.currentText().split(" ")[0]
        cfg = {
            "enabled": True,
            "provider": prov,
            "voice": raw_voice,
            "rate": self.slider_rate.value(),
            "volume": self.slider_volume.value(),
            "custom_tts_url": self.input_custom_tts_url.text().strip()
        }
        self.btn_test_tts.setText("🔊 合成并朗读中...")
        self.btn_test_tts.setEnabled(False)
        try:
            ok, msg = self.tts.speak(text, cfg)
            if ok:
                self.btn_test_tts.setText("🔈 试听完成")
            else:
                self.btn_test_tts.setText(f"发生错误: {msg[:15]}")
        finally:
            self.btn_test_tts.setEnabled(True)

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
