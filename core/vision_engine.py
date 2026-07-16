import json
import time
import requests
from typing import Dict, Any, Tuple, Optional

class VisionEngine:
    """AI 视觉识别引擎，支持接入云端 API 与本地部署 AI"""

    def __init__(self, timeout: int = 45):
        self.timeout = timeout

    def analyze(
        self,
        base64_image: str,
        system_prompt: str,
        user_prompt: str,
        ai_config: Dict[str, Any]
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        调用 AI 进行屏幕视觉内容分析
        :param base64_image: Base64 编码的 JPEG 图片
        :param system_prompt: 系统提示词
        :param user_prompt: 用户提示词
        :param ai_config: AI 连接参数字典
        :return: (是否成功, 文本识别结果/错误信息, 性能元数据如耗时)
        """
        start_time = time.time()
        meta = {
            "elapsed_ms": 0,
            "provider": ai_config.get("provider", "unknown"),
            "model": ai_config.get("model", "unknown"),
            "mode": ai_config.get("mode", "cloud")
        }

        if not base64_image:
            return False, "错误：屏幕截图 Base64 数据为空，无法进行 AI 视觉识别。", meta

        mode = ai_config.get("mode", "cloud")
        provider = ai_config.get("provider", "openai")
        base_url = ai_config.get("base_url", "").rstrip("/")
        api_key = ai_config.get("api_key", "")
        model = ai_config.get("model", "gpt-4o-mini")
        temperature = float(ai_config.get("temperature", 0.5))
        max_tokens = int(ai_config.get("max_tokens", 800))

        try:
            if mode == "local" and provider in ["ollama", "localai"]:
                success, text = self._call_local_ollama(
                    base_url=base_url,
                    model=model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    base64_image=base64_image,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:
                # 默认使用 OpenAI 及各大平台通用兼容视觉接口 Protocol
                success, text = self._call_openai_compatible(
                    base_url=base_url,
                    api_key=api_key,
                    model=model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    base64_image=base64_image,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            meta["elapsed_ms"] = int((time.time() - start_time) * 1000)
            return success, text, meta
        except Exception as e:
            meta["elapsed_ms"] = int((time.time() - start_time) * 1000)
            return False, f"AI 请求发生未捕获异常: {str(e)}", meta

    def _call_openai_compatible(
        self,
        base_url: str,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        base64_image: str,
        temperature: float,
        max_tokens: int
    ) -> Tuple[bool, str]:
        if not base_url:
            base_url = "https://api.openai.com/v1"
        if not base_url.endswith("/chat/completions"):
            endpoint = f"{base_url}/chat/completions"
        else:
            endpoint = base_url

        headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        messages = []
        if system_prompt and system_prompt.strip():
            messages.append({
                "role": "system",
                "content": system_prompt.strip()
            })

        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_prompt if user_prompt else "仔细观察并分析这张屏幕截图。"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        })

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0].get("message", {}).get("content", "").strip()
                    if content:
                        return True, content
                    else:
                        return False, "AI 模型返回内容为空。"
                else:
                    return False, f"AI 响应解析错误: {json.dumps(data, ensure_ascii=False)[:300]}"
            else:
                err_msg = resp.text[:400]
                return False, f"API 响应错误 [Status {resp.status_code}]: {err_msg}"
        except requests.exceptions.Timeout:
            return False, f"请求超时 ({self.timeout}秒)，请检查网络或本地 AI 服务运行状态。"
        except requests.exceptions.ConnectionError:
            return False, f"连接失败：无法连接至服务端 [{endpoint}]，请检查 API 网址是否填写正确或本地服务已开。"
        except Exception as e:
            return False, f"调用接口失败: {str(e)}"

    def _call_local_ollama(
        self,
        base_url: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        base64_image: str,
        temperature: float,
        max_tokens: int
    ) -> Tuple[bool, str]:
        """优先调用 Ollama 原生生成接口 /api/generate，如 base_url 已经是 /v1 则退回 _call_openai_compatible"""
        if "/v1" in base_url:
            return self._call_openai_compatible(
                base_url=base_url,
                api_key="ollama",
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                base64_image=base64_image,
                temperature=temperature,
                max_tokens=max_tokens
            )

        if not base_url:
            base_url = "http://localhost:11434"
        if not base_url.endswith("/api/generate"):
            endpoint = f"{base_url.rstrip('/')}/api/generate"
        else:
            endpoint = base_url

        full_prompt = f"{system_prompt}\n\n{user_prompt}".strip() if system_prompt else user_prompt
        payload = {
            "model": model,
            "prompt": full_prompt,
            "images": [base64_image],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            resp = requests.post(endpoint, json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                response_text = data.get("response", "").strip()
                if response_text:
                    return True, response_text
                else:
                    return False, "Ollama 返回的生成文本为空。"
            else:
                return False, f"Ollama 本地接口报错 [Status {resp.status_code}]: {resp.text[:300]}"
        except requests.exceptions.Timeout:
            return False, f"本地 AI 推理超时 ({self.timeout}秒)，请确认设备性能及模型大小。"
        except requests.exceptions.ConnectionError:
            return False, f"无法连接到本地 Ollama 服务 [{endpoint}]，请检查 `ollama serve` 是否在 Windows 11 中正常运行。"
        except Exception as e:
            return False, f"调用本地 AI 发生错误: {str(e)}"
