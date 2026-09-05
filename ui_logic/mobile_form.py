from .base_form import Form
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class MobileForm(Form):
    def __init__(self,base_form):
        super().__init__(base_form)
        # set form title
        self.setWindowTitle("أدخل معلومات الهاتف المشترى")
        # validating user inputs
        price = self.ui.price
        seller_tel = self.ui.seller_tel
        document_id = self.ui.document_id
        imei_serial = self.ui.imei_serial
        
        self.accept_numbers_only(price)
        self.accept_numbers_only(seller_tel)
        self.accept_numbers_only(document_id)
        self.accept_numbers_only(imei_serial)

        self.documents_types = {
            0:"identification_card",
            1:"driving_license",
            2:"passport"
        }
        
        
        # Connect buttons
        self.save_cliced()

    def validate_form_fields(self)->bool:
        """
        If required fields are valid, return True and False otherwise.
        """
        if self.is_empty("mobile_name") is False :
            print("mobile name is required")
            return False
        
        elif self.is_empty("seller_name") is False : 
            print("Seller name is required")
            return False
        
        elif self.is_empty("price") is True:
            if self.is_price("price") is False:
                return False
            
        elif self.is_empty("seller_tel") is True:
            if self.is_tel("seller_tel") is False:
                return False
        else:
            return True

    def save_mobile_form(self):
        if self.validate_form_fields() is False:
            return 
        else:
            mobile_info = {
                "model": self.ui.mobile_name.text(),
                "color": self.ui.mobile_color.text(),
                "price": self.ui.price.text(),
                "serial": self.ui.imei_serial.text(),
                "seller_name": self.ui.seller_name.text(),
                "seller_tel": self.ui.seller_tel.text(),
                "seller_identify_id": self.ui.document_id.text(),
                "document_type": self.documents_types[self.ui.document_type.currentIndex()],
                "created": self.current_date()
                
            }
            columns = [ key for key in mobile_info.keys()]
            data = [ key for key in mobile_info.values()]
            self.store("mobiles",columns,data)
            self.close()
            self.play_success_sound()

    def save_cliced(self):
        self.ui.save_btn.clicked.connect(self.save_mobile_form)


        




