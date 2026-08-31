from .base_form import Form
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
