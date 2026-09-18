from .base_form import Form
from ui_logic.features.print_label import print_product_labels
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class PrepareLabelForm(Form):
    def __init__(self, base_form, selected_product):
        super().__init__(base_form)
        
        self.setWindowTitle("طباعة ملصقاة السعر")
        # set icons
        self.set_icon("apply_btn","print_barcode.svg")
        self.set_icon("cancel_btn","cancel_2.svg")

        self.product = [
            selected_product[1], # name
            str(selected_product[2]), # quantity
            str(selected_product[4]), # sale price
            str(selected_product[0])  # barcode
        ]
    
        self.ui.name.setText(self.product[0])
        self.ui.barcode.setText(self.product[3])
        self.ui.price.setText(self.product[2])
        self.ui.quantity.setText(self.product[1])
        
        self.accept_numbers_only(self.ui.quantity)
    
        self.ui.apply_btn.clicked.connect(self.print_now)

        
    def print_now(self):
        """ Prints the product labels. """
        self.product[1] = float(self.ui.quantity.text())
        
        label = print_product_labels([self.product,])