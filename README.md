# AI Look Desktop System (Windows 11 现代视觉识别与智能读屏系统)

![Platform](https://img.shields.io/badge/Platform-Windows%2011%20%7C%2010-0078D4?style=for-the-badge&logo=windows)
![GUI Framework](https://img.shields.io/badge/GUI-PySide6%20%28Qt6%29-41CD52?style=for-the-badge&logo=qt)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

`AI Look Desktop System` (ailook-ds) 是一款专为 **Windows 11** 打造的智能视觉实时识别与读屏处理系统。系统不仅具备高频自适应实时抓屏与区域捕获能力，还能灵活调配**云端与本地大模型 API**，并将识别与解说通过**云端或本地离线 TTS**合成语音实时播报。

系统采用原生可拆卸/双布局架构设计：**所有核心界面全部独立分离（分为预览页、设置页和日志页）**，既可以在多标签聚合主控面板中高效操作，也可以一键剥离为各自完全独立的 Windows 11 原生圆角窗口，配合桌面悬浮极简小窗（Floating Bar），多屏幕排布与隐身轮询体验极佳！

---

## 🌟 核心功能特性

### 1. 🤖 AI 视觉大模型自由接入（云端 + 本地）
*   **☁️ 云端通用 API 接入**：
    *   原生支持 **OpenAI** (`gpt-4o`, `gpt-4o-mini`, `gpt-4-vision-preview`)。
    *   原生兼容 **阿里云通义千问 (DashScope)** 兼容模式 (`qwen-vl-max`, `qwen-vl-plus`)。
    *   原生兼容 **智谱 AI (GLM-4V)** 及 **Anthropic Claude 3.5 Sonnet** 视觉接口。
    *   支持自定义 API Base URL 与 Bearer Token，支持调节 Temperature 和 Max Tokens。
*   **🏠 本地私有化部署 AI (Ollama / LocalAI)**：
    *   支持对接到本地 Ollama (`http://localhost:11434/v1` 或 `/api/generate`)。
    *   支持运行 `llava:13b`, `qwen2-vl:7b`, `bakllava` 等本地多模态模型，完全零隐私泄露、零网络调用费用。

### 2. 🗣️ TTS 语音朗读与发声接入（云端 + 本地）
*   **⚡ 微软云端自然人声 (Edge-TTS)**：
    *   内置支持，**无需配置任何 API Key 开箱即用**！
    *   预置多国多语种精选音色（如中文自然女声 `zh-CN-XiaoxiaoNeural`、沉稳男声 `zh-CN-YunxiNeural`、纪录片音 `zh-CN-YunjianNeural`、美英日音色等），支持 -50% ~ +50% 语速平滑微调。
*   **💻 Windows 本地离线引擎 (PyTTSX3)**：
    *   基于 Windows SAPI5 离线合成器，无需联网、零延迟，在无网络和飞行模式下依旧流畅发音解说。
*   **🎙️ OpenAI TTS 官方云语音与自定义 HTTP**：
    *   支持调用 `https://api.openai.com/v1/audio/speech` (Alloy, Echo, Fable, Onyx 等高拟真音色)。
    *   支持第三方本地自建 TTS 服务 (如 GPT-SoVITS / ChatTTS / Custom REST API)。

### 3. 🧩 彻底分离的模块化与多窗口独立架构
*   **🎯 独立预览页 (Preview Page)**：
    *   实时显示屏幕截图捕获画面、显示分辨率和区域信息。
    *   流式展现大模型输出的文字摘要、工作排错与解说文本，并提供一键复制与复读。
*   **⚙️ 独立设置页 (Settings Page)**：
    *   分区清晰的 AI 引擎连接参数、TTS 语音引擎配置、提示词与截屏热键设置卡片，实时一键测试。
*   **📋 独立日志与历史记录页 (Logs & History Page)**：
    *   **流式日志台**：实时追踪 AI 请求耗时、截图字节、TTS 状态与报错告警。
    *   **历史数据库**：表格存储每条成功与失败的视觉识别记录，点击表格即可查看详细抓拍对白与分析结果。
*   **✨ 多窗口自由拆卸剥离机制 (Detachable Multi-Window)**：
    *   **一键全分离 / 单个分离**：无论在主侧边栏点击 **【✨ 全部分离为独立窗口】** 还是在各界面右上角点击 **【↗ 剥离为独立窗口】**，预览、设置、日志三页均可瞬间剥离为独立的 Windows 11 原生卡片窗口，在多台显示器或屏幕各角自由摆放！
    *   **随心合并归位**：随时点击 **【↙ 归位至主界面】** 或 **【📦 全部合并至主界面】** 重新吸附整合。

### 4. ⌨️ 屏幕捕获模式与全局热键控制
*   **抓屏控制**：支持指定物理屏幕全屏 (`fullscreen`)，或自定义精确矩形坐标 (`region`)；内置分辨率上限缩放引擎 (`max_width=1280`)，极大减少 LLM Tokens 消耗和网络传输延迟。
*   **自动定频轮询 (Auto Monitor)**：自定义间隔时间 (1.0秒 ~ 120秒)，后台异步并发截屏 -> 视觉分析 -> 语音播报。
*   **全局与局部快捷键 (Shortcuts)**：
    *   `Ctrl+Alt+S`：立即触发单次截图识别与语音朗读。
    *   `Ctrl+Alt+Q`：立即中断并停止当前播放的语音朗读。
    *   `Ctrl+Alt+M`：快速开启/停止自动轮询读屏。
*   **🛸 桌面悬浮极简条 (Floating Widget)**：
    *   极简微圆角透明卡片悬浮于屏幕顶角，可任意拖拽，方便在打游戏、看视频或编程时轻量化监控状态并触发按键。

---

## 📁 目录结构与架构设计

```text
ailook-ds/
├── README.md                 # 本手册与系统指南
├── requirements.txt          # 核心依赖清单 (PySide6, mss, Pillow, edge-tts, pyttsx3, requests, pygame)
├── start_ailook.bat          # Windows 11 极速一键启动脚本 (自动检查并加载环境)
├── install_env.bat           # Windows 11 虚拟环境 venv 与依赖包一键配置脚本
├── build_exe.bat             # 一键调用 PyInstaller 打包成 Windows 11 单文件应用程序
├── build.py                  # Python 构建和依赖打包引擎
├── config.json               # 自动生成和维护持久化的用户参数数据库
├── main.py                   # 应用程序主入口 (配置高 DPI 缩放与异常处理)
├── core/                     # 业务处理与逻辑引擎核心
│   ├── config_manager.py     # 线程安全 RLock 配置读写引擎
│   ├── screen_capture.py     # 跨平台/跨显示器高效捕获与缩放转码模块
│   ├── vision_engine.py      # OpenAI 兼容协议与 Ollama 原生协议推理引擎
│   ├── tts_engine.py         # 4模态语音合成调度引擎 (Edge/PyTTSX3/OpenAI/Custom)
│   ├── worker_thread.py      # 异步 QThread 流水线与轮询控制线程
│   └── log_manager.py        # 日志流分发与识别历史记录落盘管理
├── ui/                       # Windows 11 Fluent Design 原生图形界面库
│   ├── styles.py             # Win11 深色/浅色 QSS 样式及卡片主题表
│   ├── main_window.py        # 主界面框架与 DetachedWindow 独立分离窗控制器
│   ├── preview_page.py       # 【独立分离页】实时抓捕与解说展示控制页
│   ├── settings_page.py      # 【独立分离页】参数、模型、语速与提示词设置页
│   ├── logs_page.py          # 【独立分离页】流式运行日志与历史溯源页
│   └── floating_widget.py    # 【桌面悬浮条】微圆角可拖放悬浮控制卡片
└── utils/                    # 辅助通用工具组件
    ├── audio_player.py       # 跨平台临时音频文件/字节流回放驱动 (支持无声卡保护)
    └── shortcut_handler.py   # Windows 快捷键与热键调度处理组件
```

---

## 🚀 快速启动与部署 (Windows 11)

### 方法一：直接运行源码 (推荐开发者和普通用户)
1. 确保您的电脑已安装 **Python 3.10** 或以上版本（安装时请勾选 `Add Python to PATH`）。
2. 在项目根目录下，双击运行 **`install_env.bat`**。该脚本会自动创建 Python 虚拟环境并安装全部关键依赖（`PySide6`, `mss`, `Pillow`, `edge-tts` 等）。
3. 安装完成后，双击 **`start_ailook.bat`** 即可瞬间启动 AI Look 主程序界面及系统托盘！

### 方法二：一键打包为 Windows 11 独立 EXE 安装应用
若需要生成脱离 Python 环境运行的独立 `.exe`：
1. 双击运行 **`build_exe.bat`**。
2. 脚本将自动调用 `PyInstaller`，对模块与静态文件进行无缝编译。
3. 打包成功后，在 `dist/AILook_Desktop_System/` 文件夹下即可找到 **`AILook_Desktop_System.exe`**，直接拷贝或创建快捷方式发送至桌面运行即可。

---

## 💡 配置与指引小提示

### 1. 接入本地私有 AI (Ollama / LLaVA / Qwen2-VL)
1. 在 Windows 11 打开 CMD 或 Terminal，运行 `ollama run llava:13b` 或 `ollama run qwen2-vl:7b`。
2. 打开 AI Look 设置页 -> 切换至 **【🤖 AI 视觉大模型配置】** 选项卡 -> 选择 **【本地 AI 部署 (Local Ollama / LocalAI)】**。
3. 确认网址填写为 `http://localhost:11434/v1`，模型名称写为 `llava:13b`，点击保存生效即可实现全离线桌面识别。

### 2. 切换提示词场景模板
在设置页 **【✏️ 自定义提示词与场景】** 选项卡中，系统已为您内置了 5 大精选场景模板：
*   ✅ **默认视障读屏模式**：简短自然、专注核心要点与软件状态，适合语音播报。
*   💼 **软件与工作状态分析**：细致梳理办公软件进度、浏览器页面及待办事宜。
*   💻 **代码语法与排错助手**：分析代码编辑器报错堆栈，直接用口语指出具体报错原因和解决建议。
*   📰 **网页与文档快速摘要**：自动提炼长篇 PDF / 文章的前 3 个核心论点。
*   🌐 **实时英中双语口语翻译**：精准将屏幕中央英文对白与菜单口语化翻译解说为中文。
您可以从下拉列表选择并一键填入上方文本区域，或者随意修改内容后点击保存！

---

## 常见问题解答 (FAQ)
*   **Q: 为什么启动后没有声音播放？**
    *   A: 默认系统采用微软云端自然语音 `edge-tts`。若网络波动导致合成超时，建议在设置页把引擎切换为 `pyttsx3`（Windows 本地离线 SAPI5 引擎），即可即刻发音！
*   **Q: 如何将分离出来的三个独立窗口放回主程序？**
    *   A: 直接点击独立窗口标题栏右侧关闭按钮、或点击各窗口中的 **【↙ 归位至主界面】** 按钮，甚至在主界面侧边栏点击 **【📦 全部合并至主界面】** 即可一次性将所有独立窗口重组为单窗口模式。
