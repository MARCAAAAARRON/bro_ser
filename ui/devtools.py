from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView


class DevToolsWindow(QMainWindow):
    def __init__(self, target_browser, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Developer Tools")
        self.setGeometry(150, 150, 950, 650)

        self.devtools_view = QWebEngineView()
        self.setCentralWidget(self.devtools_view)

        # Link target page to devtools view
        target_browser.page().setDevToolsPage(self.devtools_view.page())

        # If target tab closes/destroys, close this window safely
        target_browser.destroyed.connect(self.close)
