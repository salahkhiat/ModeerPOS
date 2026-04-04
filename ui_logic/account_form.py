from .base_form import Form
import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class AccountForm(Form):
    def __init__(self,base_form, user_item_id: int=None, user_type: str=None):
        
        super().__init__(base_form)
        # Set form title
        self.setWindowTitle("قم بإنشاء حساب") 
        
        # Default validation values
        self.is_valid_name = False
        self.is_valid_tel = True
        self.editable = False
        
        # Check user account type and user ID.
        if user_item_id and user_type:
            self.user_type = user_type
            self.user_item_id = user_item_id

            self.editable = True
        
        # Filtering inputs
        telephone_field = self.ui.tel
        self.accept_numbers_only(telephone_field)

        # Validate fields.
        self.ui.name.textChanged.connect(lambda:self.update_validation_response("name","is_empty"))

        if self.editable:
            self.ui.tel.textChanged.connect(
                lambda:self.update_validation_response("tel", "is_tel_ready", user_item_id, user_type)
            )

        else:
            self.ui.tel.textChanged.connect(
                lambda:self.update_validation_response("tel", "is_tel_ready")
            )

        # Re-validate the telephone number again when the user changes the account type.
        if self.editable:
            self.ui.account_type.activated.connect(
                lambda:self.update_validation_response("tel", "is_tel_ready", user_item_id, user_type)
            )

        else:
            self.ui.account_type.activated.connect(
                lambda:self.update_validation_response("tel", "is_tel_ready")
            )

        # Buttons connection
        self.save_btn_clicked()


    # save account form inputs
    def save_account_form(self) -> None:
        """ Insert a new account into the database. """ 
        name = self.ui.name
        tel = self.ui.tel
        table = None 

        if self.editable is False:
            combo_index = self.get_current_combo_index('account_type')
            account_types = ["customers", "suppliers", "employees"]
            table = account_types[combo_index]

        else:
            table = self.user_type

        columns = ["name", "tel"]
        data = (name.text(),tel.text())
        
        if self.is_valid_name == True and self.is_valid_tel == True:

            # create a new user.
            if self.editable is False:
                self.store(table, columns, data)
                
            # edit a user information name and tel.    
            else:
                self.update_info(
                    table, columns, data, "id=?",(self.user_item_id,)
                )

            fields = [name, tel]
            self.clear_fields(fields)
            self.close()
        self.play_success_sound()
              
    def save_btn_clicked(self) -> None:
        self.ui.save_btn.clicked.connect(self.save_account_form)
        


 
