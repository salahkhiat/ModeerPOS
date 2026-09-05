from PyQt6.QtWidgets import QComboBox, QLineEdit, QPushButton
from .base_form import Form

from PyQt6.QtCore import pyqtSignal
from .expenses_category_form import ExpensesCategoryForm
from uis.category import Ui_Form as CategoryUi
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ExpenseForm(Form):
    expense_updated = pyqtSignal(bool)
    def __init__(self,base_form, expense_id=None, category=None):
        super().__init__(base_form)

        if expense_id is not None:
            self._expense_id = expense_id
            self._category = category
            self.edit_mode = True 
            self._title = "تعديل المصروف"
        else:
            self.edit_mode = False 
            self._title = "تسجيل المصروف"

        # set form title
        self.setWindowTitle(self._title)

        # set icons 
        self.set_icon("add_category_btn","add.svg")
        

        # default settings
        categories = self.get_table_as_list("expenses_categories",["name"])

        categories_combo:QComboBox = self.ui.category
        categories_combo.addItems(categories)

        if self.edit_mode is True:
            category_index = categories_combo.findText(self._category)
            categories_combo.setCurrentIndex(category_index)


        # Default validation variables.
        self.is_valid_category = False
    
        # Connect buttons
        self.add_category_clicked()


        # an amount field
        self.amount: QLineEdit = self.ui.amount
        self.accept_numbers_only(self.amount)

        # a note field
        self.note: QLineEdit = self.ui.note

        # connect save button
        save_btn: QPushButton = self.ui.save_btn
        save_btn.clicked.connect(self.create_transaction)

    
    def create_transaction(self):
        cat_dic = self.get_table_as_dict("expenses_categories","name")

        cat_name = self.ui.category.currentText()
        cat_id = None
        for id, name in cat_dic.items():
            if name == cat_name:
                cat_id = id

        valid_amount = self.is_amount("amount")
        if not valid_amount:
            print("invalid amount")
            return
        else:
            amount = float(self.ui.amount.text().strip())
            note = self.ui.note.text().strip()
            
            columns = ["category_id","note","amount","created"]
            data = (
                cat_id,
                note,
                amount,
                self.current_date()
            )
            table = "expenses"

            if self.edit_mode is True:
                cols = ["category_id", "note", "amount"]
                new_data = data[:3]
                self.update_info(table, cols, new_data, "id=?", (self._expense_id,))
                self.expense_updated.emit(True)
            else:
                self.store(table, columns, data)

            fields = [
                self.amount,
                self.note
            ]

            self.clear_fields(fields)
            self.close()
            self.play_success_sound()

    def show_category_form(self) -> int:
            """
            Show add category form.
            """
            category_form = ExpensesCategoryForm(CategoryUi)
            category_form.category_saved.connect(self.refresh_categories)
            return category_form.exec()
    
    def add_category_clicked(self):
        self.ui.add_category_btn.clicked.connect(self.show_category_form)

    def refresh_categories(self, saved:bool) -> bool:
        if saved:
            self.ui.category.clear()
            self.fetch_then_put("expenses_categories","name",self.ui.category)
            return True 
        else:
            return False 
    
        
        





        

   





