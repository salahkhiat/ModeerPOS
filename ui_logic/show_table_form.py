from .base_form import Form

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ShowTableForm(Form):
    def __init__(self,base_form, form_title):
        super().__init__(base_form)
        self.setWindowTitle(form_title)

        # set form icons
        self.set_icons()

        

    def set_icons(self):
        self.set_icon("delete_btn","delete.svg")
        self.set_icon("edit_btn","edit.svg")
        self.set_icon("previous_btn","previous.svg")
        self.set_icon("next_btn","next.svg")
        self.set_icon("cancel_btn","cancel.svg")