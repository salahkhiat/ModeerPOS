
"""
Product Label Generator
-----------------------

Input format:

products = [
    [product_name, quantity, price, barcode],
    ...
]

Example:

products = [
    ["Iphone 17 Pro Max", 5, 20000.0, "10000398334"],
    ["Samsung S25 Ultra Fold", 20, 7000.0, "4333435"],
]

Features:
    - A4
    - 6 columns
    - 13 rows
    - 78 labels per page
    - Quantity-based label duplication
    - Code128 barcodes
    - 2-13 digit barcode support
    - Arabic / English product names
    - Horizontal separator
    - Windows printing
"""


# ============================================================
# IMPORTS
# ============================================================

import os
import tempfile
import subprocess

from io import BytesIO

import arabic_reshaper
from bidi.algorithm import get_display

import barcode

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader

from barcode.writer import ImageWriter


# ============================================================
# CONFIGURATION
# ============================================================

class LabelConfig:

    # --------------------------------------------------------
    # PAGE
    # --------------------------------------------------------

    PAGE_WIDTH, PAGE_HEIGHT = A4

    COLUMNS = 6
    ROWS = 13

    MARGIN_LEFT = 8
    MARGIN_RIGHT = 8
    MARGIN_TOP = 8
    MARGIN_BOTTOM = 8

    HORIZONTAL_GAP = 0
    VERTICAL_GAP = 0

    # --------------------------------------------------------
    # BORDER
    # --------------------------------------------------------

    DRAW_BORDER = True
    BORDER_WIDTH = 0.3

    # --------------------------------------------------------
    # PRODUCT NAME
    # --------------------------------------------------------

    PRODUCT_NAME_FONT = "ArabicFont"
    PRODUCT_NAME_SIZE = 5.5

    # --------------------------------------------------------
    # BARCODE
    # --------------------------------------------------------

    BARCODE_HEIGHT = 13

    BARCODE_MAX_WIDTH_RATIO = 0.85

    BARCODE_NUMBER_FONT = "ArabicFont"
    BARCODE_NUMBER_SIZE = 5.5

    BARCODE_NUMBER_GAP = 1

    # --------------------------------------------------------
    # SEPARATOR
    # --------------------------------------------------------

    SEPARATOR_WIDTH = 0.3

    SEPARATOR_MARGIN = 3

    # Maximum gap between barcode number and separator.
    #
    # 1 PDF point ≈ 1.33 pixels at 96 DPI.
    # Therefore 1.5 pt ≈ 2 pixels.
    #
    # We keep this at 1.5 points.
    NUMBER_TO_SEPARATOR_GAP = 1.5

    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    PRICE_FONT = "ArabicFont"
    PRICE_SIZE = 7

    PRICE_SUFFIX = " DA"

    # --------------------------------------------------------
    # ARABIC FONT
    # --------------------------------------------------------

    # You can change this to another Arabic-compatible TTF.
    #
    # DejaVu Sans is usually available if installed.
    #
    # For maximum reliability in Modeer, I recommend putting
    # the font inside your application folder and referencing
    # that file directly.
    #
    
    FONT_PATH = os.path.join(
        os.path.dirname(__file__),
        "DejaVuSans.ttf"
    )


# ============================================================
# FONT SETUP
# ============================================================

def register_fonts():
    """
    Register the Unicode font used by the PDF.

    The font must support Arabic characters.
    """

    if not os.path.exists(LabelConfig.FONT_PATH):
        raise FileNotFoundError(
            "Arabic font was not found:\n"
            f"{LabelConfig.FONT_PATH}\n\n"
            "Please change LabelConfig.FONT_PATH "
            "to an existing Arabic-compatible .ttf font."
        )

    pdfmetrics.registerFont(
        TTFont(
            LabelConfig.PRODUCT_NAME_FONT,
            LabelConfig.FONT_PATH
        )
    )


# ============================================================
# ARABIC / RTL TEXT
# ============================================================

def prepare_text(text):
    """
    Prepare Arabic / RTL text for ReportLab.

    English and numbers continue to work normally.

    Example:

        "غطاء Iphone 17"

    becomes a properly shaped RTL string
    for ReportLab.
    """

    text = str(text)

    # Shape Arabic characters
    reshaped_text = arabic_reshaper.reshape(text)

    # Apply bidirectional algorithm
    display_text = get_display(reshaped_text)

    return display_text


# ============================================================
# BARCODE
# ============================================================

def generate_barcode_image(barcode_value):
    """
    Generate a Code128 barcode in memory.

    Code128 supports the requested variable length:
        2 digits
        5 digits
        8 digits
        13 digits
        etc.
    """

    barcode_value = str(barcode_value)

    barcode_class = barcode.get_barcode_class("code128")

    barcode_instance = barcode_class(
        barcode_value,
        writer=ImageWriter()
    )

    buffer = BytesIO()

    barcode_instance.write(
        buffer,
        options={
            "write_text": False,
            "module_height": LabelConfig.BARCODE_HEIGHT,
            "quiet_zone": 1,
            "font_size": 0,
        }
    )

    buffer.seek(0)

    return buffer


# ============================================================
# TEXT FITTING
# ============================================================

def fit_text(
    text,
    max_width,
    font_name,
    font_size
):
    """
    Shorten text when it doesn't fit inside the label.
    """

    text = prepare_text(text)

    if stringWidth(
        text,
        font_name,
        font_size
    ) <= max_width:

        return text

    suffix = "..."

    while text:

        candidate = text[:-1] + suffix

        if stringWidth(
            candidate,
            font_name,
            font_size
        ) <= max_width:

            return candidate

        text = text[:-1]

    return suffix


# ============================================================
# LABEL DIMENSIONS
# ============================================================

def calculate_label_dimensions():

    available_width = (
        LabelConfig.PAGE_WIDTH
        - LabelConfig.MARGIN_LEFT
        - LabelConfig.MARGIN_RIGHT
        - (
            (LabelConfig.COLUMNS - 1)
            * LabelConfig.HORIZONTAL_GAP
        )
    )

    available_height = (
        LabelConfig.PAGE_HEIGHT
        - LabelConfig.MARGIN_TOP
        - LabelConfig.MARGIN_BOTTOM
        - (
            (LabelConfig.ROWS - 1)
            * LabelConfig.VERTICAL_GAP
        )
    )

    label_width = (
        available_width
        / LabelConfig.COLUMNS
    )

    label_height = (
        available_height
        / LabelConfig.ROWS
    )

    return label_width, label_height


# ============================================================
# DRAW PRODUCT NAME
# ============================================================

def draw_product_name(
    pdf,
    product_name,
    x,
    y,
    label_width,
    label_height
):

    max_width = label_width - 4

    text = fit_text(
        product_name,
        max_width,
        LabelConfig.PRODUCT_NAME_FONT,
        LabelConfig.PRODUCT_NAME_SIZE
    )

    pdf.setFont(
        LabelConfig.PRODUCT_NAME_FONT,
        LabelConfig.PRODUCT_NAME_SIZE
    )

    text_width = stringWidth(
        text,
        LabelConfig.PRODUCT_NAME_FONT,
        LabelConfig.PRODUCT_NAME_SIZE
    )

    text_x = (
        x
        + (label_width - text_width) / 2
    )

    text_y = (
        y
        + label_height
        - 7
    )

    pdf.drawString(
        text_x,
        text_y,
        text
    )


# ============================================================
# DRAW BARCODE
# ============================================================

def draw_barcode(
    pdf,
    barcode_value,
    x,
    y,
    label_width,
    label_height
):

    barcode_buffer = generate_barcode_image(
        barcode_value
    )

    image = ImageReader(
        barcode_buffer
    )

    image_width, image_height = (
        image.getSize()
    )

    max_width = (
        label_width
        * LabelConfig.BARCODE_MAX_WIDTH_RATIO
    )

    scale = min(
        max_width / image_width,
        LabelConfig.BARCODE_HEIGHT / image_height
    )

    final_width = image_width * scale
    final_height = image_height * scale

    barcode_x = (
        x
        + (label_width - final_width) / 2
    )

    barcode_y = (
        y
        + label_height
        - 25
    )

    pdf.drawImage(
        image,
        barcode_x,
        barcode_y,
        width=final_width,
        height=final_height,
        preserveAspectRatio=True,
        mask="auto"
    )

    # --------------------------------------------------------
    # Barcode number
    # --------------------------------------------------------

    number_text = str(barcode_value)

    pdf.setFont(
        LabelConfig.BARCODE_NUMBER_FONT,
        LabelConfig.BARCODE_NUMBER_SIZE
    )

    number_width = stringWidth(
        number_text,
        LabelConfig.BARCODE_NUMBER_FONT,
        LabelConfig.BARCODE_NUMBER_SIZE
    )

    number_x = (
        x
        + (label_width - number_width) / 2
    )

    number_y = (
        barcode_y
        - LabelConfig.BARCODE_NUMBER_GAP
        - LabelConfig.BARCODE_NUMBER_SIZE
    )

    pdf.drawString(
        number_x,
        number_y,
        number_text
    )

    # Return the vertical position of the number.
    #
    # The separator needs this information so that the
    # distance between the number and separator stays tiny.
    return number_y


# ============================================================
# DRAW SEPARATOR
# ============================================================

def draw_separator(
    pdf,
    x,
    label_width,
    number_y
):
    """
    Draw the horizontal separator.

    It is positioned immediately below the barcode number.

    Maximum gap:
        ~1.5 PDF points
        ≈ 2 pixels at 96 DPI
    """

    pdf.setLineWidth(
        LabelConfig.SEPARATOR_WIDTH
    )

    separator_y = (
        number_y
        - LabelConfig.NUMBER_TO_SEPARATOR_GAP
    )

    pdf.line(
        x + LabelConfig.SEPARATOR_MARGIN,
        separator_y,
        x + label_width - LabelConfig.SEPARATOR_MARGIN,
        separator_y
    )

    return separator_y


# ============================================================
# DRAW PRICE
# ============================================================

def draw_price(
    pdf,
    price,
    x,
    separator_y,
    label_width
):
    """
    Draw the price immediately below the separator.
    """

    price_text = (
        f"{price}{LabelConfig.PRICE_SUFFIX}"
    )

    price_text = prepare_text(price_text)

    pdf.setFont(
        LabelConfig.PRICE_FONT,
        LabelConfig.PRICE_SIZE
    )

    text_width = stringWidth(
        price_text,
        LabelConfig.PRICE_FONT,
        LabelConfig.PRICE_SIZE
    )

    price_x = (
        x
        + (label_width - text_width) / 2
    )

    # Keep the price very close to the separator.
    price_y = (
        separator_y
        - LabelConfig.PRICE_SIZE
        - 1
    )

    pdf.drawString(
        price_x,
        price_y,
        price_text
    )


# ============================================================
# DRAW LABEL BORDER
# ============================================================

def draw_label_border(
    pdf,
    x,
    y,
    label_width,
    label_height
):

    if not LabelConfig.DRAW_BORDER:
        return

    pdf.setLineWidth(
        LabelConfig.BORDER_WIDTH
    )

    pdf.rect(
        x,
        y,
        label_width,
        label_height
    )


# ============================================================
# DRAW ONE LABEL
# ============================================================

def draw_label(
    pdf,
    product_name,
    price,
    barcode_value,
    x,
    y,
    label_width,
    label_height
):

    # Border
    draw_label_border(
        pdf,
        x,
        y,
        label_width,
        label_height
    )

    # Product name
    draw_product_name(
        pdf,
        product_name,
        x,
        y,
        label_width,
        label_height
    )

    # Barcode + number
    number_y = draw_barcode(
        pdf,
        barcode_value,
        x,
        y,
        label_width,
        label_height
    )

    # Horizontal separator
    separator_y = draw_separator(
        pdf,
        x,
        label_width,
        number_y
    )

    # Price
    draw_price(
        pdf,
        price,
        x,
        separator_y,
        label_width
    )


# ============================================================
# EXPAND PRODUCTS BY QUANTITY
# ============================================================

def expand_products(products):
    """
    Convert product quantities into individual labels.

    Example:

        ["iPhone", 3, 20000, "12345"]

    becomes three labels.
    """

    labels = []

    for product in products:

        if len(product) < 4:
            raise ValueError(
                "Each product must contain:\n"
                "[product_name, quantity, price, barcode]"
            )

        product_name = product[0]
        quantity = product[1]
        price = product[2]
        barcode_value = product[3]

        try:
            quantity = int(quantity)

        except (TypeError, ValueError):

            raise ValueError(
                f"Invalid quantity for "
                f"{product_name}: {quantity}"
            )

        if quantity < 0:
            raise ValueError(
                f"Quantity cannot be negative: "
                f"{quantity}"
            )

        for _ in range(quantity):

            labels.append([
                product_name,
                price,
                barcode_value
            ])

    return labels


# ============================================================
# CREATE PDF
# ============================================================

def create_labels_pdf(
    products,
    output_path
):
    """
    Generate the label PDF.
    """

    # Register Arabic font
    register_fonts()

    # Expand quantities
    labels = expand_products(products)

    if not labels:
        raise ValueError(
            "There are no labels to generate."
        )

    label_width, label_height = (
        calculate_label_dimensions()
    )

    pdf = canvas.Canvas(
        output_path,
        pagesize=A4
    )

    labels_per_page = (
        LabelConfig.COLUMNS
        * LabelConfig.ROWS
    )

    for index, label in enumerate(labels):

        product_name = label[0]
        price = label[1]
        barcode_value = label[2]

        # Position within current page
        position = (
            index % labels_per_page
        )

        column = (
            position
            % LabelConfig.COLUMNS
        )

        row = (
            position
            // LabelConfig.COLUMNS
        )

        # X
        x = (
            LabelConfig.MARGIN_LEFT
            + column
            * (
                label_width
                + LabelConfig.HORIZONTAL_GAP
            )
        )

        # Y
        #
        # PDF starts from bottom,
        # so row 0 is the top row.
        y = (
            LabelConfig.PAGE_HEIGHT
            - LabelConfig.MARGIN_TOP
            - (row + 1) * label_height
            - row
            * LabelConfig.VERTICAL_GAP
        )

        draw_label(
            pdf,
            product_name,
            price,
            barcode_value,
            x,
            y,
            label_width,
            label_height
        )

        # New page when current page is full
        is_last_label = (
            index == len(labels) - 1
        )

        page_full = (
            position
            == labels_per_page - 1
        )

        if page_full and not is_last_label:
            pdf.showPage()

    pdf.save()

    return output_path


# ============================================================
# WINDOWS PRINTING
# ============================================================

def print_pdf_windows(pdf_path):
    """
    Open the generated PDF so the user can print it.

    The user can select:
        - Physical printer
        - Microsoft Print to PDF
        - Any other installed printer
    """

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(pdf_path)

    subprocess.Popen(
        [
            "cmd",
            "/c",
            "start",
            "",
            "/wait",
            pdf_path
        ],
        shell=False
    )


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def label_generator(products):
    """
    Main function for Modeer.

    Example:

        my_products = [
            [
                "Iphone 17 Pro Max",
                5,
                20000.0,
                "10000398334"
            ],

            [
                "Samsung S25 Ultra Fold",
                20,
                7000.0,
                "4333435"
            ],

            [
                "غطاء هاتف سامسونج",
                10,
                1500.0,
                "123456789"
            ],
        ]

        label_generator(my_products)
    """

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".pdf",
        delete=False
    )

    temp_file.close()

    pdf_path = temp_file.name

    create_labels_pdf(
        products,
        pdf_path
    )

    print_pdf_windows(
        pdf_path
    )

    return pdf_path


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_products = [

        [
            "Iphone 17 Pro Max",
            5,
            20000.0,
            "10000398334"
        ],

        [
            "Samsung S25 Ultra Fold",
            20,
            7000.0,
            "4333435"
        ],

        [
            "USB Type C Cable",
            10,
            1200.0,
            "12345"
        ],

        [
            "غطاء هاتف سامسونج",
            10,
            1500.0,
            "123456789"
        ],

    ]

    label_generator(test_products)

