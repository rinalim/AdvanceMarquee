import os, sys, time, json

from datetime import datetime
from pathlib import Path
from PIL import ImageFont, Image

from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import ssd1322
from luma.core.virtual import viewport, snapshot
from luma.core.sprite_system import framerate_regulator

try:

    serial = spi()
    device = ssd1322(serial, mode="RGB")
    device.contrast(255)

    '''
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((30, 40), "Hello World", fill="white")
    while True:
        time.sleep(1)
    '''

    #img_path = str(Path(__file__).resolve().parent.joinpath('', 'kof98-logo.png'))
    #img_path = str(Path(__file__).resolve().parent.joinpath('', '1942.png'))
    img_path = str(Path(__file__).resolve().parent.joinpath('', sys.argv[1]))
    #img_path = str(Path(__file__).resolve().parent.joinpath('', 'kof98-index.png'))
    logo = Image.open(img_path).convert("RGBA")
    fff = Image.new(logo.mode, logo.size, (255,) * 4)

    background = Image.new("RGBA", device.size, "black")
    posn = ((device.width - logo.width) // 2, 0)

    while True:
        for angle in range(0, 360, 2):
            #rot = logo.rotate(angle, resample=Image.BILINEAR)
            #img = Image.composite(rot, fff, rot)
            #background.paste(img, posn)
            #device.display(background.convert(device.mode))
            device.display(logo.convert(device.mode))
            time.sleep(3)

except KeyboardInterrupt:
    pass
