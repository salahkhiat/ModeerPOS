from .base_form import Form
from PyQt6.QtWidgets import QComboBox, QLineEdit
from PyQt6.QtCore import pyqtSignal
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class LoginForm(Form):
    logged_in_process = pyqtSignal(bool)
    def __init__(self,base_form):
        super().__init__(base_form)
        # set form title
        self.setWindowTitle("تسجيل الدخول")

        self.remove_title_bar()
        self.set_icon("logo", "modeer_logo.png")
        self.set_icon("cancel_btn", "cancel_2.svg")
        self.set_icon("login_btn", "login.svg")

        # default info
        self.users: dict = {
            0: "seller",
            1: "admin" 
        }

        self.ui.login_btn.clicked.connect(
            self.check_logged_in_credentials
        )

        self.ui.cancel_btn.clicked.connect(
            lambda: self.logged_in_process.emit(False)
        )
        


    def get_logged_in_info(self):
        user_idx: QComboBox = self.ui.users.currentIndex()
        password: QLineEdit = str(self.ui.password.text()).strip()
        logged_in: dict = {
            "user": self.users[user_idx],
            "password": password
        }
        

        return logged_in 

    def check_logged_in_credentials(self):

        # get the username and password from the Login Window.
        user = self.get_logged_in_info()["user"]
        password = self.get_logged_in_info()["password"]

        # Get the secure information from the encrypted file.
        secure_information = self.get_decrypted_information()

        # Get the inner users dictionary from the secure information file.
        inner_users = secure_information["users"]
        
        if inner_users[user] == password:
        
            self.logged_in_process.emit(True)
            # Update the secure information file to include the logged-in user.
            secure_information["logged-in"]= user
            self.update_encrypted_information(secure_information)
            
            self.close()
            
        else:
            
            self.ui.password_err.setText("كلمة المرور خطأ")
            


        

    

    

        

        
