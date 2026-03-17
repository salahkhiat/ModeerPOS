from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QTableWidget, 
    QTableWidgetItem, 
    QAbstractItemView
)

from PyQt6.QtGui import QFont, QColor
from hijri_converter import Gregorian
from datetime import datetime
from typing import Dict, Any, List
import json, os, sys, random, winsound, logging
logger = logging.getLogger(__name__)

class SharedFunctions:
    def set_icon(self, btn_name, icon_name):
        icon_path = self.resource_path(f"./icons/{icon_name}")
        icon = QtGui.QIcon(icon_path)

        btn = getattr(self.ui, btn_name)
        btn.setIcon(icon)

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
            logger.debug("Running from PyInstaller bundle. Base path: %s", base_path)

        except AttributeError:
            base_path = os.path.abspath(".")
            logger.debug("Running in development mode. Base path: %s", base_path)

        full_path = os.path.join(base_path, relative_path)
        logger.debug("Resolved resource path: %s", full_path)

        return  full_path
    
    # get settings as dict 
    def get_settings(self) -> dict:
        return self.get_settings_info(self.get_settings_json_path())
    
    # Returns the Index of the current selected combobox item
    def get_current_combo_index(self,combo_name:str) -> int:
        return getattr(self.ui, combo_name).currentIndex()

    def current_date(self) -> str:
        try:
            hijri_date = self.get_settings().get("hijri_date", False)

            now = datetime.now()
            year, month, day = now.year, now.month, now.day

            if hijri_date:
                hijri = Gregorian(year, month, day).to_hijri()
                date_str = f"{hijri}"
                logger.debug("Returning Hijri date: %s", date_str)
                return date_str
            else:
                gregorian = Gregorian(year, month, day)
                date_str = f"{gregorian}"
                logger.debug("Returning Gregorian date: %s", date_str)
                return date_str

        except Exception as e:
            logger.error("Failed to get current date: %s", e, exc_info=True)
            # fallback: return Gregorian date string to avoid crashing
            return str(datetime.now().date())
    
    # check if settings.json file is exsits returns True, otherwise return False
    def is_settings_file_exists(self) -> bool:
        exists = False 
        for entry in os.scandir("."):
            if entry.is_file() and entry.name == "settings.json":
                exists =  True
                break 
        return exists
    
    # settings.json file path 
    def get_settings_json_path(self):
        return os.path.join(os.getcwd(), "settings.json")

    # Create setting.json file 
    def create_settings_file(self,settings_path):
        full_path = settings_path
        default_settings = {
            "hijri_date": True,
            "database_path": None,
            "database_name": "shop_data.db"
        }
        with open(full_path,"w") as file:
            json.dump(default_settings, file, indent=4)

    # get settings.json content
    def get_settings_info(self,settings_path): 
            settings = settings_path
            with open(settings,'r') as file:
                settings = json.load(file)
            return settings


    def fetch_then_put(self, table:str, column:str, combo:QComboBox) -> None:
        """
        Fetch table rows from the database as a List then, Then put them in combo.
        
        Args:
            table (str):  The table name.
            column (str): The table column.
            combo (QComboBox): The QComboBox.
        
        Example:
            >>> table = "Students"
            >>> column = "name"
            >>> combo = obj.ui.ComboBox
            >>> obj.fetch_then_put(table,column,combo)
            None
        """
        items = self.get_table_as_list(table,[column])
        
        # remove "-" from the list to make it appears first in combo
        items = list(items)
        if "-" in items:
            items.remove("-")
            combo.addItem("-")
            
        combo.addItems(items)
        
    def reverse_dict(self, dictionary:Dict[Any,Any]) -> Dict[Any,Any]:
     """
     Converting {Key:Value} to {Value:Key}

    Args:
        dictionary (Dict[Any,Any]): The original dictionary.
    Returns:
        Dict[Any,Any]: The reversed dictionary.
    Examples:
        >>> myDict = {1:"one", 2:"two"}
        >>> print(obj.reverse_dict(myDict))
        {"one":1, "two":2}
     """
     return {value:key for key, value in dictionary.items()}
    
    def generate_reference(self) -> int:
        """Return a random number between 1 to 1000000"""
        return random.randint(1,1000000)
    
 
    def is_in_table_widget(self,table: QTableWidget, target, column_index: int) -> bool:
        """Check if a target value exists in a specific column of a QTableWidget.

        Args:
            table (QTableWidget): The table widget to search in.
            target (Any): The value to search for. It will be converted to a string for comparison.
            column_index (int): The zero-based index of the column to search in.

        Returns:
            bool: True if the target value is found in the specified column, False otherwise.

        Raises:
            ValueError: If the column_index is out of range.
        """
        # Validate the column_index
        col_count = table.columnCount()
        if column_index < 0 or column_index >= col_count:
            raise ValueError(f"Column index {column_index} is out of range (0 .. {col_count - 1})")

        # Convert target to string for comparison
        target_str = str(target)
        
        # Loop through rows in the given column
        for row in range(table.rowCount()):
            item = table.item(row, column_index)
            if item is not None and item.text() == target_str:
                return True

        return False
    
    def q_table_column_as_list(self,table: QTableWidget, column_index: int) -> List[str]:
        """
        Extracts all values from a specific column in a QTableWidget by column index.

        Args:
            table (QTableWidget): The table to extract data from.
            column_index (int): The zero-based index of the column.

        Returns:
            List[str]: A list of strings representing the data in the specified column.

        Raises:
            ValueError: If the column index is out of range.
        """
        if column_index < 0 or column_index >= table.columnCount():
            raise ValueError(f"Column index {column_index} is out of range")

        result = []
        for row in range(table.rowCount()):
            item = table.item(row, column_index)
            result.append(item.text() if item else "")
        return result
    
    def add_list_in_qtable(self,table: QTableWidget, data: list):
        """
        Adds a list of values as a new row in a QTableWidget.

        :param table: QTableWidget instance
        :param data: list of values to insert
        """

        table.blockSignals(True)
        columns_count = len(data)

        # Ensure table has enough columns
        if table.columnCount() < columns_count:
            table.setColumnCount(columns_count)

        # Add new row at the end
        current_row = table.rowCount()
        table.insertRow(current_row)

        # --- Custom font for the new row ---
        custom_font = QFont()
        custom_font.setPointSize(16)
        custom_font.setBold(True)

        # Fill the new row with data
        for col, value in enumerate(data):
            item = QTableWidgetItem(str(value))
            item.setFont(custom_font)
            table.setItem(current_row, col, item)

        table.blockSignals(False)

    def play_success_sound(self):
        winsound.Beep(500, 700)

    def play_failure_sound(self):
        winsound.Beep(1500, 300)

    def calculate_total(self, price:str, quantity:str)-> int:
        return int(price) * int(quantity)
    
    def remove_rows_counter(self, table: QTableWidget):
        table.verticalHeader().setVisible(False)

    def make_item(self,text, font_size=18, bold=True, color=None, read_only=False ):
        item = QTableWidgetItem(str(text))
        if read_only is True:
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(font_size)
        font.setBold(bold)
        item.setFont(font)
        if color:
            item.setForeground(QColor(color))
        return item

    def set_table_properties(
        self,
        table: QTableWidget,
        headers: List[str],
        headers_width: List[int],
        header_font_size: int = 16
    ):
        # --- Validation ---
        if len(headers) != len(headers_width):
            raise ValueError("headers and headers_width must have the same length")

        if sum(headers_width) != 100:
            raise ValueError("headers_width must sum to 100 (%)")

        # --- Columns count ---
        table.setColumnCount(len(headers))

        # --- Header font ---
        header_font = QFont()
        header_font.setPointSize(header_font_size)
        header_font.setBold(True)

        # --- Set header titles ---
        for i, title in enumerate(headers):
            item = QTableWidgetItem(title)
            item.setFont(header_font)
            table.setHorizontalHeaderItem(i, item)

        # --- Calculate column widths (percent → pixels) ---
        total_width = table.viewport().width()

        for i, percent in enumerate(headers_width):
            header_width = int(total_width * percent / 100)
            table.setColumnWidth(i, header_width)
        self.remove_rows_counter(table)

    def make_rows_scrollable(self, table: QTableWidget) -> None:
        # 1. Make table rows selectable (full row).
        table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        # 2. Make the user can only select one row at a time.
        table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

    def update_variable_on_row_select(
            self, 
            table: QTableWidget = None, 
            variable: str = None, 
            column_index: int = None
    ) -> None:
        
        # Make QTable rows scrollable one by one
        self.make_rows_scrollable(table)
        
        # Connect to selection change signal
        def on_row_selected():
            selected_items = table.selectedItems()
            if selected_items:
                row = table.currentRow()
                item: QTableWidgetItem = table.item(row, column_index)
                if item:
                    setattr(self, variable, item.text())  

        # ✅ connect signal to update barcode whenever selection changes
        table.itemSelectionChanged.connect(on_row_selected)



 



    


