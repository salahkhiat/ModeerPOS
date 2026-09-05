from PyQt6.QtWidgets import QComboBox, QLineEdit
from PyQt6.QtCore import pyqtSignal
from .base_form import Form
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class SupplierPaymentForm(Form):
    transaction_updated = pyqtSignal(bool)
    def __init__(self, base_form, transaction_id=None):
        super().__init__(base_form)
        
        # this part for updating mode
        if transaction_id is not None:
            self.edit_mode = True
            self.load_old_transaction(transaction_id)
        else:
            self.edit_mode = False

        # set form title
        self.setWindowTitle("إجراء معاملة مع مورد")
        
        #  supplier's Combo part ---
        suppliers_combo: QComboBox = self.ui.supplier
        self.fetch_then_put("suppliers", "name", suppliers_combo)

        current_supplier = suppliers_combo.currentText()

        # edit mode : select the old transaction supplier.
        if self.edit_mode is True:
            index = suppliers_combo.findText(self._supplier_name)
            suppliers_combo.setCurrentIndex(index)

        # Create mode.
        else:
            self.selected_supplier_id = self.get_item_info("suppliers",("id",),"name",current_supplier.strip())["id"]
            suppliers_combo.currentTextChanged.connect(self.set_current_supplier_id)
        # ---


        # transaction type's field
        current_transaction_type: QComboBox = self.ui.transaction_type
        
        self.selected_transaction_index = self.ui.transaction_type.currentIndex()
        current_transaction_type.currentIndexChanged.connect(self.set_transaction_index)
        # Edit Mode.
        if self.edit_mode is True:
            trans_types = {
                "debt": 1,
                "deposit": 2
            }
            index = trans_types[self._transaction["type"]] 
            current_transaction_type.setCurrentIndex(index)
            
        # ---
        
        # current_transaction_type.currentIndexChanged.connect(self.set_transaction_index)
        self.types = {0:"buy", 1:"debt", 2:"deposit"}

        # piece's status
        current_status: QComboBox = self.ui.status
        self.selected_status_index = current_status.currentIndex()
        current_status.currentIndexChanged.connect(self.set_status_index)
        self.status_types = {0:"in_shop", 1:"installed"}

        # Edit Mode: disable transaction status Combo
        if self.edit_mode is True:
            current_status.setEnabled(False)

        # an amount field 
        self.amount: QLineEdit = self.ui.amount
        self.accept_numbers_only(self.amount)

        # a note field
        self.note: QLineEdit = self.ui.note

        # Edit Mode: an amount & note fields.
        if self.edit_mode is True:
            self.amount.setText(str(self._transaction["amount"]))
            self.note.setText(str(self._transaction["note"]))
        
        # save button
        if self.edit_mode is True:
            self.ui.save_btn.clicked.connect(self.update_transaction) 
        else: 
            self.ui.save_btn.clicked.connect(self.create_transaction)   
        
    
    def load_old_transaction(self, transaction_id):
        """Editing Mode"""
        self._transaction_id = transaction_id
        
        self._transaction = self.get_item_info(
            "suppliers_transactions",
            ("supplier_id", "note", "amount", "type"),
            "id",
            transaction_id
        )
        
        self._supplier_name = self.get_item_info(
            "suppliers", ("name",), "id", self._transaction['supplier_id']
        )['name']
    

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

    def validate_fields(self):
        """Returns True if the fields are valids, False otherwise."""
        valid_amount = self.is_amount("amount")
        valid_note = self.is_empty("note", True)# empty =  False

        # Invalid empty amount or price
        if not valid_amount:
            logger.debug("invalid amount")
            return False
        
        elif not valid_note and self.selected_transaction_index == 0:
            logger.debug("invalid piece name")
            return False
        
        else:

            return True

    def create_transaction(self):
        """ Create Mode: create a new transaction."""

        if self.validate_fields() is not False:
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

    def get_selected_sup_id(self) -> int:
        """Returns the selected supplier id"""
        combo: QComboBox = self.ui.supplier
        supplier_name = combo.currentText().strip()
        supplier_id = self.get_item_info("suppliers", ("id",), "name", supplier_name)['id']
        return supplier_id


    def update_transaction(self):
        """Edit Mode: update an exists transaction"""
        supplier_id = self._transaction['supplier_id']
        transaction_id = self._transaction_id
        trans_type_index = self.ui.transaction_type.currentIndex()

        # transaction data
        trans_id = self._transaction_id
        trans_type = self.types[trans_type_index]
        new_supplier_id = self.get_selected_sup_id()
        note: QLineEdit = self.ui.note.text().strip()
        amount: QLineEdit = self.ui.amount.text().strip()
        data = [new_supplier_id, note, amount, trans_type]
        
        
        def edit_confirmed():
            self.transaction_updated.emit(True)
            self.close()
            self.play_success_sound()
        
        # 1 is a debt, 2 is a deposit
        # this for suppliers_transactions
        if trans_type_index in (1, 2):
            if self.validate_fields() is not False:
                
                cols = ["supplier_id", "note", "amount", "type"]
            
                self.update_info("suppliers_transactions", cols, tuple(data), "id=?", (trans_id,))
                    
                edit_confirmed()
                logger.warning(f"supplier's transaction with id {trans_id} was updated successfully")
                
            else:
                logger.error(f" something went wrong the supplier transaction with id {trans_id} was not updated.")

        # this for pieces_transactions
        elif trans_type_index == 0:
            
            if self.validate_fields() is not False:
                selected_index = self.selected_status_index
                status = self.status_types[selected_index]
                data[3] = status
                data.append(self.current_date())
                cols = ["supplier_id", "piece", "price", "status", "created"]

                piece_trans_id = self.store("pieces_transactions", cols, data, True)
                logger.warning(f"The piece transaction was inserted with ID {piece_trans_id}")

                self.delete_item_from_db("suppliers_transactions", "id", self._transaction_id)
                logger.warning(f"The supplier transaction with ID {self._transaction_id} was deleted")
                edit_confirmed()
                




            
            
        
    

        
        
        

        




