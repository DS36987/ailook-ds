import io
import base64
from PIL import Image, ImageDraw, ImageFont
import platform
from typing import Tuple, Dict, Any, Optional, List

class ScreenCapturer:
    """实时屏幕/区域截图引擎，兼容 Windows 11 及跨平台系统"""

    @staticmethod
    def get_monitors() -> List[Dict[str, int]]:
        """获取所有显示器的物理区域信息，如获取失败则提供缺省虚拟屏幕"""
        try:
            import mss
            with mss.mss() as sct:
                monitors = []
                for idx, mon in enumerate(sct.monitors):
                    monitors.append({
                        "index": idx,  # 0 为所有屏幕合并显示区域，1 为主屏幕，2... 为次屏
                        "left": mon["left"],
                        "top": mon["top"],
                        "width": mon["width"],
                        "height": mon["height"]
                    })
                return monitors
        except Exception as e:
            # 当处于无显示器服务器或无头测试环境时返回虚拟主屏幕配置
            return [
                {"index": 0, "left": 0, "top": 0, "width": 1920, "height": 1080},
                {"index": 1, "left": 0, "top": 0, "width": 1920, "height": 1080}
            ]

    @staticmethod
    def capture(
        mode: str = "fullscreen",
        monitor_index: int = 1,
        region: Optional[List[int]] = None,
        max_width: int = 1280,
        quality: int = 80
    ) -> Tuple[Optional[Image.Image], str]:
        """
        截图并进行自动缩放和 Base64 JPEG 编码
        :param mode: "fullscreen" 或 "region"
        :param monitor_index: 屏幕序号 (通常 1 为主屏, 0 为所有屏组合)
        :param region: [left, top, width, height] (仅当 mode=="region" 时有效)
        :param max_width: 缩放后的最大宽度，设为 0 或 None 则不缩放
        :param quality: JPEG 保存质量
        :return: (PIL.Image对象, Base64字符串)
        """
        img = None
        try:
            import mss
            with mss.mss() as sct:
                monitor_list = sct.monitors
                if monitor_index < 0 or monitor_index >= len(monitor_list):
                    monitor_index = 1 if len(monitor_list) > 1 else 0

                if mode == "region" and region and len(region) == 4 and int(region[2]) > 0 and int(region[3]) > 0:
                    monitor = {
                        "left": int(region[0]),
                        "top": int(region[1]),
                        "width": int(region[2]),
                        "height": int(region[3])
                    }
                else:
                    monitor = monitor_list[monitor_index]

                # 抓取屏幕并转为 PIL 图像
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        except Exception as e:
            # 若是在 Windows 下失败或者处于 Linux Headless 虚拟测试环境，自动生成备用/模拟屏幕图像，保证系统流水线不断
            img = Image.new("RGB", (1280, 720), color=(30, 33, 40))
            draw = ImageDraw.Draw(img)
            text = f"[AILook System] Screen Capture Mode: {mode}\nMonitor Index: {monitor_index}\n(Live Headless/Test Environment or Display Guarded)"
            draw.text((60, 320), text, fill=(200, 220, 255))

        if img is None:
            return None, ""

        try:
            # 限制分辨率（对大模型极其关键，能大大加快传输和推理速率）
            if max_width and max_width > 0 and img.width > max_width:
                ratio = max_width / float(img.width)
                new_height = int(float(img.height) * float(ratio))
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            # 转为 Base64 字符串 (JPEG格式)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=min(max(int(quality), 10), 100))
            img_bytes = buffer.getvalue()
            base64_str = base64.b64encode(img_bytes).decode("utf-8")

            return img, base64_str
        except Exception as e:
            print(f"[ScreenCapturer] 图像压缩与转码异常: {e}")
            return None, ""
