from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from ui_logic.database_manager import DatabaseManager as mgr
# -------------------------
# Data
# -------------------------
a = mgr()

products = [list(product) for product in a.get_products_list()]


header = ["كودبار", "الإسم", "الكمية", "الشراء بـ", "البيع بـ", "غير"]
products.insert(0,header)

data = [
    ["Product", "Quantity", "Price", "Total", "Date"],

    ["iPhone 13", 2, "50000", "100000", "01/09/2026"],
    ["Samsung A54", 1, "40000", "40000", "02/09/2026"],
    ["Redmi Note 12", 3, "25000", "75000", "03/09/2026"],
    ["Nokia G20", 1, "15000", "15000", "04/09/2026"],
    # Add hundreds or thousands of rows here...
]


# -------------------------
# Create PDF
# -------------------------

doc = SimpleDocTemplate(
    "sales_report2.pdf",
    pagesize=A4,
    rightMargin=40,
    leftMargin=40,
    topMargin=40,
    bottomMargin=40
)


# -------------------------
# Create table
# -------------------------

table = Table(
    products,
    repeatRows=1,       # Repeat header on every page
    hAlign="CENTER"     # Center table horizontally
)


# -------------------------
# Table appearance
# -------------------------

table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

    ("GRID", (0, 0), (-1, -1), 1, colors.black),

    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))


# -------------------------
# Build PDF
# -------------------------

doc.build([table])