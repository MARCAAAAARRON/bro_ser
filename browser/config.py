import os
import json
import logging

logger = logging.getLogger("BroSer.Config")

class ConfigManager:
    def __init__(self):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_dir = os.path.join(root_dir, 'config')
        os.makedirs(config_dir, exist_ok=True)
        self.config_path = os.path.join(config_dir, 'settings.json')
        
        self.defaults = {
            "homepage": "https://www.google.com",
            "private_mode_by_default": False,
            "block_ads": False
        }
        self.settings = {}
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                logger.info("Configuration settings loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to parse settings.json (loading defaults): {e}", exc_info=True)
                self.settings = self.defaults.copy()
        else:
            logger.info("settings.json not found. Creating new configuration with default settings.")
            self.settings = self.defaults.copy()
            self.save()

    def save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
            logger.info("Configuration settings saved successfully.")
        except Exception as e:
            logger.error(f"Failed to write settings.json to disk: {e}", exc_info=True)

    def get(self, key, default=None):
        return self.settings.get(key, default if default is not None else self.defaults.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save()

