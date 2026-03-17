from PyQt6.QtWidgets import QComboBox, QLineEdit, QPushButton
from .base_form import Form
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class CustomerPaymentForm(Form):
    def __init__(self,base_form):
        super().__init__(base_form)
        # set form title
        self.setWindowTitle("إيداع جديد")

        # validating an amount

        # default settings
        customers = self.get_table_as_list("customers",["name"])
        customers.pop(customers.index("-"))

        customers_combo:QComboBox = self.ui.customer
        customers_combo.addItems(customers)

        current_customer = customers_combo.currentText()
    
        # getting a selected customer's id, then assign it into obj.selected_customer_id.
        self.selected_customer_id = self.get_item_info("customers",("id",),"name",current_customer)["id"]
        customers_combo.currentTextChanged.connect(self.set_current_customer_id)

        # an amount field
        self.amount: QLineEdit = self.ui.amount
        self.accept_numbers_only(self.amount)

        # a note field
        self.note: QLineEdit = self.ui.note

        # connect save button
        save_btn: QPushButton = self.ui.save_btn
        save_btn.clicked.connect(self.create_transaction)


    def set_current_customer_id(self,text:str):
        """
            setting a selected customer id
        """
        self.selected_customer_id = self.get_item_info("customers",("id",),"name",str(text))["id"]
        print(f"the ID of {text.strip()} is {self.selected_customer_id}.")

    
    def create_transaction(self):
        valid_amount = self.is_amount("amount")
        if not valid_amount:
            print("invalid amount")
            return
        else:
            amount = float(self.ui.amount.text().strip())
            note = self.ui.note.text().strip()
            
            columns = ["customer_id","note","amount","created"]
            data = (
                self.selected_customer_id,
                note,
                amount,
                self.current_date()
            )
            self.store("customers_payments",columns,data)
            
            fields = [
                self.amount,
                self.note
            ]

            self.clear_fields(fields)
            self.close()
            self.play_success_sound()

    
        
        




