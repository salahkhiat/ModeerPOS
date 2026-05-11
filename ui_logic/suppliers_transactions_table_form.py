from .base_form import Form
from .show_table_form import ShowTableForm

from .item_form import ItemForm
from uis.item import Ui_Form as ItemFormUi

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
        self.form.ui.edit_btn.clicked.connect(self.edit_supplier_info)


        self.form.exec()
    
    def edit_supplier_info(self):
        pass

        


        