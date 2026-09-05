from .base_form import Form
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ErrorForm(Form):
    def __init__(self,base_form,msg=""):
        super().__init__(base_form)
        self.setWindowTitle(msg)
        self.ui.err_msg.setText(msg)
        # set icons
        self.set_icon("error_btn","error.svg")
        
        


