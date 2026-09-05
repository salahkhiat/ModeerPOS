from .base_form import Form
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ContactUsForm(Form):

    def __init__(self,base_form):
        super().__init__(base_form)
        # set form title
        self.setWindowTitle("تواصل معنا")

        self.set_icon("logo_btn", "modeer_logo.png")
        self.set_icon("whatsapp_btn", "whatsapp.svg")
        self.set_icon("youtube_btn", "youtube.svg")
        self.set_icon("cancel_btn", "cancel.svg")
        
        