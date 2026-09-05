from .base_form import Form
from PyQt6.QtCore import pyqtSignal
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ExpensesCategoryForm(Form):
    category_saved = pyqtSignal(bool)

    def __init__(self,base_form):
        super().__init__(base_form)
        # set form title
        self.setWindowTitle("إضافة تقسيمة مصروفات  جديدة")
        self.ui.title.setText("نوع المصروف")

        # Default validation values
        self.is_valid_name = False

        # Validate fields.
        self.ui.name.textChanged.connect(lambda:self.update_validation_response("name","is_empty"))

        # Connect buttons
        self.save_btn_clicked()

    # save category form input
    def save_category_form(self) -> bool:
        """
        Save a category form data in the database.

        Returns:
            bool: True if it was saved successfully, and False otherwise.
        """ 
        self.update_validation_response("name","is_empty")

        name = self.ui.name
        
        table = "expenses_categories"
        columns = ["name"]
        data = (name.text(),)
        
        if self.is_valid_name == True:
            if self.is_max(table,"name"):
                self.ui.name_err.setText("تجاوزت العدد المسموح به من العناصر")
            else:
                self.category_saved.emit(self.store(table,columns,data)) # emit the signal
                fields = [name]
                self.clear_fields(fields)
                self.close()
        else:
            return False 
            
    def save_btn_clicked(self) -> None:
        """
        Connect the save button's clicked signal to the save_category method.

        This sets up the event handling so that when the save button is clicked,
        the form data will be saved.
        """
        self.ui.save_btn.clicked.connect(self.save_category_form)
    
    
    def cancel_btn_clicked(self):
        self.ui.cancel_btn.clicked.connect(lambda : self.clear_fields(['name']))
        


 
