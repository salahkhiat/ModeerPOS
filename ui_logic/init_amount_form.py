from .base_form import Form

import logging
import json
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class InitAmountForm(Form):
    
    def __init__(self,base_form):
        super().__init__(base_form)
        # set form title
        self.setWindowTitle("مبلغ الصندوق في بداية اليوم")

        amount = self.get_settings().get("init_amount", 0)
        self.ui.amount.setText(str(amount))

        self.ui.save_btn.clicked.connect(self.save_btn_clicked)
    
    def get_current_amount(self):
        return self.ui.amount.text()
    
    def save_btn_clicked(self):
        self.update_init_amount()
        

    def update_init_amount(self):
        amount = self.ui.amount.text()
        if len(amount) > 0:
            settings_path = self.get_settings_json_path()

            # Load the JSON file
            with open(settings_path, "r") as file:
                data = json.load(file)

            # Modify the value
            data["init_amount"] = int(self.ui.amount.text())

            # Save it back to the file
            with open(settings_path, "w") as file:
                json.dump(data, file, indent=4)
            
            self.close()
            self.play_success_sound()
        else:
            print("error")
        