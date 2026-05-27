from .base_form import Form
from .show_table_form import ShowTableForm

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class SalesHistoryTableForm(Form):
    def __init__(self ,base_form):
        super().__init__(base_form)
        try:
            self.form = ShowTableForm(
                base_form,
                "سجل المبيعات",
                None,
                self.get_sales_history_list,
                ["السلعة", "الباركود", "السعر", "الكمية", "المجموع", "الفاتورة", "التاريخ" ],
                {2:120, 3:60, 4:120, 5:120, 6:180},
                0,
                1,
                None
            ) 
        except Exception as e:
            print(e)
        
        self.form.ui.edit_btn.setEnabled(False)
        self.form.ui.delete_btn.setEnabled(False)
        self.form.ui.edit_btn.setStyleSheet("background-color:gray; border:1px;")
        self.form.ui.delete_btn.setStyleSheet("background-color:gray; border:1px;")
        
        self.form.exec()

        

           