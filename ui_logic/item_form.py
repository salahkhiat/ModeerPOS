from .base_form import Form

from PyQt6.QtCore import pyqtSignal
from typing import List
from PyQt6.QtWidgets import QWidget
import logging
class ItemForm(Form):
    item_added = pyqtSignal(dict)
    item_updated = pyqtSignal(bool)
    def __init__(self, base_form, item_barcode=None):
        super().__init__(base_form)
        self.setWindowTitle("إدخال معلومات السلعة")
        # set icons
        self.set_icon("add_btn","add.svg")
        
        self.add_item_btn_clicked()
        
        # accept only digits
        self.accept_numbers_only(self.ui.ref)
        self.accept_numbers_only(self.ui.quantity)
        self.accept_numbers_only(self.ui.purchase_price)
        self.accept_numbers_only(self.ui.sale_price)

        # For updating product information purpose only
        if item_barcode:
            self.item_barcode = item_barcode 
        else:
            self.item_barcode = None 
        
        # Validation
        self.is_valid_name = False
        self.is_valid_purchase_price = False
        self.is_valid_sale_price = False 
        self.is_valid_quantity = False 
        self.is_valid_ref = False

        # Validate fields.
        self.ui.name.textChanged.connect(lambda:self.update_validation_response("name","is_empty"))
        self.ui.quantity.textChanged.connect(lambda: self.update_validation_response("quantity","is_quantity"))
        self.ui.purchase_price.textChanged.connect(lambda:self.update_validation_response("purchase_price","is_purchase_price"))
        self.ui.sale_price.textChanged.connect(lambda:self.update_validation_response("sale_price","is_sale_price"))
        
    def set_table_refs(self,table_refs:List=None):

        self.table_references_list = table_refs

    def validating_fields(self):
        
        item_details = {
            'name': self.ui.name.text(),
            'purchase_price': self.ui.purchase_price.text(),
            'sale_price': self.ui.sale_price.text(),
            'quantity': self.ui.quantity.text(),
            'ref': self.ui.ref.text().strip(),
        }

        """
            barcode related.
        """

        
        # if a barcode field is Empty.
        if not self.is_empty("ref",err_msg=False): 

            # this condition block is only for updating product information option.
            if self.item_barcode:
                self.is_valid_ref = False
                    
            else:

                # this loop for saving new product.
                while True:
                    # Generate a reference (barcode)
                    generated_ref = str(self.generate_reference())
                    
                    # if the invoice table widget is Empty.
                    if len(self.table_references_list) == 0:
                        item_details['ref'] = generated_ref
                        self.is_valid_ref = True
                        break

                    # if an invoice table widget is not empty.
                    elif len(self.table_references_list) > 0:
                        # If a reference is in an invoice table widget, if yes, regenerate it then recheck. 
                        if generated_ref in self.table_references_list:
                            continue
                        # Else store a generated ref (barcode), Then set it valid
                        else:
                            item_details['ref'] = generated_ref
                            self.is_valid_ref = True
                            break
        # if a reference(barcode) field is not empty.
        else:
            
            # this condition block is only for updating product information option.
            if self.item_barcode:
                product_id = self.get_item_info(
                    "products",
                    ("id",),
                    "barcode",
                    str(self.item_barcode)
                )['id']
                
                if self.is_belonged_to_other(product_id, item_details["ref"]) is True:
                    err_msg = "المرجع مستخدم مسبقا"
                    self.set_err_msg("ref",err_msg)
                    self.is_valid_ref = False
                else:
                    self.is_valid_ref = True
                    
            else:
                ref = item_details['ref']
                # if an invoice table widget is empty.
                if len(self.table_references_list) == 0:

                    # If the reference(barcode) is not empty.
                    if item_details['ref'].strip() != "":
                            self.is_valid_ref = True

                # If an invoice table widget is not empty.
                if len(self.table_references_list) > 0:

                    # If a reference in an invoice table widget, if yes, ask the user to retry with new barcode.
                    if ref in self.table_references_list:
                        err_msg = "المرجع مستخدم مسبقا"
                        self.set_err_msg("ref",err_msg)
                        self.is_valid_ref = False

                    # If a reference is not in an invoice table widget and not empty then it is valid.
                    else: 
                        if item_details['ref'].strip() != "":
                            self.is_valid_ref = True

        """
            Quantity related.
        """
        valid_data = {
            "name" : self.is_valid_name,
            "purchase_price" : self.is_valid_purchase_price,
            "sale_price" : self.is_valid_sale_price,
            "quantity" : self.is_valid_quantity,
            "ref": self.is_valid_ref 
        }
        valid_fields = 0

        for _ , state in valid_data.items():
            if state:
                valid_fields += 1

        return (valid_fields, item_details)

    def add_item_to_invoice(self):
       
        validated_fields, item_details = self.validating_fields()

        if validated_fields != 5:
            logging.warning("A product info has entered is invalid.")

        else:
            # this condition block is only for saving product information option.
            if not self.item_barcode:    
                self.item_added.emit(item_details)

            # this condition block is only for updating product information option.
            else:
                self.apply_updates()
                self.play_success_sound()
                self.item_updated.emit(True)

            self.close()
        
               
    def add_item_btn_clicked(self):
        self.ui.add_btn.clicked.connect(lambda: self.add_item_to_invoice())
    
    def product_form_info(self):
        form: QWidget = self.ui 
        return (
            form.ref.text().strip(),
            form.name.text().strip(),
            form.quantity.text().strip(),
            form.purchase_price.text().strip(),
            form.sale_price.text().strip()
        )
    
    def apply_updates(self):
        new_data = self.product_form_info()
        columns = [
            "barcode",
            "name",
            "quantity",
            "purchase_price",
            "sale_price"
        ]
        self.update_info(
            "products",
            columns,new_data,
            f"barcode=?",
            (self.item_barcode,)
        )
    


        

    

        



    