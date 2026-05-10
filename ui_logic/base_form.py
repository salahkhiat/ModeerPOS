from PyQt6.QtWidgets import  QDialog, QMainWindow, QComboBox
from PyQt6.QtCore import Qt 

from .shared_functions import SharedFunctions
from .shared_validators import SharedValidators
from .database_manager import DatabaseManager

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class MainForm(QMainWindow,DatabaseManager):
    def __init__(self,base_form):
        super().__init__()

        self.ui = base_form()  
        self.ui.setupUi(self)  

class Form(QDialog,SharedValidators,DatabaseManager):
    def __init__(self,base_form):
        super().__init__()
        self.ui = base_form()    
        self.ui.setupUi(self)
        # remove title bar
        self.remove_title_bar()
        

        # set the icons of  save and cancel buttons 
        self.set_save_cancel_icons()

        # set the direction of the form
        self.set_form_direction()

    # remove title bar (including the red 'X', minimize, maximize)
    def remove_title_bar(self):
        
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint
        )

    # set save, cancel icons
    def set_save_cancel_icons(self):
        if hasattr(self.ui, "save_btn"):
            self.set_icon("save_btn","save.svg")
        if hasattr(self.ui, "cancel_btn"):
            self.set_icon("cancel_btn","cancel.svg")
    
    # set form direction
    def set_form_direction(self):
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)





        


