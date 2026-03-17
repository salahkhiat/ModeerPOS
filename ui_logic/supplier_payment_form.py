from PyQt6.QtWidgets import QComboBox, QLineEdit
from .base_form import Form
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class SupplierPaymentForm(Form):
    def __init__(self,base_form):
        super().__init__(base_form)
        # set form title
        self.setWindowTitle("إيداع أو دين جديد")
        
        #  supplier's field
        suppliers_combo:QComboBox = self.ui.supplier
        self.fetch_then_put("suppliers","name",suppliers_combo)
        current_supplier = suppliers_combo.currentText()

        self.selected_supplier_id = self.get_item_info("suppliers",("id",),"name",current_supplier.strip())["id"]
        suppliers_combo.currentTextChanged.connect(self.set_current_supplier_id)

        # transaction type's field
        current_transaction_type:QComboBox = self.ui.transaction_type
        self.selected_transaction_index = self.ui.transaction_type.currentIndex()
        current_transaction_type.currentIndexChanged.connect(self.set_transaction_index)
        self.types = {0:"debt",1:"deposit"}

        # an amount field
        self.amount: QLineEdit = self.ui.amount
        self.accept_numbers_only(self.amount)

        # a note field
        self.note: QLineEdit = self.ui.note
        
        # save button
        self.ui.save_btn.clicked.connect(self.create_transaction)
        
    

    def set_current_supplier_id(self,text:str):
        """
            setting a selected supplier id
        """
        
        self.selected_supplier_id = self.get_item_info("suppliers",("id",),"name",text.strip())["id"]
    
    def set_transaction_index(self,index:int):
        self.selected_transaction_index = index

    def create_transaction(self):
        valid_amount = self.is_amount("amount")
        if not valid_amount:
            print("invalid amount")
            return
        else:
            amount = float(self.ui.amount.text().strip())
            note = self.ui.note.text().strip()
            
            columns = ["supplier_id","note","amount","type","created"]
            data = (
                self.selected_supplier_id,
                note,
                amount,
                self.types[self.selected_transaction_index],
                self.current_date()
            )
            self.store("suppliers_transactions",columns,data)
            
            fields = [
                self.amount,
                self.note
            ]

            self.clear_fields(fields)
            self.close()
            self.play_success_sound()
            

            
            
        
    

        
        
        

        




