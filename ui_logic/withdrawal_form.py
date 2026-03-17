from PyQt6.QtWidgets import QComboBox, QLineEdit, QPushButton
from .base_form import Form
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class WithdrawalForm(Form):
    def __init__(self,base_form):
        super().__init__(base_form)
        # set form title
        self.setWindowTitle("سجل سحب الموظف")

        # default settings
        employees = self.get_table_as_list("employees",["name"])

        employees_combo:QComboBox = self.ui.employee
        employees_combo.addItems(employees)

        current_employee = employees_combo.currentText()
    
        # getting a selected employee's id, then assign it into obj.selected_employee_id.
        self.selected_employee_id = self.get_item_info("employees",("id",),"name",current_employee)["id"]
        employees_combo.currentTextChanged.connect(self.set_current_employee_id)

        # an amount field
        self.amount: QLineEdit = self.ui.amount
        self.accept_numbers_only(self.amount)

        # a note field
        self.note: QLineEdit = self.ui.note

        # connect save button
        save_btn: QPushButton = self.ui.save_btn
        save_btn.clicked.connect(self.create_transaction)


    def set_current_employee_id(self,text:str):
        """
            setting a selected employee id
        """
        self.selected_employee_id = self.get_item_info("employees",("id",),"name",text.strip())["id"]
    
    def create_transaction(self):
        valid_amount = self.is_amount("amount")
        if not valid_amount:
            print("invalid amount")
            return
        else:
            amount = float(self.ui.amount.text().strip())
            note = self.ui.note.text().strip()
            
            columns = ["employee_id","note","amount","created"]
            data = (
                self.selected_employee_id,
                note,
                amount,
                self.current_date()
            )
            self.store("employees_withdrawals",columns,data)
            
            fields = [
                self.amount,
                self.note
            ]

            self.clear_fields(fields)
            self.close()
            self.play_success_sound()

    
        
        





        

   


