import os
import logging
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo

logger = logging.getLogger("BroSer.AdBlocker")

class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.rules_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'config',
            'adblock_rules.txt'
        )
        self.blocked_domains = set()
        self.default_domains = [
            "doubleclick.net", "googleadservices.com", "googlesyndication.com",
            "adservice.google.com", "adnxs.com", "adtech.de", "advertising.com",
            "adform.net", "adroll.com", "adzerk.net", "scorecardresearch.com",
            "ads.youtube.com", "telemetry", "analytics"
        ]
        self._load_rules()

    def _load_rules(self):
        """Loads blocked domains from rules file, or writes the default if not present."""
        os.makedirs(os.path.dirname(self.rules_path), exist_ok=True)
        if not os.path.exists(self.rules_path):
            try:
                with open(self.rules_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(self.default_domains) + "\n")
                logger.info("Created default adblock rules file.")
            except Exception as e:
                logger.error(f"Failed to create default adblock rules file: {e}", exc_info=True)
        
        # Read the file
        try:
            if os.path.exists(self.rules_path):
                with open(self.rules_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        domain = line.strip().lower()
                        # Ignore comments or empty lines
                        if domain and not domain.startswith('#'):
                            self.blocked_domains.add(domain)
                logger.info(f"Loaded {len(self.blocked_domains)} adblock/tracker rules.")
        except Exception as e:
            logger.error(f"Failed to read adblock rules file: {e}", exc_info=True)
            # Fallback to defaults
            self.blocked_domains = set(self.default_domains)

    def interceptRequest(self, info):
        # Only block if ad filtering is enabled in config
        if not self.config.get("block_ads"):
            return

        # Do not block main frame navigation (if user explicitly navigates to the page)
        try:
            if info.resourceType() == QWebEngineUrlRequestInfo.ResourceType.ResourceTypeMainFrame:
                return
        except Exception:
            pass

        qurl = info.requestUrl()
        host = qurl.host().lower()
        if not host:
            return

        # Perform fast O(1) set checks by decomposing the hostname suffixes
        # e.g. for "sub.doubleclick.net", check "sub.doubleclick.net", "doubleclick.net", "net"
        parts = host.split('.')
        for i in range(len(parts)):
            suffix = ".".join(parts[i:])
            if suffix in self.blocked_domains:
                info.block(True)
                logger.info(f"Blocked ad/tracker request: {host} (matched rule: {suffix})")
                return

