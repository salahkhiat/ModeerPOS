from PyQt6.QtCore import QStandardPaths 
from PyQt6.QtWidgets import QFileDialog
import json 
import os 
from .base_form import Form

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class DatabaseForm(Form):
    def __init__(self,base_form):
        super().__init__(base_form)
        
        # set form title
        self.setWindowTitle("إختر مكان حفظ بيانات المحل ، معاملات، فواتير، خدمات ... إلخ ")

        # Getting settings.json path
        current_dir = os.path.dirname(__file__) # Get the current working directory 
        parent_dir = os.path.abspath(os.path.join(current_dir,"..")) # Go up one level to 'main' directory
        self.settings_path = os.path.join(parent_dir,"settings.json")

        # connect buttons
        self.borwse_btn_clicked()
        self.save_btn_clicked()
        self.cancel_btn_clicked()
        
        # Show the defualt selected path in the window
        # settings = self.get_settings_info(self.settings_path)
        settings = self.get_settings()
        self.ui.current_path.setText(settings["database_path"])
        
        # Database info
        self.database_path = settings["database_path"]
        self.database_name = settings["database_name"]
        
        # set icons
        self.set_icon("browse_btn","browse.svg")

    # update database path label 
    def update_database_label(self):
        self.ui.current_path.setText(self.database_path)

    # Getting settings.json content
    def get_settings_info(self,settings_path): 
        with open(settings_path,'r') as file:
            settings = json.load(file)
        return settings
            
    # Updating database_path in setting.json
    def update_database_path(self,selected_path,settings_path):
        settings = None

        # Updating database path in settings.json
        with open(settings_path,'r') as file:
            settings = json.load(file)

        settings["database_path"] = selected_path
        with open(settings_path,'w') as file:
            json.dump(settings,file,indent=4)

    # browse directories 
    def browse_directories(self):
        selected_path = QFileDialog.getExistingDirectory(self, "", self.database_path)
        # if user selected a path
        if len(selected_path) > 0:
            self.database_path = selected_path
            self.update_database_label()
            
    # browse button clicked
    def borwse_btn_clicked(self):
        self.ui.browse_btn.clicked.connect(self.browse_directories)  

    # save changes
    def save_changes(self):
        if self.database_path == None:
            self.database_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        self.update_database_path(self.database_path,self.settings_path)
        database_ref = os.path.join(self.database_path, self.database_name)
        self.prepare_database(database_ref)
        self.close()

    # save btn clicked
    def save_btn_clicked(self):
        self.ui.save_btn.clicked.connect(self.save_changes)   

    # # is database path selected 
    def is_database_path_selected(self)-> bool:
        if self.database_path:
            return True
        else:
            # close the app, if no database_path selected.
            exit(0)
            return False 

    # cancel btn clicked
    def cancel_btn_clicked(self):
        self.ui.cancel_btn.clicked.connect(self.is_database_path_selected)



