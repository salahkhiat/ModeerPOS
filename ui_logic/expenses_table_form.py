from .base_form import Form
from .show_table_form import ShowTableForm

from uis.expense import Ui_Form as ExpensesUi
from .expense_form import ExpenseForm

from PyQt6.QtWidgets import QMessageBox
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ExpensesTableForm(Form):
    def __init__(self ,base_form):
        super().__init__(base_form)

        self.form = ShowTableForm(
            base_form,
            "سجل المصاريف",
            "expenses",
            self.get_expenses_list,
            ["المعرف", "ملاحطة", "القسم", "المبلغ", "التاريخ"],
            {2:140, 3:100, 4:180 },
            1,
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
            expense_id = transaction[0]
            category_name = str(transaction[2])
            note = str(transaction[1])
            amount = str(transaction[3])

            form = ExpenseForm(ExpensesUi, expense_id, category_name)
            form.ui.note.setText(note)
            form.ui.amount.setText(amount)
            form.expense_updated.connect(lambda _ : self.form.load_table())

            form.exec()
           