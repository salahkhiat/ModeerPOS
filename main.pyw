from PyQt6.QtWidgets import QApplication, QLineEdit

from uis.main_screen import Ui_main_window as MainUi
from ui_logic.main_screen import MainScreen

from uis.activation import Ui_Dialog as ActivationUi
from ui_logic.activation_form import ActivationForm

import sys
import logging
from datetime import date
import json 
from fernet import Fernet
import hashlib
import subprocess
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




def get_machine_id() -> str:
    """ Returns MD5 hashed disk serial """
    result = subprocess.check_output(
        "wmic diskdrive get serialnumber",
        shell=True,
        text=True
    )
    disk_serial = result.split()[1]
    machine_id = hashlib.md5(
        disk_serial.encode()
    ).hexdigest()

    return str(machine_id)

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
            
                if days_used > 7:
                    form = ActivationForm(ActivationUi)
                    machine_id_field: QLineEdit = form.ui.user_id
                    machine_id_field.setText(f"{get_machine_id()}")
                    machine_id_field.setReadOnly(True)
                    form.exec()
                    return False
                else:
                    return True
    else:
        return True
    
    

def main():

    
    app = QApplication(sys.argv)
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

