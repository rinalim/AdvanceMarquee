import os, sys, time, json

from subprocess import *
from datetime import datetime
from pathlib import Path
from PIL import ImageFont, Image, ImageOps
from resizeimage import resizeimage
from luma.core.interface.serial import spi
from luma.core.render import canvas

SCREEN="ili9341"

def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output.decode()

def get_os():
    uname = run_cmd("uname -a")
    if "EmuELEC" in uname:
        return "emuelec"
    elif "retropie" in uname:
        return "retropie"
    else:
        print("Unkown OS")
        sys.exit(0)
        
def get_device():
    if SCREEN == "ssd1322":
        from luma.oled.device import ssd1322
        serial = spi()
        device = ssd1322(serial, mode="RGB")
        device.contrast(255)
        return device
    elif SCREEN == "ili9341":
        from luma.lcd.device import ili9341
        serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25,
             reset_hold_time=0.2, reset_release_time=0.2)
        device = ili9341(serial, active_low=False, width=320, height=240,
                     bus_speed_hz=32000000,
                     gpio_LIGHT=18
        )
        return device
    elif SCREEN == "waveshare35a":
        from luma.lcd.device import ili9486
        serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25,
             reset_hold_time=0.2, reset_release_time=0.2)
        device = ili9486(serial, active_low=False, width=320, height=480,
                 rotate=1, bus_speed_hz=31880000)
        return device
    elif SCREEN == "waveshare35b":
        from luma.lcd.device import ili9486
        serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25,
             reset_hold_time=0.2, reset_release_time=0.2)
        device = ili9486(serial, active_low=False, width=320, height=480,
                 rotate=1, bus_speed_hz=50000000)
        return device
    else:
        print("Unkown screen type")
        sys.exit(0)
        
def show_img(path, os, device):
    img = Image.open(img_path).convert("RGBA")
    if device.width != img.width or device.height != img.height:
        img = resizeimage.resize_contain(
                img, device.size, resample=Image.ANTIALIAS, bg_color=(0,0,0,0))
    if SCREEN == "ili9341" or SCREEN == "waveshare35a":
        background = Image.new("RGB", device.size, "black")
        posn = ((device.width - img.width) // 2, (device.height - img.height) // 2)
        background.paste(img, posn)
        mg = ImageOps.invert(background)
    return img

os = get_os()
device = get_device()

try:
    img_path = str(Path(__file__).resolve().parent.joinpath('', sys.argv[1]))
    show = show_img(img_path, os, device)
    while True:
        device.display(img.convert(device.mode))
        time.sleep(3)

except KeyboardInterrupt:
    pass
