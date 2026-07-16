import time
import traceback
from typing import Dict, Any, Optional
from PySide6.QtCore import QThread, Signal, QObject
from core.config_manager import ConfigManager
from core.screen_capture import ScreenCapturer
from core.vision_engine import VisionEngine
from core.tts_engine import TTSEngine
from core.log_manager import LogManager

class RecognitionWorker(QThread):
    """单次视觉识别与读屏处理后台线程"""
    # 信号定义：
    started_capture = Signal()
    capture_finished = Signal(object, str)  # PIL.Image 对象或 None, Base64 字符串
    started_ai = Signal()
    ai_finished = Signal(bool, str, dict)  # (成功布尔值, 识别文字/报错文本, 元数据)
    started_tts = Signal(str)
    tts_finished = Signal(bool, str)
    worker_finished = Signal()

    def __init__(self, parent=None, custom_user_prompt: str = ""):
        super().__init__(parent)
        self.custom_user_prompt = custom_user_prompt
        self.cfg = ConfigManager()
        self.logger = LogManager()
        self.vision = VisionEngine()
        self.tts = TTSEngine()

    def run(self):
        try:
            self.logger.log("开始执行屏幕实时捕捉与 AI 识别任务...", level="INFO", category="AI")
            self.started_capture.emit()

            # 1. 截图
            capture_cfg = self.cfg.get("capture", default={})
            mode = capture_cfg.get("mode", "fullscreen")
            monitor_idx = int(capture_cfg.get("monitor_index", 1))
            region = capture_cfg.get("region", [0, 0, 1920, 1080])
            max_width = int(capture_cfg.get("max_width", 1280))
            quality = int(capture_cfg.get("image_quality", 80))

            img, b64_str = ScreenCapturer.capture(
                mode=mode,
                monitor_index=monitor_idx,
                region=region,
                max_width=max_width,
                quality=quality
            )

            if img is None or not b64_str:
                err_msg = "屏幕捕获失败：未能成功抓取显示画面。"
                self.logger.log(err_msg, level="ERROR", category="CAPTURE")
                self.capture_finished.emit(None, "")
                self.ai_finished.emit(False, err_msg, {})
                self.worker_finished.emit()
                return

            self.capture_finished.emit(img, b64_str)
            self.logger.log(f"截图完毕 (大小: {img.width}x{img.height}, 编码后长: {len(b64_str)}B)", level="INFO", category="CAPTURE")

            # 2. AI 视觉分析
            self.started_ai.emit()
            ai_cfg = self.cfg.get_active_ai_config()
            prompt_cfg = self.cfg.get("prompts", default={})
            sys_prompt = prompt_cfg.get("system_prompt", "")
            user_prompt = self.custom_user_prompt if self.custom_user_prompt else prompt_cfg.get("user_prompt", "仔细观察并分析画面要点。")

            success, text, meta = self.vision.analyze(
                base64_image=b64_str,
                system_prompt=sys_prompt,
                user_prompt=user_prompt,
                ai_config=ai_cfg
            )

            self.ai_finished.emit(success, text, meta)
            if success:
                self.logger.log(f"AI 识别成功 [{meta.get('model')}] (耗时: {meta.get('elapsed_ms')}ms)", level="SUCCESS", category="AI")
                self.logger.record_recognition(b64_str, user_prompt, text, meta.get("elapsed_ms", 0), meta.get("provider", ""), meta.get("model", ""))
            else:
                self.logger.log(f"AI 识别提示: {text}", level="ERROR", category="AI")
                self.worker_finished.emit()
                return

            # 3. TTS 朗读
            tts_cfg = self.cfg.get_active_tts_config()
            if tts_cfg.get("enabled", True):
                self.started_tts.emit(text)
                self.logger.log("开始调用 TTS 语音合成并播放...", level="INFO", category="TTS")
                tts_ok, tts_msg = self.tts.speak(text, tts_cfg)
                self.tts_finished.emit(tts_ok, tts_msg)
                if tts_ok:
                    self.logger.log(f"语音回放状态: {tts_msg}", level="SUCCESS", category="TTS")
                else:
                    self.logger.log(f"语音回放异常: {tts_msg}", level="WARN", category="TTS")

        except Exception as e:
            err = f"工作线程发生未预料异常: {traceback.format_exc()}"
            self.logger.log(err, level="ERROR", category="SYSTEM")
            self.ai_finished.emit(False, f"系统任务异常: {str(e)}", {})
        finally:
            self.worker_finished.emit()


class AutoMonitorWorker(QThread):
    """后台定频循环自动监测线程"""
    trigger_task = Signal()
    status_changed = Signal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = False
        self.cfg = ConfigManager()

    def start_monitor(self):
        if not self.is_running:
            self.is_running = True
            self.start()
            self.status_changed.emit(True, "自动监测已运行")

    def stop_monitor(self):
        if self.is_running:
            self.is_running = False
            self.status_changed.emit(False, "自动监测已停止")

    def run(self):
        self.is_running = True
        while self.is_running:
            try:
                # 触发一次识别任务
                self.trigger_task.emit()
                # 检查周期
                capture_cfg = self.cfg.get("capture", default={})
                interval = float(capture_cfg.get("interval_seconds", 6.0))
                interval = max(1.5, min(120.0, interval))

                # 为支持平滑快速关停，以 0.2 秒小间隔探测
                elapsed = 0.0
                while self.is_running and elapsed < interval:
                    time.sleep(0.2)
                    elapsed += 0.2
            except Exception as e:
                print(f"[AutoMonitorWorker] 轮询异常: {e}")
                time.sleep(2)
