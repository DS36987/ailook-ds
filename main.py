import sys
import os
import traceback
import time

# 先确保日志目录存在以记录任何潜在崩溃
os.makedirs("logs", exist_ok=True)
CRASH_LOG = os.path.join("logs", f"crash_{time.strftime('%Y%m%d_%H%M%S')}.log")

def log_crash(msg: str):
    print(f"\n[AI Look 致命异常] {msg}", file=sys.stderr)
    try:
        with open(CRASH_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

def global_exception_hook(exctype, value, tb):
    err_msg = "".join(traceback.format_exception(exctype, value, tb))
    log_crash(err_msg)
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        if QApplication.instance():
            QMessageBox.critical(None, "AI Look 系统发生异常退出", f"运行中捕捉到未处理异常：\n\n{err_msg[:600]}\n\n详细日志已保存至: {CRASH_LOG}")
    except Exception:
        pass
    sys.exit(1)

sys.excepthook = global_exception_hook

def main():
    print("==================================================")
    print("     正在初始化 AI Look Desktop System (Win11)")
    print("==================================================")
    
    # 启用高 DPI 自动缩放支持 (Windows 11 Retina / 4K / High DPI 下最佳体验)
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    # 如果 Windows 下由于显卡驱动兼容问题导致 PySide6 闪退，可尝试开启软件渲染
    # os.environ["QT_QUICK_BACKEND"] = "software"

    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication, QMessageBox
    except ImportError as e:
        err = f"无法导入 GUI 引擎库 PySide6: {e}\n请确认已执行 `install_env.bat` 或在命令行运行: pip install PySide6 mss Pillow requests edge-tts pyttsx3 pygame pydantic"
        log_crash(err)
        return

    app = QApplication(sys.argv)
    app.setApplicationName("AI Look Desktop System")
    app.setOrganizationName("AILook")

    try:
        from core.config_manager import ConfigManager
        from ui.styles import get_theme_qss
        from ui.main_window import MainWindow

        cfg = ConfigManager()
        theme = cfg.get("app", "theme", default="dark")
        app.setStyleSheet(get_theme_qss(theme))

        print("[Main] 正在构造主程序窗口与独立窗口控制器...")
        window = MainWindow()
        window.show()
        print("[Main] 系统启动完毕，欢迎使用！")
    except Exception as e:
        err_msg = f"系统初始化及构造界面时发生异常:\n{traceback.format_exc()}"
        log_crash(err_msg)
        try:
            QMessageBox.critical(None, "AI Look 启动失败", err_msg)
        except Exception:
            pass
        return

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
