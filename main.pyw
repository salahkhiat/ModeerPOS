from PyQt6.QtWidgets import QApplication

from uis.main_screen import Ui_main_window as MainUi
from ui_logic.main_screen import MainScreen

import sys
import logging

logging.basicConfig(
    filename='modeer_logs_file.log',
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s'
)

# --- Global exception hook ---
def excepthook(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = excepthook
# --- 

def main():
    app = QApplication(sys.argv)

    # Show splash(welcome screen) first; MainScreen will open after duration
    splash = MainScreen.show_welcome_screen(
        app,
        base_form_class=MainUi,
        image_path="splash_screen.png",
        duration=2500,
        width=900,
        height=500
    )

    sys.exit(app.exec())

if __name__ == "__main__": 
    main()

