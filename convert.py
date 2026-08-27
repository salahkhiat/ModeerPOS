from pathlib import Path
from PIL import Image
import pillow_heif

# Folder containing your HEIC images
folder = Path("images")

# Register HEIC support
pillow_heif.register_heif_opener()

# Convert every HEIC file
for heic_file in folder.glob("*"):
    if heic_file.suffix.lower() in [".heic", ".heif"]:
        jpg_file = heic_file.with_suffix(".jpg")

        image = Image.open(heic_file)
        image = image.convert("RGB")
        image.save(jpg_file, "JPEG", quality=95)

        print(f"Converted: {heic_file.name} -> {jpg_file.name}")

print("Done!")