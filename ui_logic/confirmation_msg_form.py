from .base_form import Form
from PyQt6.QtCore import pyqtSignal
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ConfirmationMsgForm(Form):
    confirmed = pyqtSignal(bool)

    def __init__(self,base_form,msg=""):
        super().__init__(base_form)
        self.setWindowTitle(msg)
        self.ui.msg.setText(msg)
        # set icons
        self.set_icon("apply_btn","apply.svg")
        self.set_icon("cancel_btn","cancel.svg")

        # buttons
        self.ui.apply_btn.clicked.connect(self.apply_clicked)

    def apply_clicked(self):
        self.confirmed.emit(True)
        self.accept()