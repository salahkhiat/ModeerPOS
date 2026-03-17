from .base_form import Form

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class SalesHistoryTableForm(Form):

    def __init__(self,base_form):
        super().__init__(base_form)
        # set form title
        self.setWindowTitle("سجل المبيعات")
        headers:list = ["test1","test2","test3"]
        table = self.ui.table
        self.set_table(table, headers)
        