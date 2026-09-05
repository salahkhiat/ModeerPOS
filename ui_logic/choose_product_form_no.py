from .base_form import Form

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ChooseProductForm(Form):

    def __init__(self,base_form):
        super().__init__(base_form)
        # set icons
        self.set_icon("add_btn","add.svg")
        self.set_icon("cancel_btn","cancel.svg")
        
        