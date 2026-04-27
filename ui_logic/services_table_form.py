from .base_form import Form
from PyQt6.QtWidgets import (
    QTableView, 
    QHeaderView, 
    QMessageBox,
    QComboBox
)
from .shared_functions import TableViewModel

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ServicesTableForm(Form):

    def __init__(self,base_form):
        super().__init__(base_form)

        self.setWindowTitle("سجل الخدمات التي تم تقديمها")

        # set icons
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
        self.columns_header = ["المعرف", "الوصف", "الزبون", "الصنف", "السعر", "الإيداع", "التاريخ"]
        
        self.load_table()

        # Search box
        search_box = self.ui.search_box
        search_box.textChanged.connect(self.load_table)
        self.keyword = None 
       

    def load_table(self, keyword=None):
        if keyword:
            self.keyword = keyword

        table: QTableView = self.ui.table
        
        offset = self.page * self.page_size
        
        
        data = self.get_services_list(keyword=keyword, limit=self.page_size, offset=offset)

        self.model = TableViewModel(data, self.columns_header)

        table.setModel(self.model)

        self.set_table_basic_settings(table)

        # 🔥 update pagination counter
        self.update_pagination_counter()

        self.selected_piece_row = None

        # selected model
        selection_model = table.selectionModel()
        selection_model.selectionChanged.connect(self.on_row_selected)  
    
    def on_row_selected(self, selected, deselected):
        indexes = selected.indexes()
        
        if indexes:
            row = indexes[0].row()
            self.selected_piece_row = self.model._data[row]

    def next_page(self):
        self.page += 1
        data = self.get_services_list(keyword=self.keyword, limit=self.page_size, offset=self.page * self.page_size)

        if not data:
            self.page -= 1  # rollback
            return

        self.load_table(keyword=self.keyword)

    def previous_page(self):
        if self.page > 0:
            self.page -= 1
            self.load_table(keyword=self.keyword)
    
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

    def set_table_basic_settings(self, table):
        # Set table view headers and columns
        cols_widths = { 2:140, 3:120, 4:90, 5:90, 6:180 }
        stretch_col = 1
        resize_to_content_col = 0
        self.set_table_view_headers(table, cols_widths, resize_to_content_col, stretch_col)

        # make a row scrollable
        self.remove_rows_counter(table)
        self.make_rows_scrollable(table)

    def update_pagination_counter(self):
        current_page_number = self.page + 1
        # this line prevent my table to appears 
        self.pagination_counter.setText(f"{current_page_number}")

    def set_icons(self):

        self.set_icon("delete_btn","delete.svg")
        self.set_icon("edit_btn","edit.svg")
        self.set_icon("add_btn","add.svg")
        self.set_icon("previous_btn","previous.svg")
        self.set_icon("next_btn","next.svg")
        self.set_icon("cancel_btn","cancel.svg")
    
    def search_box(self, search_word: str) -> None:
        search_word = str(search_word).strip()
        
    





        