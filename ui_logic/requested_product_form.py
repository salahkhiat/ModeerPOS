from .base_form import Form
from PyQt6.QtCore import pyqtSignal 
from typing import Dict
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class RequestedProductForm(Form):
    product_info:pyqtSignal = pyqtSignal(dict)
    def __init__(self,base_form):
        super().__init__(base_form)
        # set form title
        self.setWindowTitle("تسجيل السلع المطلوبة ")
        self.ui.title.setText("وصف قصير")

        # Default validation values
        self.is_valid_name = False

        # Validate fields.
        self.ui.name.textChanged.connect(lambda:self.update_validation_response("name","is_empty"))

        # Connect buttons
        self.save_btn_clicked()

    # save requested product form input
    def save_requested_product_form(self) -> bool:
        """
        Save a requested product form data in the database.

        Returns:
            bool: True if it was saved successfully, and False otherwise.
        """ 
        self.update_validation_response("name","is_empty")

        name = self.ui.name
        
        table = "requested_products"
        columns = ["name","created"]
        created = self.current_date()
        data = (name.text(),created)
        
        if self.is_valid_name == True:
            if self.is_max(table,"name",max_len=100):
                self.ui.name_err.setText("تجاوزت العدد المسموح به من العناصر")
            else:
                self.store(table,columns,data)
                fields = [name]
                self.clear_fields(fields)
                self.close()
                self.play_success_sound()
                requested_products:Dict = self.get_table_as_dict("requested_products","name")
                self.product_info.emit(requested_products)
        else:
            return False 
            
    def save_btn_clicked(self) -> None:
        """
        Connect the save button's clicked signal to the save_requested_product_form method.

        This sets up the event handling so that when the save button is clicked,
        the form data will be saved.
        """
        self.ui.save_btn.clicked.connect(self.save_requested_product_form)
    
    
    def cancel_btn_clicked(self):
        self.ui.cancel_btn.clicked.connect(lambda : self.clear_fields(['name']))
        


 
