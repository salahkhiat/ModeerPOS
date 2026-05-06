from .base_form import Form

from uis.show_table import Ui_ShowTableUi as ShowTableUi
from show_table_form import ShowTableForm

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ProductsTableForm(Form):
    def __init__(self ,base_form):
        super().__init__(base_form)
        title = "سجل السلع"
        db_table = "products"
        fetch_func  = self.get_services_list
        table_header = []
        form = ShowTableForm(ShowTableUi,)

        


        