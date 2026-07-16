import asyncio
import io
import os
import tempfile
import threading
import requests
from typing import Dict, Any, Tuple, Optional
from utils.audio_player import AudioPlayer

class TTSEngine:
    """TTS 语音合成与回放引擎，支持云端 (Edge-TTS, OpenAI-TTS, Custom-HTTP) 及本地 (PyTTSx3, Local-HTTP)"""

    def __init__(self):
        self.player = AudioPlayer()
        self._speech_lock = threading.RLock()
        self.is_speaking = False

    def speak(self, text: str, tts_config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        同步或异步触发发声，此函数建议在 Worker 线程或独立后台调用
        :param text: 要转换成语音的纯文本
        :param tts_config: TTS 配置词典
        :return: (是否成功, 状态或异常描述)
        """
        if not text or not text.strip():
            return False, "文本为空，无需朗读。"

        if not tts_config.get("enabled", True):
            return False, "TTS 功能当前已停用。"

        provider = tts_config.get("provider", "edge-tts")
        volume = int(tts_config.get("volume", 100))

        with self._speech_lock:
            self.is_speaking = True
            try:
                # 1. Edge-TTS 微软云端自然人声
                if provider == "edge-tts":
                    voice = tts_config.get("voice", "zh-CN-XiaoxiaoNeural")
                    rate_val = tts_config.get("rate", 0)
                    if isinstance(rate_val, str) and "%" in rate_val:
                        rate_str = rate_val
                    else:
                        try:
                            rate_num = int(rate_val)
                            rate_str = f"+{rate_num}%" if rate_num >= 0 else f"{rate_num}%"
                        except Exception:
                            rate_str = "+0%"
                    success, msg = self._speak_edge_tts(text, voice, rate_str, volume)

                # 2. OpenAI TTS 官方或兼容接口
                elif provider == "openai-tts":
                    voice = tts_config.get("openai_tts_voice", "alloy")
                    model = tts_config.get("openai_tts_model", "tts-1")
                    api_key = tts_config.get("api_key", "")
                    base_url = tts_config.get("base_url", "https://api.openai.com/v1")
                    success, msg = self._speak_openai_tts(text, voice, model, api_key, base_url, volume)

                # 3. Windows 本地 PyTTSx3 离线语音
                elif provider == "pyttsx3":
                    try:
                        rate_offset = int(tts_config.get("rate", 0)) if not isinstance(tts_config.get("rate", 0), str) else 0
                    except Exception:
                        rate_offset = 0
                    success, msg = self._speak_pyttsx3(text, rate_offset, volume)

                # 4. 自定义 HTTP TTS 接口 (本地/第三方)
                elif provider in ["custom-http", "local-http"]:
                    url = tts_config.get("custom_tts_url", "http://localhost:9880/tts")
                    token = tts_config.get("custom_tts_token", "")
                    success, msg = self._speak_custom_http(text, url, token, volume)
                else:
                    success, msg = self._speak_edge_tts(text, "zh-CN-XiaoxiaoNeural", "+0%", volume)

                return success, msg
            finally:
                self.is_speaking = False

    def stop(self):
        """立即停止当前正在朗读或播放的语音"""
        with self._speech_lock:
            self.is_speaking = False
            self.player.stop()

    def _speak_edge_tts(self, text: str, voice: str, rate: str, volume: int) -> Tuple[bool, str]:
        try:
            import edge_tts
            async def _generate_audio():
                communicate = edge_tts.Communicate(text, voice, rate=rate)
                audio_bytes = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_bytes += chunk["data"]
                return audio_bytes

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    new_loop = asyncio.new_event_loop()
                    audio_data = new_loop.run_until_complete(_generate_audio())
                    new_loop.close()
                else:
                    audio_data = loop.run_until_complete(_generate_audio())
            except RuntimeError:
                new_loop = asyncio.new_event_loop()
                audio_data = new_loop.run_until_complete(_generate_audio())
                new_loop.close()

            if audio_data and len(audio_data) > 0:
                self.player.play_bytes(audio_data, volume=volume)
                return True, f"[Edge-TTS ({voice})] 语音合成完成并已开始播放 (大小: {len(audio_data)}B)"
            else:
                return False, f"[Edge-TTS] 合成语音流返回数据为空。"
        except Exception as e:
            return False, f"[Edge-TTS] 微软云端发声异常 (检查网络连接): {str(e)}"

    def _speak_openai_tts(self, text: str, voice: str, model: str, api_key: str, base_url: str, volume: int) -> Tuple[bool, str]:
        try:
            if not base_url:
                base_url = "https://api.openai.com/v1"
            if not base_url.endswith("/audio/speech"):
                endpoint = f"{base_url.rstrip('/')}/audio/speech"
            else:
                endpoint = base_url

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "input": text,
                "voice": voice,
                "response_format": "mp3"
            }
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                audio_data = resp.content
                if audio_data and len(audio_data) > 0:
                    self.player.play_bytes(audio_data, volume=volume)
                    return True, f"[OpenAI TTS ({voice})] 语音合成成功"
                else:
                    return False, "[OpenAI TTS] 返回语音字节流为空"
            else:
                return False, f"[OpenAI TTS] 接口响应错误 [Status {resp.status_code}]: {resp.text[:200]}"
        except Exception as e:
            return False, f"[OpenAI TTS] 请求报错: {str(e)}"

    def _speak_pyttsx3(self, text: str, rate_offset: int, volume: int) -> Tuple[bool, str]:
        """使用 Windows SAPI5 离线引擎合成或播放"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            current_rate = engine.getProperty('rate')
            engine.setProperty('rate', max(80, min(400, current_rate + rate_offset)))
            engine.setProperty('volume', max(0.0, min(1.0, volume / 100.0)))

            tmp_fd, tmp_path = tempfile.mkstemp(suffix=".wav", prefix="ailook_pyttsx3_")
            os.close(tmp_fd)
            engine.save_to_file(text, tmp_path)
            engine.runAndWait()

            if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 100:
                self.player.play_file(tmp_path, volume=volume)
                return True, f"[PyTTSX3 本地离线] 合成完毕 ({os.path.basename(tmp_path)})"
            else:
                engine.say(text)
                engine.runAndWait()
                return True, "[PyTTSX3 本地离线] 语音直接播报完毕"
        except Exception as e:
            return False, f"[PyTTSX3 本地离线] 引擎发声报错: {str(e)}"

    def _speak_custom_http(self, text: str, url: str, token: str, volume: int) -> Tuple[bool, str]:
        try:
            headers = {"Content-Type": "application/json"}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            payload = {"text": text}
            resp = requests.post(url, headers=headers, json=payload, timeout=25)
            if resp.status_code == 200:
                audio_data = resp.content
                if audio_data and len(audio_data) > 0:
                    self.player.play_bytes(audio_data, volume=volume)
                    return True, f"[自定义 HTTP TTS] 合成完成并开始播报"
                else:
                    return False, "[自定义 HTTP TTS] 返回数据大小为 0"
            else:
                return False, f"[自定义 HTTP TTS] 服务响应异常 [Status {resp.status_code}]"
        except Exception as e:
            return False, f"[自定义 HTTP TTS] 调用网络请求失败: {str(e)}"
