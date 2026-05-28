import os

def get_dark_theme(assets_dir=None):
    if not assets_dir:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(os.path.dirname(current_dir), 'assets')
    
    close_xpm = os.path.join(assets_dir, "close.xpm").replace('\\', '/')
    
    css = """
    /* ── Window ── */
    QMainWindow {
        background-color: #202124;
    }

    /* ── Tab Strip Container ── */
    QWidget#tabStrip {
        background-color: #202124;
    }

    /* ── Tab Bar (Chrome-style rounded tabs) ── */
    QTabBar#chromeTabBar {
        background-color: transparent;
        border: none;
        qproperty-drawBase: 0;
    }

    QTabBar#chromeTabBar::tab {
        background-color: #35363a;
        color: #9aa0a6;
        padding: 7px 18px;
        margin-right: 1px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        border: none;
        min-width: 120px;
        max-width: 220px;
    }

    QTabBar#chromeTabBar::tab:selected {
        background-color: #292a2d;
        color: #e8eaed;
    }

    QTabBar#chromeTabBar::tab:hover:!selected {
        background-color: #3c4043;
    }

    QTabBar#chromeTabBar::close-button {
        image: url(PLACEHOLDER_CLOSE_XPM);
        subcontrol-position: right;
        border: none;
        border-radius: 4px;
        width: 16px;
        height: 16px;
    }

    QTabBar#chromeTabBar::close-button:hover {
        background-color: #ec5f5f;
    }


    /* ── "+" New Tab Button ── */
    QToolButton#addTabBtn {
        background-color: transparent;
        color: #9aa0a6;
        font-size: 18px;
        font-weight: bold;
        border: none;
        border-radius: 50%;
        padding: 4px 8px;
        margin-left: 4px;
    }

    QToolButton#addTabBtn:hover {
        background-color: #3c4043;
    }

    /* ── Navigation Toolbar ── */
    QToolBar {
        background-color: #292a2d;
        border: none;
        spacing: 4px;
        padding: 6px 8px;
    }

    /* ── Standard/Dialog Push Buttons ── */
    QPushButton {
        background-color: #35363a;
        color: #e8eaed;
        border: 1px solid #5f6368;
        border-radius: 4px;
        padding: 6px 16px;
        font-size: 13px;
        font-weight: normal;
    }

    QPushButton:hover {
        background-color: #3c4043;
    }

    QPushButton:pressed {
        background-color: #44474b;
    }

    QPushButton#saveBtn {
        background-color: #8ab4f8;
        color: #202124;
        font-weight: bold;
        border: none;
    }

    QPushButton#saveBtn:hover {
        background-color: #a8c7fa;
    }

    QPushButton#saveBtn:pressed {
        background-color: #7c9fe6;
    }

    /* ── Nav Buttons in Toolbar ── */
    QToolBar QPushButton {
        background-color: transparent;
        border: none;
        border-radius: 20px;
        padding: 6px;
    }

    QToolBar QPushButton:hover {
        background-color: #3c4043;
    }

    QToolBar QPushButton:pressed {
        background-color: #44474b;
    }

    /* ── URL / Omnibox ── */
    QLineEdit#urlBar {
        background-color: #35363a;
        color: #e8eaed;
        border: none;
        border-radius: 18px;
        padding: 6px 16px;
        font-size: 14px;
        selection-background-color: #8ab4f8;
        selection-color: #202124;
    }

    QLineEdit#urlBar:focus {
        background-color: #202124;
        border: 2px solid #8ab4f8;
    }

    /* ── Emoji Toolbar Buttons ── */
    QPushButton#bookmarkBtn,
    QPushButton#historyBtn,
    QPushButton#bookmarksBtn,
    QPushButton#downloadsBtn,
    QPushButton#settingsBtn,
    QPushButton#devtoolsBtn {
        font-size: 16px;
        padding: 5px 7px;
        min-width: 30px;
        border-radius: 20px;
    }

    /* ── Browser Content Stack ── */
    QStackedWidget#browserStack {
        background-color: #202124;
        border: none;
    }

    /* ── Dialogs ── */
    QDialog {
        background-color: #292a2d;
        color: #e8eaed;
        border-radius: 8px;
    }

    QListWidget {
        background-color: #202124;
        color: #e8eaed;
        border: 1px solid #3c4043;
        border-radius: 8px;
        padding: 4px;
        font-size: 13px;
    }

    QListWidget::item {
        padding: 10px;
        border-bottom: 1px solid #35363a;
        border-radius: 4px;
    }

    QListWidget::item:selected {
        background-color: #394457;
        color: #e8eaed;
    }

    QListWidget::item:hover {
        background-color: #35363a;
    }

    QLabel {
        color: #e8eaed;
        font-size: 14px;
        font-weight: bold;
    }

    /* ── Progress Bars ── */
    QProgressBar {
        background-color: #35363a;
        color: #e8eaed;
        border: none;
        border-radius: 4px;
        text-align: center;
        font-size: 11px;
        min-height: 14px;
        max-height: 14px;
    }

    QProgressBar::chunk {
        background-color: #8ab4f8;
        border-radius: 4px;
    }

    QLabel#downloadFilename {
        font-size: 13px;
        font-weight: bold;
        color: #e8eaed;
    }

    QLabel#downloadStatus {
        font-size: 12px;
        color: #8ab4f8;
        font-weight: normal;
    }

    QLabel#downloadSize {
        font-size: 11px;
        color: #9aa0a6;
        font-weight: normal;
    }

    /* ── Settings ── */
    QLineEdit#settingsInput {
        background-color: #35363a;
        color: #e8eaed;
        border: 1px solid #3c4043;
        border-radius: 4px;
        padding: 6px 10px;
        font-size: 13px;
    }

    QCheckBox {
        color: #e8eaed;
        font-size: 13px;
        spacing: 8px;
    }

    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border-radius: 3px;
        border: 2px solid #9aa0a6;
        background-color: transparent;
    }

    QCheckBox::indicator:checked {
        background-color: #8ab4f8;
        border-color: #8ab4f8;
    }

    QPushButton#dangerBtn {
        background-color: #c5221f;
        color: #ffffff;
        font-weight: bold;
        border: none;
        padding: 10px 20px;
        border-radius: 4px;
        font-size: 13px;
    }

    QPushButton#dangerBtn:hover {
        background-color: #ea4335;
    }

    QPushButton#dangerBtn:pressed {
        background-color: #9c1b18;
    }

    /* ── Menus ── */
    QMenu {
        background-color: #292a2d;
        color: #e8eaed;
        border: 1px solid #3c4043;
        border-radius: 8px;
        padding: 4px;
    }

    QMenu::item {
        padding: 8px 24px;
        border-radius: 4px;
    }

    QMenu::item:selected {
        background-color: #3c4043;
    }

    /* ── Message Boxes ── */
    QMessageBox {
        background-color: #292a2d;
        color: #e8eaed;
    }

    QMessageBox QPushButton {
        background-color: #3c4043;
        color: #e8eaed;
        padding: 6px 16px;
        border-radius: 4px;
        min-width: 70px;
    }

    QMessageBox QPushButton:hover {
        background-color: #44474b;
    }

    /* ── Scrollbars ── */
    QScrollBar:vertical {
        background: transparent;
        width: 8px;
    }

    QScrollBar::handle:vertical {
        background: #5f6368;
        border-radius: 4px;
        min-height: 30px;
    }

    QScrollBar::handle:vertical:hover {
        background: #9aa0a6;
    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0;
    }

    QScrollBar:horizontal {
        background: transparent;
        height: 8px;
    }

    QScrollBar::handle:horizontal {
        background: #5f6368;
        border-radius: 4px;
    }

    QScrollBar::handle:horizontal:hover {
        background: #9aa0a6;
    }

    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {
        width: 0;
    }
    """
    return css.replace("PLACEHOLDER_CLOSE_XPM", close_xpm)
