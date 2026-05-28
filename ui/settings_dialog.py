from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QCheckBox, QPushButton, QMessageBox
)
from PyQt6.QtWebEngineCore import QWebEngineProfile


class SettingsDialog(QDialog):
    def __init__(self, config_manager, history_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.history_manager = history_manager

        self.setWindowTitle("Settings")
        self.setMinimumSize(400, 300)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Homepage configuration
        home_layout = QHBoxLayout()
        home_layout.addWidget(QLabel("Homepage URL:"))
        self.homepage_input = QLineEdit()
        self.homepage_input.setObjectName("settingsInput")
        home_layout.addWidget(self.homepage_input)
        layout.addLayout(home_layout)

        # Private mode by default
        self.private_checkbox = QCheckBox("Open new tabs in Private Mode by default")
        self.private_checkbox.setObjectName("settingsCheckbox")
        layout.addWidget(self.private_checkbox)

        # Basic Ad blocking placeholder (Phase 8 support groundwork)
        self.adblock_checkbox = QCheckBox("Enable Basic Ad Filtering")
        self.adblock_checkbox.setObjectName("settingsCheckbox")
        layout.addWidget(self.adblock_checkbox)

        layout.addStretch()

        # Clear browsing data button
        self.clear_data_btn = QPushButton("Clear All Browsing Data")
        self.clear_data_btn.setObjectName("dangerBtn")
        self.clear_data_btn.clicked.connect(self._clear_browsing_data)
        layout.addWidget(self.clear_data_btn)

        # Dialog buttons (Save / Cancel)
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.clicked.connect(self._save_settings)
        buttons_layout.addWidget(self.save_btn)

        layout.addLayout(buttons_layout)

    def _load_settings(self):
        self.homepage_input.setText(self.config_manager.get("homepage"))
        self.private_checkbox.setChecked(self.config_manager.get("private_mode_by_default"))
        self.adblock_checkbox.setChecked(self.config_manager.get("block_ads"))

    def _save_settings(self):
        homepage = self.homepage_input.text().strip()
        if homepage:
            if not homepage.startswith("http"):
                homepage = "https://" + homepage
            self.config_manager.set("homepage", homepage)
        
        self.config_manager.set("private_mode_by_default", self.private_checkbox.isChecked())
        self.config_manager.set("block_ads", self.adblock_checkbox.isChecked())
        
        self.accept()

    def _clear_browsing_data(self):
        confirm = QMessageBox.question(
            self, "Confirm Clear",
            "Are you sure you want to clear all history, cookies, and cache?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # 1. Clear SQL history
            self.history_manager.clear_history()
            
            # 2. Clear Qt HTTP cache & cookies
            default_profile = QWebEngineProfile.defaultProfile()
            default_profile.clearHttpCache()
            default_profile.cookieStore().deleteAllCookies()
            
            QMessageBox.information(
                self, "Success",
                "Browsing history, cookies, and cache cleared successfully!"
            )
