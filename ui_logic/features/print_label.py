from __future__ import annotations

import os
import win32print

from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter

import arabic_reshaper
from bidi.algorithm import get_display

from ui_logic.shared_functions import SharedFunctions 



# ============================================================
# CONFIGURATION
# ============================================================

settings = SharedFunctions().get_settings()

selected_size = settings["selected_size"] 

LABEL_WIDTH_MM = settings["label_size"][selected_size]["width"]
LABEL_HEIGHT_MM = settings["label_size"][selected_size]["height"]

# label_width_mm = settings["label_size"][selected_size]["width"]
# label_height_mm = settings["label_size"][selected_size]["height"]


# LABEL_WIDTH_MM = 50
# LABEL_HEIGHT_MM = 25

DPI = 203

# Change this if your labels have a different gap.
# Typical small labels may have around 2 mm.
LABEL_GAP_MM = 2.0

# Printer name as it appears in Windows.
# DEFAULT_PRINTER_NAME = settings["barcode_printer"]

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
        "module_width": 0.26,
        "module_height": 6,
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


def resize_barcode(
    image: Image.Image,
    max_width: int,
    max_height: int,
) -> Image.Image:

    # Keep the barcode dimensions independent.
    # Width is controlled by module_width.
    # Height is controlled by module_height.

    new_width = min(image.width, max_width)
    new_height = min(image.height, max_height)

    return image.resize(
        (new_width, new_height),
        Image.Resampling.NEAREST,
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
    label_width_mm: float = LABEL_WIDTH_MM,
    label_height_mm: float = LABEL_HEIGHT_MM,
) -> Image.Image:

    width = mm_to_dots(label_width_mm)
    height = mm_to_dots(label_height_mm)

    # Scale relative to the original 50 x 25 mm label.
    scale = min(
        label_width_mm / 50.0,
        label_height_mm / 25.0,
    )

    # White label.
    image = Image.new(
        "L",
        (width, height),
        255,
    )

    draw = ImageDraw.Draw(image)

    # --------------------------------------------------------
    # Margins
    # --------------------------------------------------------

    margin_x = mm_to_dots(1.5 * scale)

    usable_width = width - (margin_x * 2)

    # --------------------------------------------------------
    # Product name
    # --------------------------------------------------------

    name_font = get_fitting_product_font(
        draw,
        str(product_name),
        usable_width,
        starting_size=max(10, int(25 * scale)),
        minimum_size=max(8, int(14 * scale)),
    )

    name_y = mm_to_dots(0.7 * scale)

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

    barcode_max_width = usable_width
    barcode_max_height = mm_to_dots(9.5 * scale)

    barcode_image = resize_barcode(
        barcode_image,
        barcode_max_width,
        barcode_max_height,
    )

    barcode_x = (width - barcode_image.width) // 2

    barcode_y = mm_to_dots(5.2 * scale)

    image.paste(
        barcode_image,
        (barcode_x, barcode_y),
    )

    # --------------------------------------------------------
    # Barcode number
    # --------------------------------------------------------

    code_font = get_font(
        max(10, int(20 * scale))
    )

    code_y = (
        barcode_y
        + barcode_image.height
        + mm_to_dots(0.1 * scale)
    )

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

    separator_y = height - mm_to_dots(5.8 * scale)

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

    price_font = get_font(
        max(12, int(30 * scale))
    )

    price_y = separator_y + mm_to_dots(0.2 * scale)

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



def create_tspl_job(
    label_image: Image.Image,
    gap_mm: float = LABEL_GAP_MM,
    label_width_mm: float = LABEL_WIDTH_MM,
    label_height_mm: float = LABEL_HEIGHT_MM,
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
        f"SIZE {label_width_mm} mm,{label_height_mm} mm\r\n"
    ).encode("ascii")

    commands += (
        f"GAP {gap_mm} mm,0 mm\r\n"
    ).encode("ascii")

    commands += b"DIRECTION 1\r\n"

    commands += b"REFERENCE 0,0\r\n"

    commands += b"CLS\r\n"

    # --------------------------------------------------------
    # Bitmap
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



def print_product_labels(
    products
    # printer_name: str = DEFAULT_PRINTER_NAME,
    # gap_mm: float = 2.0,
    # label_width_mm: float = LABEL_WIDTH_MM,
    # label_height_mm: float = LABEL_HEIGHT_MM,
) -> int:

    # --------------------------------------------------------
    # Check printer
    # --------------------------------------------------------
    settings = SharedFunctions().get_settings()
    printer_name: str = settings["barcode_printer"]
    selected_size = settings["selected_size"] 
    label_width_mm: float = settings["label_size"][selected_size]["width"]
    label_height_mm: float = settings["label_size"][selected_size]["height"]

    gap_mm: float = 2.0

   
    printers = win32print.EnumPrinters(
        win32print.PRINTER_ENUM_LOCAL
        | win32print.PRINTER_ENUM_CONNECTIONS
    )

    available_printers = [
        printer[2]
        for printer in printers
    ]

    if printer_name not in available_printers:
        raise ValueError(
            f"Printer not found:\n\n"
            f"{printer_name}\n\n"
            f"Available printers:\n"
            + "\n".join(available_printers)
        )

    # --------------------------------------------------------
    # Open printer
    # --------------------------------------------------------

    printer_handle = win32print.OpenPrinter(
        printer_name
    )

    printed_count = 0

    try:

        for product in products:

            if len(product) != 4:
                raise ValueError(
                    "Each product must contain:\n"
                    "[product_name, quantity, price, barcode]"
                )

            product_name, quantity, price, barcode = product

            quantity = int(quantity)

            if quantity <= 0:
                continue

            # ------------------------------------------------
            # Create label
            # ------------------------------------------------

            label_image = create_label(
                str(product_name),
                float(price),
                str(barcode),
                label_width_mm,
                label_height_mm,
            )

            # ------------------------------------------------
            # Create TSPL data
            # ------------------------------------------------

            tspl_data = create_tspl_job(
                label_image,
                gap_mm=gap_mm,
                label_width_mm=label_width_mm,
                label_height_mm=label_height_mm,
            )

            # ------------------------------------------------
            # Print required quantity
            # ------------------------------------------------

            for _ in range(quantity):

                job_info = (
                    "Modeer Barcode Label",
                    None,
                    "RAW",
                )

                job_id = win32print.StartDocPrinter(
                    printer_handle,
                    1,
                    job_info,
                )

                try:

                    win32print.StartPagePrinter(
                        printer_handle
                    )

                    win32print.WritePrinter(
                        printer_handle,
                        tspl_data,
                    )

                    win32print.EndPagePrinter(
                        printer_handle
                    )

                finally:

                    win32print.EndDocPrinter(
                        printer_handle
                    )

                printed_count += 1

    finally:

        win32print.ClosePrinter(
            printer_handle
        )

    return printed_count


# ============================================================
# EXAMPLE
# ============================================================








if __name__ == "__main__":
    print(SharedFunctions.get_settings())

    # products = [
    #     ["محل بنوأمية جاهز", 1, 3800, 10000398334],
    #     # ["Samsung S25 Ultra Fold", 2, 7000.0, 4333435],
    # ]

    # printed = print_product_labels(
    #     products,
    #     printer_name="Xprinter XP-233B",
    #     gap_mm=2.0,
    #     label_width_mm=40, #40
    #     label_height_mm=20 ,#20
    # )

    # print(f"Successfully sent {printed} labels to the printer.")