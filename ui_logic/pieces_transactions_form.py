from .base_form import Form


import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class PiecesTransactionsForm(Form):

    def __init__(self,base_form):
        super().__init__(base_form)
        # set icons
        self.set_icon("install_btn","install.svg")
        self.set_icon("in_shop_btn","pending.svg")
        self.set_icon("return_btn","return.svg")
        self.set_icon("delete_btn","delete.svg")
        self.set_icon("previous_btn","previous.svg")
        self.set_icon("next_btn","next.svg")
        self.set_icon("cancel_btn","cancel.svg")
        
        