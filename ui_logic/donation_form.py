from .base_form import Form
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class DonationForm(Form):

    def __init__(self,base_form):
        super().__init__(base_form)
        # set form title
        self.setWindowTitle("إدعم المطور")

        self.set_icon("developer_photo_btn", "developer.png")
        self.set_icon("baridi_mob_btn", "baridi_mob.png")
        self.set_icon("cancel_btn", "cancel.svg")
        
        