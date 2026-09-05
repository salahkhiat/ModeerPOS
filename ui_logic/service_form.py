from .base_form import Form
from .category_form import CategoryForm
from uis.category import Ui_Form as CategoryUi
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox, QLineEdit
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

 
        # load brands and suppliers list
        suppliers_combo = self.ui.supplier
        self.fetch_then_put("suppliers", "name", suppliers_combo)

        brands_combo: QComboBox = self.ui.brand
        self.fetch_then_put("device_brands", "name", brands_combo)

        # edit mode : select the old transaction customer and category.
        if self.edit_mode is True:
            customers_combo = self.ui.customer
            self.fetch_then_put("customers", "name", customers_combo)

            categories_combo = self.ui.category
            self.fetch_then_put("services_categories", "name", categories_combo)

            customer_index = customers_combo.findText(self._customer_name)
            customers_combo.setCurrentIndex(customer_index)

            category_index = categories_combo.findText(self._category)
            categories_combo.setCurrentIndex(category_index)

        # set form title
        if self.edit_mode is False:
            self.setWindowTitle("تسجيل خدمة جديدة")
        else:
            self.setWindowTitle(f"تعديل الخدمة رقم {self._service_id}")

        # set icons 
        self.set_icon("add_category_btn","add.svg")

        # Connect buttons
        self.add_category_clicked()


        # Filtering inputs.
        amount_field = self.ui.amount
        deposit_field = self.ui.deposit
        piece_field = self.ui.piece_price
        self.accept_numbers_only(amount_field)
        self.accept_numbers_only(deposit_field)
        self.accept_numbers_only(piece_field)
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
    
    def get_fields_values(self):
        note = self.ui.note.text()
        amount = 0 if self.ui.amount.text().strip() == "" else float(self.ui.amount.text())
        deposit = 0 if self.ui.deposit.text().strip() == "" else float(self.ui.deposit.text())
        piece_price = 0 if self.ui.piece_price.text().strip() == "" else float(self.ui.piece_price.text())
        
        return (note, amount, deposit, piece_price)
        

    def save_service_form(self):
        # Fetch Customers and Categories table data {id:name}
        created = self.current_date()

        cus_dict = self.get_table_as_dict("customers","name")
        cat_dic = self.get_table_as_dict("services_categories","name")

        brand_dict = self.get_table_as_dict("device_brands", "name")
        brand: QComboBox = self.ui.brand
        selected_brand = brand.currentText()
        brand_id = self.reverse_dict(brand_dict)[selected_brand]

        supplier_dict = self.get_table_as_dict("suppliers", "name")
        supplier: QComboBox = self.ui.supplier
        selected_supplier = supplier.currentText()
        if selected_supplier != '-':
            supplier_id = self.reverse_dict(supplier_dict)[selected_supplier]
        else:
            supplier_id = None

        category: QComboBox = self.ui.category
        selected_category = category.currentText()

        description: QLineEdit = self.ui.note
        piece_description = f"{selected_category} {selected_brand} {description.text()}"

        
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
        
        note, amount, deposit, piece_price = self.get_fields_values()
        
        # Perform this case when you add a piece that belong to some one
        if piece_price > 0 and supplier_id != None:
            p_t_columns = ["supplier_id", "piece", "price", "status", "created"]
            p_t_data = [supplier_id, piece_description, piece_price, "installed", created]
            self.store("pieces_transactions", p_t_columns, p_t_data)
        #---

        columns = [
            "customer_id",
            "category_id",
            "description",
            "default_price",
            "piece_price",
            "paid_price",
            "brand_id",
            "created"
        ]

        data = [cus_id, cat_id, note, amount, piece_price, deposit, brand_id, created]
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


    
    def update_service_form(self):
        # 1- Get the service id
        service_id = self._service_id

        # 2- Get the selected customer id
        customer_name: str = self.ui.customer.currentText().strip()
        customer_id = self.get_item_info("customers", ("id",), "name", customer_name)['id']

        # 3- Get the selected service category id
        category_name: str = self.ui.category.currentText().strip()
        category_id = self.get_item_info("services_categories", ("id",), "name", category_name)['id']

        # 4- Get the fields values
        description, amount, deposit, piece_price = self.get_fields_values()

        # 5- Set the table details 
        table = "services"
        cols = [
            "customer_id", 
            "category_id", 
            "description", 
            "default_price", 
            "paid_price", 
            "piece_price"
        ]
        data = (customer_id, category_id, description, amount, deposit, piece_price)

        # 6- Apply changes
        self.update_info(table, cols, data, "id=?", (service_id,))

        # 7- Finish the process
        self.service_updated.emit(True)
        self.play_success_sound()
        self.close()

    def save_btn_clicked(self):
        
        if self.edit_mode is True:
            self.ui.save_btn.clicked.connect(self.update_service_form)
        else:
            self.ui.save_btn.clicked.connect(self.save_service_form)


        
        