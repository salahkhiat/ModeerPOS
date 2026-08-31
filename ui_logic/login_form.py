from .base_form import Form
from PyQt6.QtWidgets import QComboBox, QLineEdit
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class LoginForm(Form):
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
            lambda: print(self.get_login_info())
        )
        


    def get_login_info(self):
        user_idx: QComboBox = self.ui.users.currentIndex()
        password: QLineEdit = str(self.ui.password.text()).strip()
        logged_in: dict = {
            "user": self.users[user_idx],
            "password": password
        }
        
        return logged_in

    

    

        

        
