from .base_form import Form
from .show_table_form import ShowTableForm

from .item_form import ItemForm
from uis.item import Ui_Form as ItemFormUi

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ProductsTableForm(Form):
    def __init__(self ,base_form):
        super().__init__(base_form)

        self.form = ShowTableForm(
            base_form,
            "جدول السلع",
            "products",
            self.get_products_list,
            ["الباركود", "الإسم", "الكمية", "الشراء بـ", "البيع بـ"],
            { 2:100, 3:100, 4:100 },
            1,
            0,
            "barcode"
        ) 
        self.form.ui.edit_btn.clicked.connect(self.edit_product)


        self.form.exec()
    
    def edit_product(self):
        product_id = self.form.selected_row[0]
        product_information = self.get_item_info(
            "products",
            (
                "barcode", 
                "name", 
                "quantity", 
                "sale_price", 
                "purchase_price"
            ),
            "barcode",
            product_id
            
        )
        # product_info = product_information.values()
        barcode = product_information["barcode"]
        name = product_information["name"]
        quantity = product_information["quantity"]
        sale_price = product_information["sale_price"]
        purchase_price = product_information["purchase_price"]

        form = ItemForm(ItemFormUi, product_id)
        form.set_icon("add_btn","apply.svg")
        form.setWindowTitle(name)
        form.ui.title.setText(name)
        form.ui.ref.setText(barcode)
        form.ui.name.setText(name)
        form.ui.quantity.setText(str(quantity))
        form.ui.purchase_price.setText(f"{purchase_price:.0f}")
        form.ui.sale_price.setText(f"{sale_price:.0f}")
        form.item_updated.connect(lambda _ : self.form.load_table()) 
        form.exec()

        


        