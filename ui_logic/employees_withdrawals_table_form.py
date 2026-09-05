from .base_form import Form
from .show_table_form import ShowTableForm

from uis.withdrawal import Ui_Form as WithdrawalUi
from .withdrawal_form import WithdrawalForm

from PyQt6.QtWidgets import QMessageBox
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class EmployeesWithdrawalsTableForm(Form):
    def __init__(self ,base_form):
        super().__init__(base_form)

        self.form = ShowTableForm(
            base_form,
            "سجل سحوبات العمال",
            "employees_withdrawals",
            self.get_employees_withdrawals_list,
            ["المعرف", "العامل", "ملاحظة", "المبلغ", "التاريخ"],
            {1:140, 3:100, 4:180 },
            2,
            0,
            "id"
        ) 
        
        self.form.ui.edit_btn.clicked.connect(self.edit_transaction)
        


        self.form.exec()

        
    
    def edit_transaction(self):

        transaction = self.form.selected_row

        if transaction is None:
            QMessageBox.warning(None, "تنبيه", "لم تحدد أي معاملة بعد")

        else:
            transaction_id = transaction[0]
            employee_name = str(transaction[1])
            note = str(transaction[2])
            amount = str(transaction[3])

            form = WithdrawalForm(WithdrawalUi, transaction_id, employee_name)
            form.ui.note.setText(note)
            form.ui.amount.setText(amount)
            form.withdrawal_updated.connect(lambda _ : self.form.load_table())

            form.exec()
           