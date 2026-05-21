from .base_form import Form
from .category_form import CategoryForm
from uis.category import Ui_Form as CategoryUi
from PyQt6.QtCore import pyqtSignal
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ServiceForm(Form):
    service_updated = pyqtSignal(bool)
    def __init__(self, base_form, service_id=None, customer_name=None, category=None):
        super().__init__(base_form)

        # check form mode
        if service_id is not None:
            self.edit_mode = True
            self._service_id = service_id
            self._customer_name = customer_name
            self._category = category
        else:
            self.edit_mode = False

        #  customer and Category Combo part ---
        customers_combo = self.ui.customer
        self.fetch_then_put("customers", "name", customers_combo)

        categories_combo = self.ui.category
        self.fetch_then_put("services_categories", "name", categories_combo)


        # edit mode : select the old transaction customer and category.
        if self.edit_mode is True:
            supplier_index = customers_combo.findText(self._customer_name)
            customers_combo.setCurrentIndex(supplier_index)

            category_index = categories_combo.findText(self._category)
            categories_combo.setCurrentIndex(category_index)


        # set form title
        self.setWindowTitle("تسجيل خدمة جديدة")

        # set icons 
        self.set_icon("add_category_btn","add.svg")

        # Connect buttons
        self.add_category_clicked()

        # Filtering inputs.
        amount_field = self.ui.amount
        deposit_field = self.ui.deposit
        self.accept_numbers_only(amount_field)
        self.accept_numbers_only(deposit_field)
        self.enable_field(self.ui.deposit,False)

        # Default validation variables.
        self.is_valid_category = False
        self.is_valid_note = False 
        self.is_valid_amount = False 
        self.is_valid_deposit = True 
        
        # Validate fields.
        self.initial_validation()


        # Save Button clicked.
        self.save_btn_clicked()

    def initial_validation(self):
        self.ui.customer.activated.connect(self.check_customer)
        self.ui.category.activated.connect(lambda:self.update_validation_response("category","is_cur_item_empty"))
        self.ui.note.textChanged.connect(lambda:self.update_validation_response("note","is_empty"))
        self.ui.amount.textChanged.connect(lambda:self.update_validation_response("amount","is_amount"))
        self.ui.deposit.textChanged.connect(lambda:self.update_validation_response("deposit","is_deposit"))
    
    def check_customer(self):
        if self.is_cur_item_empty("customer"):
            self.enable_field(self.ui.deposit,True)
        else:
            self.enable_field(self.ui.deposit,False)
        
    def show_category_form(self) -> int:
        """
        Show add category form.
        """
        category_form = CategoryForm(CategoryUi)
        category_form.category_saved.connect(self.refresh_categories)
        return category_form.exec()
    
    def add_category_clicked(self):
        self.ui.add_category_btn.clicked.connect(self.show_category_form)

    def refresh_categories(self, saved:bool) -> bool:
        if saved:
            self.ui.category.clear()
            self.fetch_then_put("services_categories","name",self.ui.category)
            return True 
        else:
            return False 
        

    def save_service_form(self):
        # Fetch Customers and Categories table data {id:name}
        cus_dict = self.get_table_as_dict("customers","name")
        cat_dic = self.get_table_as_dict("services_categories","name")
        
        # cus_name and cat_name are the activated combo text.
        cus_name = self.ui.customer.currentText() 
        cus_id = None 
        for id, name in cus_dict.items():
            if name == cus_name:
                cus_id = id 
       
        cat_name = self.ui.category.currentText()
        cat_id = None
        for id, name in cat_dic.items():
            if name == cat_name:
                cat_id = id
        
        note = self.ui.note.text()
        amount = 0 if self.ui.amount.text().strip() == "" else float(self.ui.amount.text())
        deposit = 0 if self.ui.deposit.text().strip() == "" else float(self.ui.deposit.text())
        piece_price = 0 if self.ui.piece_price.text().strip() == "" else float(self.ui.piece_price.text())
        created = self.current_date()
        
        columns = [
            "customer_id",
            "category_id",
            "description",
            "default_price",
            "piece_price",
            "paid_price",
            "created"
        ]
        data = [cus_id, cat_id, note, amount, piece_price, deposit, created]
        table = "services"

       
        fields = [
            self.ui.note,
            self.ui.amount,
            self.ui.piece_price,
            self.ui.deposit
        ]

        if (self.is_valid_category or self.is_valid_note) and (self.is_valid_amount ):
            if cus_name == '-':
                if self.store(table,columns,tuple(data)):
                    self.clear_fields(fields)
            else:
                columns.insert(4, "paid_price")
                data.insert(4, deposit)
                if self.store(table, columns, tuple(data)):
                    self.clear_fields(fields)
            self.close()
            self.play_success_sound()
        elif  (not  self.is_valid_category and not self.is_valid_note) or (not self.is_valid_amount):

            if not self.is_valid_amount:
                self.update_validation_response("amount","is_amount")

            if not  self.is_valid_category and not self.is_valid_note:
                
                self.update_validation_response("note","is_empty")
    
    def save_btn_clicked(self):
        self.ui.save_btn.clicked.connect(self.save_service_form)


        
        