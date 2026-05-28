import sys
import os
import logging
from PyQt6.QtWidgets import QApplication

from browser.window import BroSerWindow
from ui import themes

def setup_logging():
    # Make sure 'data' directory exists
    os.makedirs("data", exist_ok=True)
    
    # Format and configure the root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] (%(name)s) %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("data/bro-ser.log", encoding='utf-8')
        ]
    )
    logger = logging.getLogger("BroSer.Main")
    logger.info("========================================")
    logger.info("Bro-ser web browser starting up...")
    logger.info("========================================")

def main():
    setup_logging()
    logger = logging.getLogger("BroSer.Main")
    
    try:
        # Fix Windows Taskbar Icon explicitly setting AppUserModelID
        try:
            import ctypes
            myappid = 'antigravity.broser.browser.v1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            logger.info("Windows AppUserModelID registered explicitly for taskbar icon.")
        except Exception as e:
            logger.debug(f"Non-windows environment or failed SetCurrentProcessExplicitAppUserModelID: {e}")

        app = QApplication(sys.argv)
        
        # Apply Dark Theme using absolute assets path to ensure dynamic resources resolve in PyInstaller
        root_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(root_dir, 'assets')
        app.setStyleSheet(themes.get_dark_theme(assets_dir))
        logger.info("Dark UI theme style sheets applied successfully.")

        window = BroSerWindow()
        window.show()
        logger.info("Main browser window spawned and rendered.")

        exit_code = app.exec()
        logger.info(f"Browser application exited clean with code {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.critical(f"Unhandled crash on main thread during runtime: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()