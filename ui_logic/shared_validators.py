from PyQt6.QtGui import  QRegularExpressionValidator 
from PyQt6.QtCore import QRegularExpression 
from PyQt6.QtWidgets import QLineEdit

from .database_manager import DatabaseManager

from typing import List

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class SharedValidators(DatabaseManager):
    # Set only numbers are accepted  
    def accept_numbers_only(self,field:QLineEdit ) -> None:
        """ Accept only numbers."""

        regex = QRegularExpression("^\d*$") # Accepts only digits 0-9
        validator = QRegularExpressionValidator(regex)
        field.setValidator(validator)
    
    def enable_field(self, field:QLineEdit, state=True):
        """
        Enable/Disable QLineEdit field, Enabled by default.

        Args:
            field (QLineEdit): the field as QLineEdit.
            state (bool): True is Enabled, and False is Disabled.
        """
        if state is True:
            field.setStyleSheet("background-color:white;")
        else:
            self.clear_fields([field])
            field.setStyleSheet("background-color:gray;")
        field.setEnabled(state)


    # Check the minimum and the maximum of an amount. min = 1 DZD , max = 10000000 DZD.
    def is_price(self, field_name:str):
        field = getattr(self.ui,field_name).text()
        if len(field) > 0:
            amount = int(field)
            if amount == 0 :
                self.set_err_msg(field_name,"الصفر قيمة مرفوضة")
                return False 
            elif amount > 10000000:
                self.set_err_msg(field_name,"أقصى مبلغ هو : 10000000 دج")
                return False
            elif amount > 0 and amount < 10000001:
                self.set_err_msg(field_name, "الحقل جاهز")
                return True 
            
    # Set a error message
    def set_err_msg(self, field_name:str ,msg:str=""):
        field_err = getattr(self.ui,field_name + "_err")
        field_err.setText(msg)

    # Check if the field is empty
    def is_empty(self, field_name:str, err_msg:bool=True )-> bool:
        """
        If the field is empty return False, and True otherwise.

        Args:
            field_name (str): the QLineEdit name.
            err_msg (bool): True by default to return error messages, and False without messages.
        """
        field = getattr(self.ui,field_name).text()
        if len(field) == 0:
            if err_msg:
                self.set_err_msg(field_name,"هذا الحقل مطلوب")
            return False
        else:
            if err_msg:
                self.set_err_msg(field_name,"الحقل جاهز")
            return True 
         
    
    def is_tel(self, field_name:str) -> bool:
        """ Returns True if a tel is valid, False otherwise."""

        field = getattr(self.ui,field_name).text()
        
        if len(field) < 10 and len(field) > 0:
            self.set_err_msg(field_name,"الهاتف أقصر من 10 أرقام")
            return False
        
        elif len(field) == 0:
            self.set_err_msg(field_name,"رقم الهاتف إختياري")
            return True 
        
        else:
            if field.startswith(("05","06","07")) :
                self.set_err_msg(field_name,"رقم الهاتف جاهز")
                return True
            
            else:
                self.set_err_msg(field_name," الهاتف يجب أن يبدأ بـ 05, 06, 07")
                return False
            
    def is_tel_ready(self, tel_field: str, user_id=None, user_type=None) -> bool :
        """ Returns True if the tel is ready to save, False otherwise. """

        table = None
        if user_id is not None and user_type is not None: 
            table = user_type

        else:
            combo_index = self.get_current_combo_index('account_type')
            account_types = ["customers", "suppliers", "employees"]
            table = account_types[combo_index]
        
        tel = getattr(self.ui, tel_field).text()

        if len(tel) == 0:
            return True
        if len(tel) > 0:
            # Edit Mode.
            if user_id is not None:
                if self.tel_exists(table, tel, user_id):
                    self.set_err_msg(tel_field, "الرقم مربوط بحساب آخر")
                    return False
                else:
                    return True
                
            # Insert Mode.
            else:
                if self.tel_exists(table, tel):
                    self.set_err_msg(tel_field, "هذا الرقم موجود مسبقا")
                    return False
                else:
                    return True
            
            
    
    def is_amount(self, field_name:str) -> bool:

        return self.is_empty(field_name) and self.is_price(field_name)
    
    
    def is_deposit(self, field_name:str) -> bool:

        if self.is_empty(field_name) == False:
            self.set_err_msg(field_name, "هذا الحقل إختياري")
            return True 
        else:
            return self.is_price(field_name)
    
    def is_max(self, table:str, column:str, max_len:int=10) -> bool:
        """
        Check if the table has the numbers of rows equivalent/greater than max_len.

        Args:
            table (str): the table name.
            column (str): the column name.4
            max_length (int): the maximum number of rows.
        Returns:
            bool : True if the numbers of rows is equivalent to max_len or greater 10 by default, and False otherwise.
        Examples:
            >>> table = "customers"
            >>> column = "name"
            >>> obj.is_max(table, column,5)
            False
        """
        rows = self.get_table_as_list(table,[column])
        
        if len(rows)  >= max_len:
            return True 
        else:
            return False 
        
    def is_cur_item_empty(self, combo_name:str) -> bool:
        """
        Check if the current (selected combo item) is empty ("") or equivalent to "-".

        Args:
            combo (str): the combo box name.
        Returns:
            bool: True if it is empty or equivalent to '-', and False otherwise.
        Examples:
            >>> combo = "QComboBox_name"
            >>> combo.addItem("first item")
            >>> obj.is_cur_item_empty(combo)
            False
        """
        combo_value = getattr(self.ui,combo_name).currentText()
        if combo_value == "" or combo_value == "-":
            return False 
        else:
            return True 

    def clear_fields(self, fields: List[QLineEdit] ) -> None:
        """
        Clears the text in multiple QLineEdit fields.

        :param fields: a list of QLineEdit .
        :type fields: list[QLineEdit]

        example:
        >>> name = obj.ui.name
        >>> address = obj.ui.address
        >>> fields = [name,address]
        >>> obj.clear_fields(fields)
        """
        for field in fields:
            field.clear()
    
    def update_validation_response(self, field_name: str, validating_fun: str, user_id=None, table=None) -> None:        
        validating = getattr(self, validating_fun)
        response = None 
        if user_id is not None and table is not None:
            response = validating(field_name, user_id, table)
        else:
            response = validating(field_name)
        setattr(self, "is_valid_" + field_name, response) 

    def is_purchase_price(self, field_name:str) -> bool:

        self.is_sale_price("sale_price")
        
        # if purchase price is not empty.
        if self.is_empty(field_name,err_msg=False):
            field = int(getattr(self.ui,field_name).text())

            # if purchase price is equivalent to 0.
            if field == 0:
                msg = "إنتبه! سعر الشراء الآن '0دج'"
                self.set_err_msg(field_name,msg)
                return True 
            # if purchase price is greater than 1000.000 DZD.
            elif field > 1000000:
                msg = "أقصى سعر مسموح به هو 1000.000 دج"
                self.set_err_msg(field_name,msg)
                return False
            # if purchase price is greater than 0 and less than 1000.001 DZD.
            elif field > 0 and field < 1000001:
                msg = "السعر جاهز"
                self.set_err_msg(field_name,msg)
                return True

            # if there is an expected error.
            else:
                msg = "تأكد من سلامة الحقل"
                self.set_err_msg(field_name,msg)
                return False
            
        # if a purchase price is empty.
        else:
            msg = "إنتبه! سعر الشراء الآن '0دج'"
            self.set_err_msg(field_name,msg)
            return True 
        
    def is_sale_price(self, field_name:str) -> bool:
        purchase_price = "purchase_price"
        
        # if sale price is not empty.
        if self.is_empty(field_name,err_msg=False):
            purchase_p = getattr(self.ui,purchase_price).text()
            p_price = None
            if len(purchase_p) == 0:
                p_price = 0
            else:
                p_price = int(purchase_p)

            field = int(getattr(self.ui,field_name).text())
    
            # if purchase price is equivalent to 0.
            if field == 0:
                msg = " الصفر غير مقبول كسعر بيع"
                self.set_err_msg(field_name,msg)
                return False 
            # if sale price is greater than 1000.000 DZD.
            elif field > 1000000:
                msg = "أقصى سعر مسموح به هو 1000.000 دج"
                self.set_err_msg(field_name,msg)
                return False
            # if sale price is greater than 0 and less than 500.001 DZD.
            elif (field > 0 and field < 1000001) and field > p_price:
                msg = "السعر جاهز"
                self.set_err_msg(field_name,msg)
                return True
            # if sale price is less than purchase_price
            elif (field > 0 and field < 1000001) and field < p_price:
                msg = "إنتبه:سعر البيع أقل من الشراء"
                self.set_err_msg(field_name,msg)
                return True
            # if sale parice is equivalent to purchase price.
            elif field == p_price and field != 0:
                msg = "إنتبه:السعر يساوي سعر الشراء"
                self.set_err_msg(field_name,msg)
                return True
            # if there is an expected error.
            else:
                msg = " "
                self.set_err_msg(field_name,msg)
                return False
            
        # if a sale price is empty.
        else:
            msg = "سعر البيع مطلوب"
            self.set_err_msg(field_name,msg)
            return False 
        
    def is_quantity(self, field_name:str) -> bool:

        field = getattr(self.ui,field_name).text()
        # if not empty
        if self.is_empty(field_name,err_msg=False):
            if int(field) == 0:
                msg = "0 كمية غير مقبولة"
                self.set_err_msg(field_name,msg)
                return False
            elif int(field) > 1000:
                msg = "أقصى كمية هي 1000 قطعة"
                self.set_err_msg(field_name,msg)
                return True 
            elif int(field) > 0 and int(field) < 1001:
                msg = "الحقل جاهز"
                self.set_err_msg(field_name,msg)
                return True
        # if empty
        else:
            msg = "حقل الكمية مطلوب"
            self.set_err_msg(field_name,msg)
            return False
            


    


    
        
    


        