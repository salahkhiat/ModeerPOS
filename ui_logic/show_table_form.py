from .base_form import Form
from PyQt6.QtWidgets import (
    QTableView,
    QHeaderView,
    QMessageBox
)
from uis.confirmation_msg import Ui_Dialog as ConfirmationMsgUi
from .confirmation_msg_form import ConfirmationMsgForm
from .shared_functions import TableViewModel

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ShowTableForm(Form):
    def __init__(
        self, 
        base_form,
        form_title,
        db_table,
        fetch_function,
        table_header,
        header_widths,
        stretch_col,
        resize_content_col,
        delete_column
    ):
        super().__init__(base_form)
        self.setWindowTitle(form_title)
        self._db_table = db_table
        self._fetch_function = fetch_function
        self._table_header = table_header
        self._header_widths = header_widths
        self._stretch_col = stretch_col
        self._resize_content_col = resize_content_col
        self._delete_column = delete_column
        
        
        self._table:QTableView = self.ui.table

        # set form icons
        self.set_icons()

        # Pagination part
        next_btn = self.ui.next_btn
        previous_btn = self.ui.previous_btn
        
        next_btn.clicked.connect(self.next_page)
        previous_btn.clicked.connect(self.previous_page)

        self.page = 0
        self.page_size = 15
        self.pagination_counter = self.ui.page_number

        # load table 
        self.keyword = None 
        self.load_table()

        # Search box
        search_box = self.ui.search_box
        search_box.textChanged.connect(self.load_table)

        # connect buttons
        self.connect_buttons()
    
    def load_table(self, keyword=None):
        
        keyword = str(keyword).strip() if keyword is not None else None

        # 🔥 only reset page if keyword CHANGED
        if keyword != self.keyword:
            self.page = 0

        self.keyword = keyword
                
        table = self._table
        
        offset = self.page * self.page_size
        
        data = self._fetch_function(keyword=keyword, limit=self.page_size, offset=offset)
        
        self.model = TableViewModel(data, self._table_header)
        table.setModel(None)
        table.setModel(self.model)

        self.set_table_basic_settings()
        
        #  update pagination counter
        self.update_pagination_counter() 
        
        self.selected_row = None

        # selected model
        selection_model = table.selectionModel()
        selection_model.selectionChanged.connect(self.on_row_selected)




    def on_row_selected(self, selected, deselected):
        indexes = selected.indexes()
        
        if indexes:
            row = indexes[0].row()
            self.selected_row = self.model._data[row]

    def next_page(self):
        self.page += 1
        data = self._fetch_function(keyword=self.keyword, limit=self.page_size, offset=self.page * self.page_size)

        if not data:
            self.page -= 1  # rollback
            return

        self.load_table(keyword=self.keyword)

    def previous_page(self):
        if self.page > 0:
            self.page -= 1
            self.load_table(keyword=self.keyword)

    def set_table_basic_settings(self):
        # Set table view headers and columns
        
        self.set_table_view_headers(
            self._table, 
            self._header_widths, 
            self._resize_content_col, 
            self._stretch_col
        )

        # make a row scrollable
        self.remove_rows_counter(self._table)
        self.make_rows_scrollable(self._table)


    def set_table_view_headers(
            self, 
            table, 
            fixed_cols:dict[int:int], 
            resize_to_content_col:int, 
            stretch_col:int
        ):
        """ Set A table view headers, columns fixed and stretch widths"""

        header = table.horizontalHeader()
        col_count = table.model().columnCount()

        # Set all to Interactive first
        for col in fixed_cols.keys():
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)

        for col, width in fixed_cols.items():
            # Custom widths for first col
            table.setColumnWidth(col, width)
        
        if resize_to_content_col:
            header.setSectionResizeMode(resize_to_content_col, QHeaderView.ResizeMode.ResizeToContents)

        # Last column stretches
        header.setSectionResizeMode(stretch_col, QHeaderView.ResizeMode.Stretch)

    def delete_btn_clicked(self):
        self.ui.delete_btn.clicked.connect(self.delete_item)
    
    def customer_payments_deletion(self):
        """Check from the process type before apply deletion"""
        if self._db_table == "customers_payments":
            process = self.selected_row[3]
            if process == "service":
                self._db_table = "services"
                return True
            
            elif process == "payment":
                self._db_table = "customers_payments"
                return True 
            
            else:
                title = "تنبيه"
                text = "لا يمكنك حذف هذا العنصر"
                QMessageBox.warning(None, title, text)
                return False
        else:
            return True
            
    def delete_item(self):
        if self.selected_row is None:
            title = "تأكيد عمية الحذف"
            text = "إختر العنصر الذي تريد حذفه"
            QMessageBox.warning(None, title, text)
        else:
            
            msg = "هل أنت متأكد من عملية الحذف؟"
            form = ConfirmationMsgForm(ConfirmationMsgUi, msg)
            form.confirmed.connect(self.confirm_deletion)
            form.exec()

    def confirm_deletion(self, cmd):
        if cmd is True:
            # Get the selected item id.
            item_id = self.selected_row[0]

            if not self.customer_payments_deletion():
                return 
            
            # Delete the selected item.
            self.delete_item_from_db(self._db_table, self._delete_column, item_id)

            # Reset the pagination page to 0.
            self.page = 0 

            # Reload the items table.
            self.load_table()

    def set_icons(self):
        self.set_icon("delete_btn","delete.svg")
        self.set_icon("edit_btn","edit.svg")
        self.set_icon("previous_btn","previous.svg")
        self.set_icon("next_btn","next.svg")
        self.set_icon("cancel_btn","cancel.svg")

    def update_pagination_counter(self):
        current_page_number = self.page + 1
        self.pagination_counter.setText(f"{current_page_number}")

    def connect_buttons(self):
        self.delete_btn_clicked()