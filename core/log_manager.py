import os
import time
import json
import threading
from typing import List, Dict, Any, Callable, Optional

class LogManager:
    """日志引擎与历史记录管理模块，支持将日志流式分发给 UI 日志页，并持久化至本地磁盘"""
    _instance = None
    _lock = threading.RLock()

    def __new__(cls, log_dir: str = "logs"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LogManager, cls).__new__(cls)
                cls._instance._init(log_dir)
            return cls._instance

    def _init(self, log_dir: str):
        with self._lock:
            self.log_dir = os.path.abspath(log_dir)
            os.makedirs(self.log_dir, exist_ok=True)
            self.log_file = os.path.join(self.log_dir, f"system_{time.strftime('%Y%m%d')}.log")
            self.history_file = os.path.join(self.log_dir, "recognition_history.json")
            self.logs: List[Dict[str, str]] = []
            self.history: List[Dict[str, Any]] = []
            self.listeners: List[Callable[[Dict[str, str]], None]] = []
            self.history_listeners: List[Callable[[Dict[str, Any]], None]] = []
            self._load_history()

    def add_listener(self, callback: Callable[[Dict[str, str]], None]):
        with self._lock:
            if callback not in self.listeners:
                self.listeners.append(callback)

    def remove_listener(self, callback: Callable[[Dict[str, str]], None]):
        with self._lock:
            if callback in self.listeners:
                self.listeners.remove(callback)

    def add_history_listener(self, callback: Callable[[Dict[str, Any]], None]):
        with self._lock:
            if callback not in self.history_listeners:
                self.history_listeners.append(callback)

    def log(self, message: str, level: str = "INFO", category: str = "SYSTEM"):
        """
        记录一条系统日志并分发到注册监听的 GUI 视图
        :param message: 日志内容
        :param level: INFO, WARN, ERROR, SUCCESS
        :param category: SYSTEM, AI, TTS, CAPTURE, USER
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "level": level.upper(),
            "category": category.upper(),
            "message": message
        }
        with self._lock:
            self.logs.append(entry)
            if len(self.logs) > 2000:
                self.logs.pop(0)

        # 写文件
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] [{level.upper()}] [{category.upper()}] {message}\n")
        except Exception:
            pass

        # 回调通知 GUI
        for listener in list(self.listeners):
            try:
                listener(entry)
            except Exception as e:
                print(f"[LogManager] 回调通知 UI 失败: {e}")

    def record_recognition(self, image_b64_sample: str, prompt: str, result: str, elapsed_ms: int, provider: str, model: str):
        """记录一条识别成功或失败的历史记录"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        item = {
            "id": str(time.time()),
            "timestamp": timestamp,
            "prompt": prompt,
            "result": result,
            "elapsed_ms": elapsed_ms,
            "provider": provider,
            "model": model,
            "image_thumb": image_b64_sample[:100] if image_b64_sample else ""
        }
        with self._lock:
            self.history.insert(0, item)
            if len(self.history) > 300:
                self.history.pop()
        self._save_history()

        for listener in list(self.history_listeners):
            try:
                listener(item)
            except Exception as e:
                print(f"[LogManager] 回调历史监听 UI 失败: {e}")

    def get_logs(self, limit: int = 500, level_filter: str = "ALL", category_filter: str = "ALL") -> List[Dict[str, str]]:
        with self._lock:
            result = []
            for item in self.logs:
                if level_filter != "ALL" and item["level"] != level_filter:
                    continue
                if category_filter != "ALL" and item["category"] != category_filter:
                    continue
                result.append(item)
            return result[-limit:]

    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._lock:
            return self.history[:limit]

    def clear_logs(self):
        with self._lock:
            self.logs.clear()
            try:
                with open(self.log_file, "w", encoding="utf-8") as f:
                    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [INFO] [SYSTEM] 日志已清空\n")
            except Exception:
                pass

    def clear_history(self):
        with self._lock:
            self.history.clear()
        self._save_history()

    def _load_history(self):
        with self._lock:
            if os.path.exists(self.history_file):
                try:
                    with open(self.history_file, "r", encoding="utf-8") as f:
                        self.history = json.load(f)
                except Exception:
                    self.history = []

    def _save_history(self):
        with self._lock:
            try:
                with open(self.history_file, "w", encoding="utf-8") as f:
                    json.dump(self.history[:300], f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[LogManager] 保存识别历史失败: {e}")
