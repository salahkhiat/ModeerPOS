from .base_form import Form
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ActivationForm(Form):

    def __init__(self,base_form):
        super().__init__(base_form)
        # set form title
        self.setWindowTitle("تفعيل البرنامج")

        self.set_icon("status_btn", "unactive.svg")
        self.set_icon("cancel_btn", "cancel.svg")
        self.set_icon("apply_btn", "apply.svg")
        
        