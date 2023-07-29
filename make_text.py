from PIL import Image, ImageDraw, ImageFont
import random
import string

img = Image.new('RGB', (1000,800),color = (255,255,255))

draw = ImageDraw.Draw(img)
font = ImageFont.truetype("arial.ttf", 300)
text = ''.join([random.choice(string.ascii_letters).upper() for i in range(4)])
draw.text((0, 0),text,(0,0,0),font=font)
img.save('sample-out.png')