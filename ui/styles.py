# Windows 11 Fluent Design QSS 样式库与色彩管理器

WIN11_DARK_QSS = """
* {
    font-family: "Segoe UI Variable Display", "Microsoft YaHei UI", "Segoe UI", sans-serif;
    font-size: 13px;
    color: #FFFFFF;
}

QMainWindow, QDialog, QWidget#MainContainer, QWidget#WindowPage {
    background-color: #202020;
}

QWidget#Sidebar {
    background-color: #282828;
    border-right: 1px solid #383838;
}

/* 导航按键 */
QPushButton.NavButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 10px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 500;
    color: #CCCCCC;
}
QPushButton.NavButton:hover {
    background-color: #333333;
    color: #FFFFFF;
}
QPushButton.NavButton[active="true"] {
    background-color: #383838;
    color: #60CDFF;
    font-weight: bold;
    border-left: 3px solid #60CDFF;
}

/* 卡片容器 */
QFrame.Card, QGroupBox {
    background-color: #2B2B2B;
    border: 1px solid #383838;
    border-radius: 8px;
    padding: 12px;
    margin-top: 6px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #60CDFF;
    font-weight: 600;
}

/* 普通按钮 */
QPushButton {
    background-color: #333333;
    border: 1px solid #454545;
    border-radius: 6px;
    padding: 6px 14px;
    color: #FFFFFF;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #3C3C3C;
    border-color: #555555;
}
QPushButton:pressed {
    background-color: #2D2D2D;
    color: #AAAAAA;
}

/* 主色调重要按钮 (Accent Button) */
QPushButton.AccentButton {
    background-color: #0078D4;
    border: 1px solid #0086E4;
    color: #FFFFFF;
    font-weight: 600;
}
QPushButton.AccentButton:hover {
    background-color: #1A86DA;
}
QPushButton.AccentButton:pressed {
    background-color: #006CBE;
}

/* 危险/警告按钮 */
QPushButton.DangerButton {
    background-color: #C42B1C;
    border: 1px solid #D13426;
    color: #FFFFFF;
}
QPushButton.DangerButton:hover {
    background-color: #D13426;
}

/* 输入框与选择框 */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #1E1E1E;
    border: 1px solid #3E3E3E;
    border-radius: 6px;
    padding: 6px 10px;
    color: #FFFFFF;
    selection-background-color: #0078D4;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #60CDFF;
    background-color: #1A1A1A;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #2D2D2D;
    border: 1px solid #454545;
    selection-background-color: #0078D4;
    border-radius: 6px;
}

/* 表格与树形/列表组件 */
QTableWidget, QListWidget {
    background-color: #1E1E1E;
    border: 1px solid #383838;
    border-radius: 6px;
    gridline-color: #333333;
}
QHeaderView::section {
    background-color: #2D2D2D;
    border: none;
    border-bottom: 1px solid #454545;
    padding: 6px;
    font-weight: bold;
    color: #DDDDDD;
}

/* 进度条与滑动条 */
QProgressBar {
    background-color: #1E1E1E;
    border: 1px solid #383838;
    border-radius: 4px;
    text-align: center;
    color: #FFFFFF;
}
QProgressBar::chunk {
    background-color: #0078D4;
    border-radius: 3px;
}

/* 标签选项卡 (TabWidget) */
QTabWidget::pane {
    border: 1px solid #383838;
    background-color: #2B2B2B;
    border-radius: 6px;
}
QTabBar::tab {
    background-color: #202020;
    color: #AAAAAA;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 4px;
}
QTabBar::tab:selected {
    background-color: #2B2B2B;
    color: #60CDFF;
    font-weight: bold;
    border-bottom: 2px solid #60CDFF;
}
QTabBar::tab:hover:!selected {
    background-color: #282828;
    color: #EEEEEE;
}
"""

WIN11_LIGHT_QSS = """
* {
    font-family: "Segoe UI Variable Display", "Microsoft YaHei UI", "Segoe UI", sans-serif;
    font-size: 13px;
    color: #1A1A1A;
}

QMainWindow, QDialog, QWidget#MainContainer, QWidget#WindowPage {
    background-color: #F3F3F3;
}

QWidget#Sidebar {
    background-color: #E8E8E8;
    border-right: 1px solid #D1D1D1;
}

QPushButton.NavButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 10px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 500;
    color: #555555;
}
QPushButton.NavButton:hover {
    background-color: #DCDCDC;
    color: #000000;
}
QPushButton.NavButton[active="true"] {
    background-color: #FFFFFF;
    color: #0078D4;
    font-weight: bold;
    border-left: 3px solid #0078D4;
}

QFrame.Card, QGroupBox {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 12px;
    margin-top: 6px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #0078D4;
    font-weight: 600;
}

QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 6px;
    padding: 6px 14px;
    color: #222222;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #F5F5F5;
    border-color: #AAAAAA;
}

QPushButton.AccentButton {
    background-color: #0078D4;
    border: 1px solid #006CBE;
    color: #FFFFFF;
    font-weight: 600;
}
QPushButton.AccentButton:hover {
    background-color: #1A86DA;
}

QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 6px;
    padding: 6px 10px;
    color: #1A1A1A;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #0078D4;
}

QTableWidget, QListWidget {
    background-color: #FFFFFF;
    border: 1px solid #DDDDDD;
    border-radius: 6px;
}
QHeaderView::section {
    background-color: #F0F0F0;
    border: none;
    border-bottom: 1px solid #CCCCCC;
    padding: 6px;
    font-weight: bold;
    color: #333333;
}

QTabWidget::pane {
    border: 1px solid #DDDDDD;
    background-color: #FFFFFF;
    border-radius: 6px;
}
QTabBar::tab {
    background-color: #EBEBEB;
    color: #555555;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 4px;
}
QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #0078D4;
    font-weight: bold;
    border-bottom: 2px solid #0078D4;
}
"""

def get_theme_qss(theme: str = "dark") -> str:
    if theme.lower() == "light":
        return WIN11_LIGHT_QSS
    return WIN11_DARK_QSS
