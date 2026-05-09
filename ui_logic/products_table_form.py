from .base_form import Form
from .show_table_form import ShowTableForm

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ProductsTableForm(Form):
    def __init__(self ,base_form):
        super().__init__(base_form)
    # def __init__(self ):
    #     super().__init__()
        
        
        self.form = ShowTableForm(
            base_form,
            "Services table",
            "services",
            self.get_services_list,
            ["المعرف", "الوصف", "الزبون", "الصنف", "السعر", "الإيداع", "التاريخ"],
            { 2:140, 3:120, 4:90, 5:90, 6:180 },
            1,
            0
        ) 

        self.form.exec()

        


        