from .base_form import Form
from .show_table_form import ShowTableForm

from uis.supplier_payment import Ui_Form as SupplierTransactionUi
from .supplier_payment_form import SupplierPaymentForm

from PyQt6.QtWidgets import QMessageBox
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class SuppliersTransactionsTableForm(Form):
    def __init__(self ,base_form):
        super().__init__(base_form)

        self.form = ShowTableForm(
            base_form,
            "سجل عمليات الموردين",
            "suppliers_transactions",
            self.get_suppliers_transactions_list,
            ["المعرف", "المورد", "الوصف", "العملية", "المبلغ", "التاريخ"],
            {1:100, 3:100, 4:100, 5:180 },
            2,
            0,
            "id"
        ) 
        self.form.ui.edit_btn.clicked.connect(self.edit_transaction)


        self.form.exec()
    
    def edit_transaction(self):

        transaction_id = self.form.selected_row
        if transaction_id is None:
            QMessageBox.warning(None, "تنبيه", "لم تحدد أي معاملة بعد")

        else:
            form = SupplierPaymentForm(SupplierTransactionUi, transaction_id[0])
            form.transaction_updated.connect(lambda _ : self.form.load_table())
            form.exec()

        

        


        