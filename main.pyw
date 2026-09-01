from PyQt6.QtWidgets import QApplication

from uis.main_screen import Ui_main_window as MainUi
from ui_logic.main_screen import MainScreen

from uis.activation import Ui_Dialog as ActivationUi
from ui_logic.activation_form import ActivationForm

from uis.login import Ui_Dialog as LoginUi
from ui_logic.login_form import LoginForm

import sys
import logging
from datetime import date
import json 
from fernet import Fernet
logging.basicConfig(
    filename='modeer_logs_file.log',
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s'
)

# APP KEY
KEY = b"bW8k0iO_bekfUW-e90nuxzKRr5dx6Bn1J0DsXNSKWAo="
cipher = Fernet(KEY)

# --- Global exception hook ---
def excepthook(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = excepthook
# --- 


def write_encrypted_data(data):
    """put data as json in an encrypted file"""
    json_text = json.dumps(data)
    encrypted = cipher.encrypt(json_text.encode())
    with open("file_mgr.dat", "wb") as file:
        file.write(encrypted)

def create_licence_file():
    """Create licence file with default values"""
    data = {
        "first_run": False,
        "first_run_date": f"{date.today()}",
        "activated": False
    }
    write_encrypted_data(data)


def check_activation() -> bool:
    with open("file_mgr.dat", "rb") as file:
        encrypted = file.read()
    decrypted = cipher.decrypt(encrypted)
    data = json.loads(decrypted.decode())
    activation = data['activated']
    first_run = data['first_run']
    

    
    if activation is not True:
        # 1- if this is the first run at all
        if first_run is True:
            new_data = {
                "first_run": False,
                "first_run_date": f"{date.today()}",
                "activated": False
            }
            write_encrypted_data(new_data)

        # 2- if ran it before
        elif first_run is False:
            # 1- check the days used.
                first_run_date = date.fromisoformat(data['first_run_date'])
                today = date.today()
                
                days_used = (today - first_run_date).days
            
                if days_used >= 30:
                    form = ActivationForm(ActivationUi)
                    form.exec()
                    return False
                else:
                    return True
    else:
        return True
    
LOGGED_IN = False

def check_credentials(logged_in):
    """ Valid credentials returns True, otherwise False. """
    global LOGGED_IN 
    LOGGED_IN = logged_in
    

def main():
    app = QApplication(sys.argv)
    form = LoginForm(LoginUi)
    form.logged_in_process.connect(check_credentials)
    form.exec()
   
    if not LOGGED_IN:
        return 
  
    activation = check_activation()
    if activation is not True:
        return

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

