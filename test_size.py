from PIL import ImageFont

# Load the font (you'll need to have the specific .ttf file)
font = ImageFont.truetype("arial.ttf", 300)

# The text to be measured
text = "REBORT"

# Get the width and height of the text
width, height = font.getsize(text)

print(f"Width: {width}, Height: {height}")