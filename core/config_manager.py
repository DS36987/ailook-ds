import json
import os
import threading
from typing import Dict, Any, List

class ConfigManager:
    _instance = None
    _lock = threading.RLock()

    DEFAULT_CONFIG = {
        "app": {
            "name": "AI Look Desktop System",
            "version": "1.0.0",
            "theme": "dark",  # dark or light
            "always_on_top": False,
            "min_to_tray": True
        },
        "vision_ai": {
            "mode": "cloud",  # "cloud" 或 "local"
            "cloud_provider": "openai",  # "openai", "aliyun", "zhipu", "anthropic", "custom"
            "api_key": "",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o-mini",
            "temperature": 0.5,
            "max_tokens": 800,
            "local_provider": "ollama",  # "ollama", "localai", "custom_http"
            "local_base_url": "http://localhost:11434/v1",
            "local_model": "llava:13b",
            "local_api_key": "ollama"
        },
        "tts": {
            "enabled": True,
            "mode": "cloud",  # "cloud" 或 "local"
            "provider": "edge-tts",  # "edge-tts", "openai-tts", "pyttsx3", "custom-http"
            "voice": "zh-CN-XiaoxiaoNeural",
            "rate": 0,  # edge-tts 语速百分比或 pyttsx3 WPM 偏移
            "volume": 100,  # 0-100
            "openai_tts_voice": "alloy",
            "openai_tts_model": "tts-1",
            "custom_tts_url": "http://localhost:9880/tts",
            "custom_tts_token": ""
        },
        "prompts": {
            "system_prompt": "你是一个专业的桌面实时智能视觉识别与读屏助手。请观察提供的屏幕截图，用自然、生动、口语化的中文简练描述当前屏幕所展示的核心要点、关键变化及软件状态。要求回答可以直接用于语音播报，禁止使用 Markdown 粗体、星号、列表符号等任何特殊格式符号。",
            "user_prompt": "请分析当前的屏幕截图，直接说出最重要的动态内容或关注重点。",
            "active_template": "默认视障读屏模式",
            "templates": [
                {
                    "name": "默认视障读屏模式",
                    "system_prompt": "你是一个专业的桌面实时智能视觉识别与读屏助手。请观察提供的屏幕截图，用自然、生动、口语化的中文简练描述当前屏幕所展示的核心要点、关键变化及软件状态。要求回答可以直接用于语音播报，禁止使用 Markdown 粗体、星号、列表符号等任何特殊格式符号。",
                    "user_prompt": "请分析当前的屏幕截图，直接说出最重要的动态内容或关注重点。"
                },
                {
                    "name": "软件与工作状态分析",
                    "system_prompt": "你是一位资深的生产力工作辅助顾问。请细致分析用户当前打开的办公应用、浏览器选项卡、代码编辑器或文档处理工具，总结当前的核心工作任务进度，并指出可能存在的错误提示或待办事宜。",
                    "user_prompt": "仔细观察桌面工作区，总结我的当前状态和重点信息。"
                },
                {
                    "name": "代码语法与排错助手",
                    "system_prompt": "你是一位资深编程专家。观察屏幕中的代码编辑器、终端窗口和报错堆栈日志，指出当前的编程语言、正在编写的功能模块，以及具体的报错原因与解决建议。直接给出简明的口语建议，方便发音播报。",
                    "user_prompt": "帮我看看屏幕上的代码或报错情况，告诉我发生了什么并提出修改建议。"
                },
                {
                    "name": "网页与文档快速摘要",
                    "system_prompt": "你是一位信息整理专家。重点关注当前屏幕中所展示的网页内容、长文本新闻、PDF文档或邮件，直接提炼出其中的3个最关键中心思想或论点，用简短清晰的语言概述。",
                    "user_prompt": "提取屏幕当前显示的文档或网页重点摘要。"
                },
                {
                    "name": "实时英中双语口语翻译",
                    "system_prompt": "你是一位同声传译与跨国交流助手。如果屏幕中有英文或外部语言界面/文章，请先以一句话总结核心大意，然后精准口语化翻译屏幕最中心区域的英文文本。",
                    "user_prompt": "请将当前屏幕上方及中心最关键的英文翻译并解说为中文。"
                }
            ]
        },
        "capture": {
            "mode": "fullscreen",  # "fullscreen", "region", "active_window"
            "monitor_index": 0,
            "region": [0, 0, 1920, 1080],
            "interval_seconds": 6.0,
            "auto_start_monitor": False,
            "image_quality": 80,
            "max_width": 1280
        },
        "shortcuts": {
            "enable": True,
            "capture_trigger": "Ctrl+Alt+S",
            "stop_tts": "Ctrl+Alt+Q",
            "toggle_monitor": "Ctrl+Alt+M"
        }
    }

    def __new__(cls, config_path: str = "config.json"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ConfigManager, cls).__new__(cls)
                cls._instance._init(config_path)
            return cls._instance

    def _init(self, config_path: str):
        with self._lock:
            self.config_path = os.path.abspath(config_path)
            self.config_data = {}
            self.load()

    def load(self) -> Dict[str, Any]:
        """从磁盘加载配置文件，若不存在或损坏则自动创建缺省配置"""
        with self._lock:
            if os.path.exists(self.config_path):
                try:
                    with open(self.config_path, "r", encoding="utf-8") as f:
                        loaded = json.load(f)
                    self.config_data = self._merge_dict(self.DEFAULT_CONFIG.copy(), loaded)
                except Exception as e:
                    print(f"[ConfigManager] 加载配置文件异常，将恢复缺省配置: {e}")
                    self.config_data = self._merge_dict({}, self.DEFAULT_CONFIG)
                    self._save_unlocked()
            else:
                self.config_data = self._merge_dict({}, self.DEFAULT_CONFIG)
                self._save_unlocked()
            return self.config_data

    def save(self) -> bool:
        """保存当前配置到磁盘"""
        with self._lock:
            return self._save_unlocked()

    def _save_unlocked(self) -> bool:
        try:
            os.makedirs(os.path.dirname(self.config_path) or ".", exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"[ConfigManager] 保存配置文件失败: {e}")
            return False

    def _merge_dict(self, default: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并字典，确保当新版本增加新配置字段时自动补充"""
        merged = default.copy()
        for k, v in custom.items():
            if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
                merged[k] = self._merge_dict(merged[k], v)
            else:
                merged[k] = v
        return merged

    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """安全读取配置"""
        with self._lock:
            if section not in self.config_data:
                return default
            if key is None:
                return self.config_data.get(section, default)
            return self.config_data[section].get(key, default)

    def set(self, section: str, key: str, value: Any) -> bool:
        """更新并保存指定字段项"""
        with self._lock:
            if section not in self.config_data:
                self.config_data[section] = {}
            self.config_data[section][key] = value
            return self._save_unlocked()

    def set_section(self, section: str, data: Dict[str, Any]) -> bool:
        """替换或更新整个分组配置"""
        with self._lock:
            if section not in self.config_data or not isinstance(self.config_data[section], dict):
                self.config_data[section] = {}
            self.config_data[section].update(data)
            return self._save_unlocked()

    def get_all(self) -> Dict[str, Any]:
        with self._lock:
            return self.config_data.copy()

    def get_active_ai_config(self) -> Dict[str, Any]:
        """获取当前激活的 AI 模型完整连接参数"""
        with self._lock:
            vision = self.get("vision_ai", default={})
            mode = vision.get("mode", "cloud")
            if mode == "cloud":
                provider = vision.get("cloud_provider", "openai")
                base_url = vision.get("base_url", "https://api.openai.com/v1")
                if provider == "aliyun" and ("openai.com" in base_url or not base_url):
                    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
                elif provider == "zhipu" and ("openai.com" in base_url or not base_url):
                    base_url = "https://open.bigmodel.cn/api/paas/v4"
                return {
                    "mode": "cloud",
                    "provider": provider,
                    "base_url": base_url,
                    "api_key": vision.get("api_key", ""),
                    "model": vision.get("model", "gpt-4o-mini"),
                    "temperature": vision.get("temperature", 0.5),
                    "max_tokens": vision.get("max_tokens", 800)
                }
            else:
                return {
                    "mode": "local",
                    "provider": vision.get("local_provider", "ollama"),
                    "base_url": vision.get("local_base_url", "http://localhost:11434/v1"),
                    "api_key": vision.get("local_api_key", "ollama"),
                    "model": vision.get("local_model", "llava:13b"),
                    "temperature": vision.get("temperature", 0.5),
                    "max_tokens": vision.get("max_tokens", 800)
                }

    def get_active_tts_config(self) -> Dict[str, Any]:
        """获取当前激活的 TTS 语音引擎配置"""
        with self._lock:
            tts = self.get("tts", default={})
            return tts.copy()
