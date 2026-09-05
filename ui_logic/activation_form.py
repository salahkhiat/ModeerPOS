from .base_form import Form
from PyQt6.QtWidgets import QLineEdit, QLabel, QPushButton
import logging
import subprocess
import hashlib
import json
from fernet import Fernet
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ActivationForm(Form):
    # APP KEY
    KEY = b"bW8k0iO_bekfUW-e90nuxzKRr5dx6Bn1J0DsXNSKWAo="
    cipher = Fernet(KEY)

    def __init__(self,base_form):
        super().__init__(base_form)
        # set form title
        self.setWindowTitle("تفعيل البرنامج")
        sensetive_data = self.get_decrypted_data()

        if sensetive_data['activated'] == False:
            self.set_icon("status_btn", "unactive.svg")
            self.ui.apply_btn.clicked.connect(self.check_activation)

        elif sensetive_data['activated'] == True:
            self.ui.serial.setText(self.expected_serial())
            self.succeeded_status()

        self.set_icon("cancel_btn", "cancel.svg")
        self.set_icon("apply_btn", "apply.svg")

        machine_id_field: QLineEdit = self.ui.user_id
        machine_id_field.setText(f"{self.get_machine_id()}")
        machine_id_field.setReadOnly(True)

        print(self.expected_serial())

    def write_encrypted_data(self, data):
        """put data as json in an encrypted file"""
        json_text = json.dumps(data)
        encrypted = self.cipher.encrypt(json_text.encode())
        with open("file_mgr.dat", "wb") as file:
            file.write(encrypted)
    
    def get_decrypted_data(self) -> dict:
        with open("file_mgr.dat", "rb") as file:
            encrypted = file.read()
        decrypted = self.cipher.decrypt(encrypted)
        data = json.loads(decrypted.decode())
        return data 

    def get_machine_id(self) -> str:
        """ Returns MD5 hashed disk serial """
        result = subprocess.check_output(
            "wmic diskdrive get serialnumber",
            shell=True,
            text=True
        )
        disk_serial = result.split()[1].strip()
        machine_id = hashlib.md5(
            disk_serial.encode()
        ).hexdigest()

        return str(machine_id)
    
    def expected_serial(self):
        "Returns the expected serial"
        app_key = self.KEY.decode()
        machine_id = self.get_machine_id()

        expected_serial = f"{app_key}{machine_id}"

        hashed_serial = hashlib.md5(
            expected_serial.encode()
        ).hexdigest()

        return hashed_serial
    
    def check_activation(self):
        serial_field: QLineEdit = self.ui.serial
        error_msg: QLabel = self.ui.message
        if len(serial_field.text()) == 0:
            error_msg.setText("أدخل مفتاح التفعيل من فضلك")
            error_msg.setStyleSheet("color:orange;")
            return False
        
        elif len(serial_field.text()) > 0:
            entered_serial = serial_field.text().strip()

            if entered_serial != self.expected_serial():
                error_msg.setText("مفتاح التفعيل غير صالح")
                error_msg.setStyleSheet("color:red;")
                return False

            elif entered_serial == self.expected_serial():
                # Get old data
                data = self.get_decrypted_data()
                
                # Activate the app
                data['activated'] = True 
                self.write_encrypted_data(data)
            
                # change the UI status
                self.succeeded_status()

                return True

    def succeeded_status(self):
        serial_field: QLineEdit = self.ui.serial
        serial_field.setReadOnly(True)

        error_msg: QLabel = self.ui.message
        error_msg.setText("المفتاح صحيح")
        error_msg.setStyleSheet("color:green;")

        status_label: QLabel = self.ui.status_text
        status_label.setText("تم تفعيل البرنامج")

        self.set_icon("status_btn", "activated.svg")
        
        apply_btn: QPushButton = self.ui.apply_btn
        apply_btn.setDisabled(True)



        
        