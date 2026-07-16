import sys
import os
import traceback
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox
from core.config_manager import ConfigManager
from ui.styles import get_theme_qss
from ui.main_window import MainWindow

def main():
    # 启用高 DPI 自动缩放支持 (Windows 11 Retina / 4K / High DPI 下最佳体验)
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("AI Look Desktop System")
    app.setOrganizationName("AILook")

    # 从配置读取主题
    cfg = ConfigManager()
    theme = cfg.get("app", "theme", default="dark")
    app.setStyleSheet(get_theme_qss(theme))

    try:
        window = MainWindow()
        window.show()
    except Exception as e:
        err_msg = f"系统启动时发生未捕获异常:\n{traceback.format_exc()}"
        print(err_msg)
        try:
            QMessageBox.critical(None, "AI Look 启动失败", err_msg)
        except Exception:
            pass
        sys.exit(1)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
