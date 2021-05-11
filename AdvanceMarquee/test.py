import os, sys
from subprocess import *
from time import *
from pathlib import Path
from PIL import ImageFont, Image, ImageOps
from resizeimage import resizeimage
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas

# ssd1322, ssd1306, ili9341, waveshare35a, waveshare35b, framebuffer
SCREEN=sys.argv[1]

def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output.decode()

def get_device():
    if SCREEN == "ssd1322":
        from luma.oled.device import ssd1322
        serial = spi()
        device = ssd1322(serial, mode="RGB")
        device.contrast(255)
    elif SCREEN == "ssd1306":
        from luma.oled.device import ssd1306
        serial = i2c(port=2, address=0x3C)
        device = ssd1306(serial, mode="RGB")
    elif SCREEN == "ili9341":
        from luma.lcd.device import ili9341
        serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25,
             reset_hold_time=0.2, reset_release_time=0.2)
        device = ili9341(serial, active_low=False, width=320, height=240,
                     bus_speed_hz=32000000,
                     gpio_LIGHT=18)
    elif SCREEN == "waveshare35a":
        from luma.lcd.device import ili9486
        serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25,
             reset_hold_time=0.2, reset_release_time=0.2)
        device = ili9486(serial, active_low=False, width=320, height=480,
                 rotate=1, bus_speed_hz=31880000)
    elif SCREEN == "waveshare35b":
        from luma.lcd.device import ili9486
        serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25,
             reset_hold_time=0.2, reset_release_time=0.2)
        device = ili9486(serial, active_low=False, width=320, height=480,
                 rotate=3, bus_speed_hz=50000000)
    elif SCREEN == "framebuffer":
        from luma.core import device
        device = device.linux_framebuffer("/dev/fb1")
    else:
        print("Unkown screen type")
        sys.exit(0)
    return device

def show_img(path, device):
    img = Image.open(path).convert("RGBA")
    if device.width != img.width or device.height != img.height:
        img = resizeimage.resize_contain(
                img, device.size, resample=Image.ANTIALIAS, bg_color=(0,0,0,0))
    if SCREEN == "ili9341" or SCREEN == "waveshare35a":
        background = Image.new("RGB", device.size, "black")
        posn = ((device.width - img.width) // 2, (device.height - img.height) // 2)
        background.paste(img, posn)
        img = ImageOps.invert(background)
    return img

def change_img(img_path):
    show = show_img(img_path, device)
    device.display(show.convert(device.mode))

device = get_device()
img_path = str(Path(__file__).resolve().parent.joinpath('', sys.argv[2]))
change_img(img_path)
sleep(5)
