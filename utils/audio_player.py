import os
import tempfile
import threading
import time
from typing import Optional

class AudioPlayer:
    """跨平台线程安全音频回放器，支持 Pygame 驱动播放与虚拟声卡回落保护"""
    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AudioPlayer, cls).__new__(cls)
                cls._instance._init()
            return cls._instance

    def _init(self):
        with self._lock:
            self.mixer_ready = False
            self._current_temp_file = None
            self._playback_lock = threading.RLock()
            try:
                import pygame
                pygame.mixer.init()
                self.mixer_ready = True
            except Exception as e:
                print(f"[AudioPlayer] 初始化 Pygame 音频驱动器提示 (如处于无声卡设备): {e}")
                self.mixer_ready = False

    def play_bytes(self, audio_data: bytes, volume: int = 100) -> bool:
        """从字节流中异步播放音频"""
        if not audio_data or len(audio_data) == 0:
            return False

        with self._playback_lock:
            self.stop()
            try:
                suffix = ".mp3" if audio_data[:3] == b'ID3' or b'\xff\xfb' in audio_data[:10] else ".wav"
                tmp_fd, tmp_path = tempfile.mkstemp(suffix=suffix, prefix="ailook_tts_")
                with os.fdopen(tmp_fd, "wb") as f:
                    f.write(audio_data)
                self._current_temp_file = tmp_path

                if self.mixer_ready:
                    import pygame
                    try:
                        vol = max(0, min(100, volume)) / 100.0
                        pygame.mixer.music.load(tmp_path)
                        pygame.mixer.music.set_volume(vol)
                        pygame.mixer.music.play()
                        return True
                    except Exception as play_err:
                        print(f"[AudioPlayer] Pygame 播放临时音频文件失败: {play_err}")
                else:
                    print(f"[AudioPlayer] (虚拟回放/无声卡) 音频已生成至: {tmp_path} (大小: {len(audio_data)} 字节)")
                    return True
            except Exception as e:
                print(f"[AudioPlayer] 播放字节流异常: {e}")
                return False

    def play_file(self, file_path: str, volume: int = 100) -> bool:
        """从文件路径中异步播放音频"""
        if not os.path.exists(file_path):
            return False
        with self._playback_lock:
            self.stop()
            if self.mixer_ready:
                try:
                    import pygame
                    vol = max(0, min(100, volume)) / 100.0
                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.set_volume(vol)
                    pygame.mixer.music.play()
                    return True
                except Exception as e:
                    print(f"[AudioPlayer] 播放文件异常: {e}")
            else:
                print(f"[AudioPlayer] (虚拟回放) 正在播放文件: {file_path}")
                return True
        return False

    def stop(self):
        """立即停止当前回放并清理可能存在的临时文件"""
        with self._playback_lock:
            if self.mixer_ready:
                try:
                    import pygame
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()
                except Exception:
                    pass
            if self._current_temp_file and os.path.exists(self._current_temp_file):
                try:
                    os.unlink(self._current_temp_file)
                except Exception:
                    pass
                self._current_temp_file = None

    def is_playing(self) -> bool:
        """检查当前是否正在回放音频"""
        with self._playback_lock:
            if self.mixer_ready:
                try:
                    import pygame
                    return pygame.mixer.music.get_busy()
                except Exception:
                    return False
            return False
