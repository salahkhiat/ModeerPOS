from PyQt6.QtWidgets import QComboBox, QLineEdit
from .base_form import Form
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class SupplierPaymentForm(Form):
    def __init__(self, base_form, transaction_id=None):
        super().__init__(base_form)
        # this part for updating mode
        self._transaction_id = transaction_id

        if transaction_id is not None:
            self._transaction = self.get_item_info(
                "suppliers_transactions",
                ("supplier_id", "note", "amount", "type"),
                "id",
                transaction_id
            )
            
            self._supplier_name = self.get_item_info(
                "suppliers", ("name",), "id", self._transaction['supplier_id']
            )['name']
        ####
            

        # set form title
        self.setWindowTitle("إجراء معاملة مع مورد")
        
        #  supplier's field
        suppliers_combo: QComboBox = self.ui.supplier
        self.fetch_then_put("suppliers", "name", suppliers_combo)
        current_supplier = suppliers_combo.currentText()

        # this for updating mode
        if transaction_id is not None:
            index = suppliers_combo.findText(self._supplier_name)
            suppliers_combo.setCurrentIndex(index)
        ####


        self.selected_supplier_id = self.get_item_info("suppliers",("id",),"name",current_supplier.strip())["id"]
        suppliers_combo.currentTextChanged.connect(self.set_current_supplier_id)



        # transaction type's field
        current_transaction_type: QComboBox = self.ui.transaction_type
        
        self.selected_transaction_index = self.ui.transaction_type.currentIndex()
        if transaction_id is None:

            current_transaction_type.currentIndexChanged.connect(self.set_transaction_index)
        self.types = {0:"buy", 1:"debt", 2:"deposit"}

        # for updating mode
        if transaction_id is not None:
            trans_types = {
                "deposit":"إيداع",
                "debt":"دين"
            }
            current_transaction_type.clear()
            current_transaction_type.addItems(trans_types.values())

        ###
        
        
        # piece's status
        current_status: QComboBox = self.ui.status

        self.selected_status_index = current_status.currentIndex()
        current_status.currentIndexChanged.connect(self.set_status_index)
        self.status_types = {0:"in_shop", 1:"installed"}
        # this part for updating mode
        if transaction_id is not None:
            current_status.setEnabled(False)




        # an amount field
        self.amount: QLineEdit = self.ui.amount
        self.accept_numbers_only(self.amount)

        # a note field
        self.note: QLineEdit = self.ui.note
        
        # save button
        self.ui.save_btn.clicked.connect(self.create_transaction)
        
    

    def set_current_supplier_id(self, text:str):
        """
            setting a selected supplier id
        """
        
        self.selected_supplier_id = self.get_item_info("suppliers", ("id",), "name",text.strip())["id"]
    
    def set_transaction_index(self, index:int):
        self.selected_transaction_index = index

        # check status state
        self.disable_enable_status(index)

        # set placeholders
        self.set_placeholders(index)

    def set_status_index(self, index:int):
        self.selected_status_index = index

    def disable_enable_status(self, index):
        status: QComboBox = self.ui.status
        if index != 0:
            status.setEnabled(False)
        else:
            status.setEnabled(True)

    def set_placeholders(self, index):
        note: QLineEdit = self.ui.note
        amount: QLineEdit = self.ui.amount

        if index == 0:
            note.setPlaceholderText("إسم القطعة مثلا : Nappe A12")
            amount.setPlaceholderText("سعر القطعة مثلا : 850دج")
        else:
            note.setPlaceholderText("ملاحظة قصيرة")
            amount.setPlaceholderText("المبلغ")
            
        
    def create_transaction(self):
        valid_amount = self.is_amount("amount")
        valid_note = self.is_empty("note", True)# empty =  False

        # Invalid empty amount or price
        if not valid_amount:
            logger.debug("invalid amount")
            return
        
        # Invalid empty piece name
        elif not valid_note and self.selected_transaction_index == 0:
            logger.debug("invalid piece name")
            return
        else:
            # amount represents Amount and Piece price
            amount = float(self.ui.amount.text().strip())

            # note represents a Short note and Piece name.
            note = self.ui.note.text().strip() 

            table, columns = None, None
            data = [ 
                self.selected_supplier_id,
                note,
                amount,
                self.status_types[self.selected_status_index],
                self.current_date()
            ]

            # If a transaction type is buy
            if self.selected_transaction_index == 0:
                table = "pieces_transactions"
                columns = ["supplier_id", "piece", "price", "status", "created"]

            # If a transaction type is Deposit or Debt
            else:
                table = "suppliers_transactions"
                columns = ["supplier_id","note","amount","type","created"]
                data[3] = self.types[self.selected_transaction_index]

            # save a transaction into a database
            self.store(table, columns, tuple(data))
            
            # Clean fields content
            fields = [self.amount, self.note]
            self.clear_fields(fields)

            self.close()
            self.play_success_sound()
            

            
            
        
    

        
        
        

        




