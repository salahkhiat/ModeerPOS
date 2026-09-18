from __future__ import annotations

import os
import win32print

from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter

import arabic_reshaper
from bidi.algorithm import get_display


# ============================================================
# CONFIGURATION
# ============================================================

LABEL_WIDTH_MM = 50
LABEL_HEIGHT_MM = 25

DPI = 203

# Change this if your labels have a different gap.
# Typical small labels may have around 2 mm.
LABEL_GAP_MM = 2.0

# Printer name as it appears in Windows.
DEFAULT_PRINTER_NAME = "Xprinter XP-233B"

# Font used for the label.
# Arial is normally available on Windows and supports Arabic.
DEFAULT_FONT = r"C:\Windows\Fonts\arial.ttf"


# ============================================================
# UNIT CONVERSION
# ============================================================

def mm_to_dots(mm: float) -> int:
    """
    Convert millimeters to printer dots.

    XP-233B = 203 DPI ≈ 8 dots/mm.
    """
    return round(mm * DPI / 25.4)


# ============================================================
# FONT
# ============================================================

def get_font(size: int) -> ImageFont.FreeTypeFont:
    """
    Load the configured font.
    """
    if not os.path.exists(DEFAULT_FONT):
        raise FileNotFoundError(
            f"Font not found:\n{DEFAULT_FONT}\n"
            "Please change DEFAULT_FONT to a valid .ttf font."
        )

    return ImageFont.truetype(DEFAULT_FONT, size)


# ============================================================
# ARABIC TEXT
# ============================================================

def prepare_text(text: str) -> str:
    """
    Prepare Arabic text for Pillow.

    Pillow does not always handle Arabic shaping/bidi correctly
    by itself, so reshape Arabic characters and apply bidi ordering.
    """
    text = str(text)

    if any("\u0600" <= char <= "\u06FF" for char in text):
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)

    return text


# ============================================================
# DRAW CENTERED TEXT
# ============================================================

def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    image_width: int,
):
    """
    Draw text horizontally centered.
    """
    text = prepare_text(text)

    bbox = draw.textbbox((0, 0), text, font=font)

    text_width = bbox[2] - bbox[0]

    x = (image_width - text_width) // 2

    draw.text(
        (x, y),
        text,
        font=font,
        fill=0,
    )


# ============================================================
# FIT PRODUCT NAME
# ============================================================

def get_fitting_product_font(
    draw: ImageDraw.ImageDraw,
    product_name: str,
    max_width: int,
    starting_size: int = 25,
    minimum_size: int = 14,
):
    """
    Reduce the font size until the product name fits
    inside the label.
    """

    for size in range(starting_size, minimum_size - 1, -1):
        font = get_font(size)

        text = prepare_text(product_name)

        bbox = draw.textbbox(
            (0, 0),
            text,
            font=font,
        )

        width = bbox[2] - bbox[0]

        if width <= max_width:
            return font

    return get_font(minimum_size)


# ============================================================
# CREATE BARCODE
# ============================================================

def create_barcode(code: str) -> Image.Image:
    """
    Generate a Code 128 barcode.

    The human-readable number is NOT generated here because
    we draw it ourselves underneath the barcode.
    """

    code = str(code)

    Code128 = barcode.get_barcode_class("code128")

    writer_options = {
        "write_text": False,
        "module_width": 0.25,
        "module_height": 10,
        "quiet_zone": 1,
    }

    barcode_instance = Code128(
        code,
        writer=ImageWriter(),
    )

    filename = barcode_instance.save(
        "temp_barcode",
        options=writer_options,
    )

    image = Image.open(filename).convert("L")

    # Delete temporary PNG.
    try:
        os.remove(filename)
    except OSError:
        pass

    return image


# ============================================================
# FIT BARCODE
# ============================================================

def resize_barcode(
    barcode_image: Image.Image,
    max_width: int,
    max_height: int,
) -> Image.Image:
    """
    Resize barcode while keeping its aspect ratio.
    """

    original_width, original_height = barcode_image.size

    scale_x = max_width / original_width
    scale_y = max_height / original_height

    scale = min(scale_x, scale_y)

    new_width = max(1, int(original_width * scale))
    new_height = max(1, int(original_height * scale))

    return barcode_image.resize(
        (new_width, new_height),
        Image.Resampling.LANCZOS,
    )


# ============================================================
# CONVERT IMAGE TO TSPL BITMAP DATA
# ============================================================

def image_to_tspl_bitmap(image: Image.Image) -> bytes:
    """
    Convert a PIL 1-bit image into TSPL BITMAP format.

    TSPL:
        1 = printed / black
        0 = blank / white
    """

    image = image.convert("1")

    width, height = image.size

    if width % 8 != 0:
        raise ValueError(
            "Image width must be divisible by 8 for TSPL bitmap."
        )

    bytes_per_row = width // 8

    bitmap = bytearray()

    pixels = image.load()

    for y in range(height):

        for byte_x in range(bytes_per_row):

            byte = 0

            for bit in range(8):

                x = byte_x * 8 + bit

                pixel = pixels[x, y]

                # PIL:
                # 0   = black
                # 255 = white
                #
                # TSPL:
                # 1 = printed
                # 0 = blank

                if pixel != 0:
                    byte |= (1 << (7 - bit))

            bitmap.append(byte)

    return bytes(bitmap)

def create_label(
    product_name: str,
    price: float,
    code: str,
) -> Image.Image:

    width = mm_to_dots(LABEL_WIDTH_MM)
    height = mm_to_dots(LABEL_HEIGHT_MM)

    # White label background.
    image = Image.new(
        "L",
        (width, height),
        255,
    )

    draw = ImageDraw.Draw(image)

    # --------------------------------------------------------
    # Margins
    # --------------------------------------------------------

    margin_x = mm_to_dots(1.5)

    usable_width = width - (margin_x * 2)

    # --------------------------------------------------------
    # Product name
    # --------------------------------------------------------

    name_font = get_fitting_product_font(
        draw,
        str(product_name),
        usable_width,
        starting_size=25,
        minimum_size=14,
    )

    name_y = mm_to_dots(0.7)

    draw_centered_text(
        draw,
        str(product_name),
        name_y,
        name_font,
        width,
    )

    # --------------------------------------------------------
    # Barcode
    # --------------------------------------------------------

    barcode_image = create_barcode(str(code))

    # Bigger barcode
    barcode_max_width = usable_width
    barcode_max_height = mm_to_dots(9.5)

    barcode_image = resize_barcode(
        barcode_image,
        barcode_max_width,
        barcode_max_height,
    )

    barcode_x = (width - barcode_image.width) // 2

    barcode_y = mm_to_dots(5.2)

    image.paste(
        barcode_image,
        (barcode_x, barcode_y),
    )

    # --------------------------------------------------------
    # Barcode number
    # --------------------------------------------------------

    code_font = get_font(20)

    code_y = barcode_y + barcode_image.height + mm_to_dots(0.1)

    draw_centered_text(
        draw,
        str(code),
        code_y,
        code_font,
        width,
    )

    # --------------------------------------------------------
    # Separator
    # --------------------------------------------------------

    separator_y = height - mm_to_dots(5.8)

    draw.line(
        (
            margin_x,
            separator_y,
            width - margin_x,
            separator_y,
        ),
        fill=0,
        width=1,
    )

    # --------------------------------------------------------
    # Price
    # --------------------------------------------------------

    price_text = f"{price:,.1f} دج"

    # Much bigger price
    price_font = get_font(30)

    price_y = separator_y + mm_to_dots(0.2)

    draw_centered_text(
        draw,
        price_text,
        price_y,
        price_font,
        width,
    )

    # --------------------------------------------------------
    # Convert to pure 1-bit image
    # --------------------------------------------------------

    image = image.convert("1")

    return image


# ============================================================
# BUILD TSPL COMMAND
# ============================================================

def create_tspl_job(
    label_image: Image.Image,
    gap_mm: float = LABEL_GAP_MM,
) -> bytes:

    width, height = label_image.size

    if width % 8 != 0:
        raise ValueError(
            "Label width must be divisible by 8."
        )

    bitmap_width_bytes = width // 8

    bitmap_data = image_to_tspl_bitmap(label_image)

    commands = bytearray()

    # --------------------------------------------------------
    # Label configuration
    # --------------------------------------------------------

    commands += (
        f"SIZE {LABEL_WIDTH_MM} mm,{LABEL_HEIGHT_MM} mm\r\n"
    ).encode("ascii")

    commands += (
        f"GAP {gap_mm} mm,0 mm\r\n"
    ).encode("ascii")

    commands += b"DIRECTION 1\r\n"

    commands += b"REFERENCE 0,0\r\n"

    commands += b"CLS\r\n"

    # --------------------------------------------------------
    # Bitmap
    #
    # x = 0
    # y = 0
    # width = bytes
    # height = dots
    # mode = 0
    # --------------------------------------------------------

    commands += (
        f"BITMAP 0,0,{bitmap_width_bytes},{height},0,"
    ).encode("ascii")

    commands += bitmap_data

    commands += b"\r\n"

    commands += b"PRINT 1,1\r\n"

    return bytes(commands)


# ============================================================
# SEND RAW DATA TO WINDOWS PRINTER
# ============================================================

def send_to_printer(
    printer_name: str,
    data: bytes,
):
    """
    Send raw TSPL bytes directly to a Windows printer.
    """

    handle = win32print.OpenPrinter(printer_name)

    try:
        job = win32print.StartDocPrinter(
            handle,
            1,
            ("Python Label Printing", None, "RAW"),
        )

        try:
            win32print.StartPagePrinter(handle)

            win32print.WritePrinter(
                handle,
                data,
            )

            win32print.EndPagePrinter(handle)

        finally:
            win32print.EndDocPrinter(handle)

    finally:
        win32print.ClosePrinter(handle)


# ============================================================
# MAIN FUNCTION
# ============================================================

def print_product_labels(
    products,
    printer_name: str = DEFAULT_PRINTER_NAME,
    gap_mm: float = LABEL_GAP_MM,
):
    """
    Print product labels.

    products format:

        [
            [product_name, quantity, price, barcode],
            ...
        ]

    Example:

        products = [
            ["Iphone 17 Pro Max", 5, 20000.0, 10000398334],
            ["Samsung S25 Ultra Fold", 20, 7000.0, 4333435],
        ]

    Quantity controls the number of physical labels.
    """

    if not products:
        raise ValueError("products cannot be empty.")

    # Check that printer exists.
    available_printers = [
        printer[2]
        for printer in win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL
            | win32print.PRINTER_ENUM_CONNECTIONS
        )
    ]

    if printer_name not in available_printers:
        raise ValueError(
            f"Printer not found:\n\n"
            f"{printer_name}\n\n"
            f"Available printers:\n"
            + "\n".join(available_printers)
        )

    total_labels = 0

    for product in products:

        if len(product) != 4:
            raise ValueError(
                "Each product must contain:\n"
                "[name, quantity, price, barcode]"
            )

        product_name, quantity, price, code = product

        # ----------------------------------------------------
        # Validate quantity
        # ----------------------------------------------------

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            raise ValueError(
                f"Invalid quantity for {product_name!r}: {quantity}"
            )

        if quantity <= 0:
            raise ValueError(
                f"Quantity must be greater than 0 "
                f"for {product_name!r}."
            )

        # ----------------------------------------------------
        # Validate barcode
        # ----------------------------------------------------

        if code is None or str(code).strip() == "":
            raise ValueError(
                f"Barcode cannot be empty for {product_name!r}."
            )

        # ----------------------------------------------------
        # Validate price
        # ----------------------------------------------------

        try:
            price = float(price)
        except (TypeError, ValueError):
            raise ValueError(
                f"Invalid price for {product_name!r}: {price}"
            )

        # ----------------------------------------------------
        # Render ONE label
        # ----------------------------------------------------

        label_image = create_label(
            product_name=str(product_name),
            price=price,
            code=str(code),
        )

        # ----------------------------------------------------
        # Create TSPL for ONE label
        # ----------------------------------------------------

        tspl_data = create_tspl_job(
            label_image,
            gap_mm=gap_mm,
        )

        # ----------------------------------------------------
        # Print quantity times
        # ----------------------------------------------------

        for _ in range(quantity):

            send_to_printer(
                printer_name,
                tspl_data,
            )

            total_labels += 1

    return total_labels


# ============================================================
# EXAMPLE
# ============================================================

if __name__ == "__main__":

    products = [
        ["شاحن هواوي أصلي M20", 1, 20000.0, 10000398334],
        ["Samsung S25 Ultra Fold", 2, 7000.0, 4333435],
    ]

    printed = print_product_labels(
        products,
        printer_name="Xprinter XP-233B",
        gap_mm=2.0,
    )

    print(f"Successfully sent {printed} labels to the printer.")