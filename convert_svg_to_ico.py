from PIL import Image
import cairosvg
import io
import os

# Convert SVG to PNG
png_data = cairosvg.svg2png(url="bari_logo.svg", output_width=256, output_height=256)

# Load PNG data into PIL Image
png_image = Image.open(io.BytesIO(png_data))

# Create ICO file
png_image.save("bari_logo.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

print("Conversion completed: bari_logo.svg -> bari_logo.ico")