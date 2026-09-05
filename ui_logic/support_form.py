from .base_form import Form
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class SupportForm(Form):

    def __init__(self,base_form):
        super().__init__(base_form)
        # set form title
        self.setWindowTitle("الدعم الفني")

        self.set_icon("logo_btn", "modeer_logo.png")
        self.set_icon("whatsapp_btn", "whatsapp.svg")
        self.set_icon("web_btn", "web.svg")
        self.set_icon("cancel_btn", "cancel.svg")
        
        