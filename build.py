import os
import sys
import subprocess

def build_windows_exe():
    print("======================================================")
    print("      AI Look Desktop System - Windows 11 EXE 打包程序")
    print("======================================================")
    
    # 检查并安装 pyinstaller
    try:
        import PyInstaller
    except ImportError:
        print("[Build] 正在安装 PyInstaller 打包工具...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller>=6.0.0"])

    build_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "AILook_Desktop_System",
        "--noconfirm",
        "--windowed", # 无黑窗模式
        "--clean",
        "--add-data", f"README.md{os.pathsep}.",
        "--add-data", f"requirements.txt{os.pathsep}.",
        "--hidden-import", "PySide6",
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtGui",
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "PIL",
        "--hidden-import", "mss",
        "--hidden-import", "pyttsx3",
        "--hidden-import", "edge_tts",
        "--hidden-import", "pygame",
        "--hidden-import", "requests",
        "--hidden-import", "pydantic",
        "main.py"
    ]

    print("[Build] 开始打包 EXE... (此过程大约需要 1-3 分钟)")
    res = subprocess.call(build_cmd)
    if res == 0:
        print("\n✅ 打包成功！独立运行应用位于: dist/AILook_Desktop_System/AILook_Desktop_System.exe")
    else:
        print("\n❌ 打包过程出现异常，请检查控制台错误日志。")

if __name__ == "__main__":
    build_windows_exe()
