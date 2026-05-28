import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QTabBar, QToolButton, QMenu
)
from PyQt6.QtGui import QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtCore import QUrl, pyqtSignal, Qt
from browser.history import HistoryManager

logger = logging.getLogger("BroSer.Tabs")



class BroSerTabWidget(QWidget):
    active_url_changed = pyqtSignal(str)
    active_title_changed = pyqtSignal(str)
    tab_state_changed = pyqtSignal()

    def __init__(self, adblocker=None, parent=None):
        super().__init__(parent)

        self.adblocker = adblocker
        self.history_manager = HistoryManager()
        self.private_profile = None
        self.browsers = []  # Keep references to browser widgets

        # ── Main vertical layout: TabStrip → Toolbar (injected) → Content ──
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # ── Tab strip (QTabBar + "+" button) ──
        self.tab_strip = QWidget()
        self.tab_strip.setObjectName("tabStrip")
        strip_layout = QHBoxLayout(self.tab_strip)
        strip_layout.setContentsMargins(8, 4, 8, 0)
        strip_layout.setSpacing(0)

        self.tab_bar = QTabBar()
        self.tab_bar.setObjectName("chromeTabBar")
        self.tab_bar.setTabsClosable(True)
        self.tab_bar.setMovable(True)
        self.tab_bar.setExpanding(False)
        self.tab_bar.setDrawBase(False)
        self.tab_bar.currentChanged.connect(self.on_current_changed)
        self.tab_bar.tabCloseRequested.connect(self.close_tab)
        strip_layout.addWidget(self.tab_bar)

        # "+" new tab button
        self.add_tab_btn = QToolButton()
        self.add_tab_btn.setObjectName("addTabBtn")
        self.add_tab_btn.setText("+")
        self.add_tab_btn.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.add_tab_btn.clicked.connect(lambda: self.add_new_tab())

        menu = QMenu(self)
        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(lambda: self.add_new_tab())
        new_private_action = QAction("New Private Tab 🕶️", self)
        new_private_action.triggered.connect(lambda: self.add_new_tab(is_private=True))
        menu.addAction(new_tab_action)
        menu.addAction(new_private_action)
        self.add_tab_btn.setMenu(menu)
        strip_layout.addWidget(self.add_tab_btn)
        strip_layout.addStretch()

        self.main_layout.addWidget(self.tab_strip)

        # ── Toolbar placeholder (injected by window.py via set_toolbar) ──
        self.toolbar_placeholder = None

        # ── Content stack ──
        self.stack = QStackedWidget()
        self.stack.setObjectName("browserStack")
        self.main_layout.addWidget(self.stack)

    def set_toolbar(self, toolbar):
        """Inject the navigation toolbar between the tab strip and the content area."""
        self.toolbar_placeholder = toolbar
        # Insert at index 1 (after tab_strip, before stack)
        self.main_layout.insertWidget(1, toolbar)

    def add_new_tab(self, url_str="https://www.google.com", is_private=False):
        browser = QWebEngineView()
        browser.is_private = is_private

        if is_private:
            if not self.private_profile:
                # Creates a secure off-the-record profile in PyQt6
                self.private_profile = QWebEngineProfile(self)
                self.private_profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)
                self.private_profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
                self.private_profile.setHttpCacheMaximumSize(50 * 1024 * 1024)  # 50MB Memory cache max
                logger.info("Initialized secure memory-only off-the-record private profile.")
                if self.adblocker:
                    self.private_profile.setUrlRequestInterceptor(self.adblocker)
            page = QWebEnginePage(self.private_profile, browser)
            browser.setPage(page)

        browser.setUrl(QUrl(url_str))

        # Connect browser signals
        browser.urlChanged.connect(lambda qurl, b=browser: self.on_browser_url_changed(qurl, b))
        browser.titleChanged.connect(lambda title, b=browser: self.on_browser_title_changed(title, b))
        browser.loadFinished.connect(lambda _, b=browser: self.on_browser_load_finished(b))

        self.browsers.append(browser)
        self.stack.addWidget(browser)
        tab_label = "🕶️ New Tab" if is_private else "New Tab"
        i = self.tab_bar.addTab(tab_label)
        self.tab_bar.setCurrentIndex(i)
        self.tab_state_changed.emit()

    def close_tab(self, index):
        if self.tab_bar.count() < 2:
            return
        browser = self.browsers[index]
        self.tab_bar.removeTab(index)
        self.stack.removeWidget(browser)
        self.browsers.remove(browser)
        browser.deleteLater()
        self.tab_state_changed.emit()

    def count(self):
        return self.tab_bar.count()

    def widget(self, index):
        if 0 <= index < len(self.browsers):
            return self.browsers[index]
        return None

    def current_browser(self):
        index = self.tab_bar.currentIndex()
        if 0 <= index < len(self.browsers):
            return self.browsers[index]
        return None

    def on_current_changed(self, index):
        if 0 <= index < len(self.browsers):
            self.stack.setCurrentIndex(index)
            browser = self.browsers[index]
            self.active_url_changed.emit(browser.url().toString())
            is_private = getattr(browser, 'is_private', False)
            title = browser.title() or "New Tab"
            display_title = f"🕶️ {title}" if is_private else title
            self.active_title_changed.emit(display_title)
            self.tab_state_changed.emit()

    def on_browser_url_changed(self, qurl, browser):
        if browser == self.current_browser():
            self.active_url_changed.emit(qurl.toString())

    def on_browser_title_changed(self, title, browser):
        index = self.browsers.index(browser) if browser in self.browsers else -1
        is_private = getattr(browser, 'is_private', False)
        display_title = f"🕶️ {title}" if is_private else title
        if index != -1:
            short = display_title[:25] + "…" if len(display_title) > 25 else display_title
            self.tab_bar.setTabText(index, short)
        if browser == self.current_browser():
            self.active_title_changed.emit(display_title)

    def on_browser_load_finished(self, browser):
        title = browser.title()
        url = browser.url().toString()
        is_private = getattr(browser, 'is_private', False)
        display_title = f"🕶️ {title}" if is_private else title
        index = self.browsers.index(browser) if browser in self.browsers else -1
        if index != -1 and title:
            short = display_title[:25] + "…" if len(display_title) > 25 else display_title
            self.tab_bar.setTabText(index, short)
            if browser == self.current_browser():
                self.active_title_changed.emit(display_title)
        if not is_private and url and url != "about:blank":
            self.history_manager.add_visit(url, title or "")
        self.tab_state_changed.emit()

    # Navigation slots
    def back(self):
        if self.current_browser():
            self.current_browser().back()

    def forward(self):
        if self.current_browser():
            self.current_browser().forward()

    def reload(self):
        if self.current_browser():
            self.current_browser().reload()

    def go_home(self):
        pass

    def navigate(self, url_str):
        if self.current_browser():
            self.current_browser().setUrl(QUrl(url_str))
