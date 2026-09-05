from PyQt6.QtWidgets import (
    QTableView,
    QHeaderView,
)

from .shared_functions import TableViewModel, SharedFunctions

import logging
# uses this file's name for easier debugging
logger = logging.getLogger(__name__)

class ShowMainTables():
    def __init__(
        self, 
        table_view,
        fetch_function,
        table_header,
        header_widths,
        stretch_col,
        resize_content_col,
        next_btn,
        previous_btn,
        counter
        
    ):
        self._fetch_function = fetch_function
        self._table_header = table_header
        self._header_widths = header_widths
        self._stretch_col = stretch_col
        self._resize_content_col = resize_content_col
        
        self._table:QTableView = table_view
       
        # Pagination part
        
        next_btn.clicked.connect(self.next_page)
        previous_btn.clicked.connect(self.previous_page)
       

        self.page = 0
        self.page_size = 15
        self.pagination_counter = counter

        # load table 
        self.load_table()

    
    def load_table(self):
        
                
        table = self._table
        
        offset = self.page * self.page_size
        
        data = self._fetch_function(limit=self.page_size, offset=offset)
        
        
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
        data = self._fetch_function(limit=self.page_size, offset=self.page * self.page_size)

        if not data:
            self.page -= 1  # rollback
            return

        self.load_table()

    def previous_page(self):
        if self.page > 0:
            self.page -= 1
            self.load_table()

    def set_table_basic_settings(self):
        # Set table view headers and columns
        
        self.set_table_view_headers(
            self._table, 
            self._header_widths, 
            self._resize_content_col, 
            self._stretch_col
        )
      
        SharedFunctions.remove_rows_counter(self._table)
       
        SharedFunctions.make_rows_scrollable(self._table)

    def set_table_view_headers(
            self, 
            table, 
            fixed_cols:dict[int:int] | None = None, 
            resize_to_content_col:int | None = None , 
            stretch_col:int | None = None 
        ):
        """ Set A table view headers, columns fixed and stretch widths"""
       
        header = table.horizontalHeader()
        
        if fixed_cols is not None:
            # Set all to Interactive first
            for col in fixed_cols.keys():
                header.setSectionResizeMode(
                    col, 
                    QHeaderView.ResizeMode.Interactive
            )

            for col, width in fixed_cols.items():
                # Custom widths for first col
                table.setColumnWidth(col, width)
        
        if resize_to_content_col is not None:
            
            header.setSectionResizeMode(
                resize_to_content_col, 
                QHeaderView.ResizeMode.ResizeToContents
            )
        

        if stretch_col is not None:
            # Last column stretches
            header.setSectionResizeMode(stretch_col, QHeaderView.ResizeMode.Stretch)

    def update_pagination_counter(self):
        current_page_number = self.page + 1
        self.pagination_counter.setText(f"{current_page_number}")
