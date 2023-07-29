import math
import random
import string
import sys

from PIL import Image, ImageDraw, ImageFont
import random
import string
import time
from tqdm import tqdm


# config 
NUM_LETTERS = 4
DISTANCE_BETWEEN_CIRCLES = 1
PROBABILITY_OF_COLOR_CHANGE = 0.55
FONT_SIZE = 300
MIN_DIAMETER = 7
MAX_DIAMETER = 17
# MIN_DIAMETER = 10
# MAX_DIAMETER = 27.6
ROTATION_STEP_SIZE = 5

if len(sys.argv) < 3:
    text = ' '.join([random.choice(string.ascii_letters).upper() for i in range(NUM_LETTERS)])
else:
    text = ' '.join(list(sys.argv[2]))

text = text.upper()



font = ImageFont.truetype("arial.ttf", FONT_SIZE)
_, _,width, height = font.getbbox(text)
img = Image.new('RGB', (width+120,height+120),color = (255,255,255))
draw = ImageDraw.Draw(img)
draw.text((60, 0),text,(0,0,0),font=font)
img.save('sample-out.png')


try:
    from scipy.spatial import cKDTree as KDTree
    import numpy as np
    IMPORTED_SCIPY = True
except ImportError:
    IMPORTED_SCIPY = False

BACKGROUND = (255, 255, 255)
TOTAL_CIRCLES = 1600#1650

color = lambda c: ((c >> 16) & 255, (c >> 8) & 255, c & 255)

# Original
# COLORS_ON = [
#     color(0xF9BB82), color(0xEBA170), color(0xFCCD84)
# ]
# COLORS_OFF = [
#     color(0x9CA594), color(0xACB4A5), color(0xBBB964),
#     color(0xD7DAAA), color(0xE5D57D), color(0xD1D6AF)
# ]

# First attempt
# COLORS_ON = [
#     color(0xC4BDB5), color(0xBBB4AC), color(0xF0C4B1)
# ]
# COLORS_OFF = [
#     color(0xFA7E91), color(0xF8C383), color(0xD59B6F),
#     color(0xF2C685), color(0xF4C98E), color(0x46B77D)
# ]

# From the 5
# COLORS_ON = [
#     color(0x968170), color(0xE1876F), color(0xA6B87C),
#     color(0xA3B579)#, color(0x54782E), color(0x8C4B29), color(0xAF9B54)
# ]
# COLORS_OFF = [
#     color(0xAB6D3B), color(0xAB9750), color(0x804825),
#     color(0x557E3A), color(0xAF9B54), color(0xCA422A),
#     color(0xDE7B5A), color(0xAD9859), color(0x783A23)
# ]

# From slide 19
# COLORS_ON = [
#     color(0xE38971), color(0x91AB6C), color(0x927D6C),
#     color(0x9AAC70)#, color(0x406925), color(0x8C4B29), color(0xAF9B54)
# ]
# COLORS_OFF = [
#     color(0xC25B37), color(0xA28D4E), color(0xC45E37),
#     color(0x9E884E),  color(0xAB9657), color(0x985A29), color(0x995B32), #,color(0x7E3E1D),
# ]


# From slide 5 Part 2
COLORS_ON = [
    color(0xE1876F),color(0x8B7665),color(0xA7B97D)
]
COLORS_OFF = [
    color(0x985930),color(0xC6754B),color(0x9A5B32),color(0x884A38),color(0xAD9662),color(0x608743)
]

COLOR_MAPPING = {
    COLORS_OFF[0]: COLORS_ON[0], COLORS_OFF[1]: COLORS_ON[0], COLORS_OFF[2]: COLORS_ON[1], COLORS_OFF[3]: COLORS_ON[1], COLORS_OFF[4]: COLORS_ON[2], COLORS_OFF[5]: COLORS_ON[2],
}

REVERSE_COLOR_MAPPING = {
    COLORS_ON[0]: [COLORS_OFF[0], COLORS_OFF[1]], COLORS_ON[1]: [COLORS_OFF[2], COLORS_OFF[3]], COLORS_ON[2]: [COLORS_OFF[4], COLORS_OFF[5]]
}


def select_swatch(image, circle):
    if overlaps_motive(image, circle):
        return COLORS_ON
    return COLORS_OFF

"""
    returns: list of circles
"""
def generate_cicles(image, min_diameter, max_diameter):
    circles = []
    image_width, image_height = image.size
    radius = random.triangular(min_diameter, max_diameter,
                                max_diameter * 0.8 + min_diameter * 0.2) / 2

        
    x_dist = random.uniform(-1*(image_width * 0.48 - radius), image_width * 0.48 - radius)
    y_dist = random.uniform(-1*(image_height * 0.48 - radius), image_height * 0.48 - radius)
    x = image_width  * 0.5 + x_dist
    y = image_height * 0.5 + y_dist
    colors = select_swatch(image, (x, y, radius, None))
    fill_color = random.choice(colors)
    circles.append((x, y, radius, fill_color))

    i = 0
    while i < len(circles):
        circle = circles[i]
        angle = random.uniform(0, math.pi * 2)
        for j in range(int(360/ROTATION_STEP_SIZE)):

            distance_from_center = random.uniform(1+circle[2]+radius, DISTANCE_BETWEEN_CIRCLES+circle[2]+radius)
            x = circle[0] + math.cos(angle) * distance_from_center
            y = circle[1] + math.sin(angle) * distance_from_center
            radius = random.triangular(min_diameter, max_diameter,
                                max_diameter * 0.8 + min_diameter * 0.2) / 2
            collision = check_cirlce_collision([x, y, radius], circles, image_width, image_height)
            
            if not collision:
                if overlaps_motive(image, (x, y, radius, None)) == overlaps_motive(image, circle):
                    if random.random() < PROBABILITY_OF_COLOR_CHANGE:
                        fill_color = circle[3]
                    else:
                        fill_color = random.choice(select_swatch(image, (x, y, radius, None)))
                elif(overlaps_motive(image, circle) == False):
                    fill_color = COLOR_MAPPING[circle[3]]
                else:
                    fill_color = random.choice(REVERSE_COLOR_MAPPING[circle[3]])
                circles.append((x, y, radius, fill_color))
            angle += ROTATION_STEP_SIZE*(math.pi /180)
        
        i += 1
        if i%100==0:
            print(i)

    return circles








def overlaps_motive(image, circle):
    x, y, r, _ = circle
    # points_x = [x, x, x, x-r, x+r, x-r*0.93, x-r*0.93, x+r*0.93, x+r*0.93]
    # points_y = [y, y-r, y+r, y, y, y+r*0.93, y-r*0.93, y+r*0.93, y-r*0.93]
    points_x = [x]
    points_y = [y]
    for xy in zip(points_x, points_y):
        if image.getpixel(xy)[:3] != BACKGROUND:
            return True

    return False


def circle_intersection(circle1, circle2):
    x1, y1, r1 = circle1[:3]
    x2, y2, r2 = circle2[:3]
    return (x2 - x1)**2 + (y2 - y1)**2 < (r2 + r1)**2


def circle_draw(draw_image, image, circle):
    x, y, r, fill_color = circle
    draw_image.ellipse((x - r, y - r, x + r, y + r),
                       fill=fill_color,
                       outline=fill_color)
    

    
def display_circles(draw_image, image, circles):
    for circle in circles:
        circle_draw(draw_image, image, circle)



def check_cirlce_collision(circle, circles, image_width, image_height):
    check_edges = circle[0] > (image_width * 0.02 + circle[2]) and circle[0] < image_width * 0.98 - circle[2] \
        and circle[1] > (image_height * 0.02 + circle[2]) and circle[1] < image_height * 0.98 - circle[2]

    return any(circle_intersection(circle, circle2) for circle2 in circles) or not check_edges


def main():
    image = Image.open(sys.argv[1]).convert('RGB')
    image2 = Image.new('RGB', image.size, BACKGROUND)
    draw_image = ImageDraw.Draw(image2)

    width, height = image.size

    min_diameter = MIN_DIAMETER #(width + height) / 200
    max_diameter = MAX_DIAMETER #(width + height) / 75
    circles = generate_cicles(image, min_diameter, max_diameter)
    display_circles(draw_image, image, circles)


    
    image2.show()

    time.sleep(10)

    image.show()


if __name__ == '__main__':
    main()
