import os, sys, time, json
import xml.etree.ElementTree as ET
from subprocess import *
from time import *
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

def get_publisher(romname):
    filename = romname+".zip"
    publisher = ""
    for item in root:
        if filename in item.findtext('path'):
            publisher = item.findtext('publisher')
            break
    if publisher == "":
        return ""
    words = publisher.split()
    return words[0].lower()

def change_img(img_path):
    show = show_img(img_path, os, device)
    device.display(img.convert(device.mode))

doc = ET.parse(ROOT+"PieMarquee2/PieMarquee2/gamelist_short.xml")
root = doc.getroot()
os = get_os()
device = get_device()

cur_imgname = ""
while True:
    sleep_interval = 1
    ingame = ""
    romname = ""
    sysname = ""
    pubpath = ""
    imgpath = ""
    ps_grep = run_cmd("ps -ef | grep '{emuelecRunEmu' | grep -v 'grep'")
    if len(ps_grep) > 1: # Ingame
        ingame="*"
        words = ps_grep.split()
        if 'advmame' in ps_grep:
            sysname = "arcade"
            romname = words[-1]
        else:
            '''
            pid = words[1]
            if os.path.isfile("/proc/"+pid+"/cmdline") == False:
                continue
            path = run_cmd("strings -n 1 /proc/"+pid+"/cmdline | grep roms")
            path = path.replace('/home/pi/RetroPie/roms/','')
            if len(path.replace('"','').split("/")) < 2:
                continue
            sysname = path.replace('"','').split("/")[0]
            '''
            path = words[6]
            path = path.replace('/storage/roms/','')
            sysname = path.split("/")[0]
            if sysname in arcade:
                sysname = "arcade"
            romname = path.split("/")[-1].rsplit('.', 1)[0]
    else:
        sysname = "system"
        romname = "maintitle"

    #print(ROOT + "marquee/" + sysname  + "/" + romname + ".png")
    if os.path.isfile(ROOT + "marquee/" + sysname  + "/" + romname + ".png") == True:
        imgname = sysname + "/" + romname
        if ingame == "*":
            publisher = get_publisher(romname)
            if os.path.isfile(ROOT + "marquee/publisher/" + publisher + ".png") == True:
                pubpath = ROOT + "marquee/publisher/" + publisher + ".png"
    elif os.path.isfile(ROOT + "marquee/system/" + sysname + ".png") == True:
        imgname = "system/" + sysname
    else:
        imgname = "system/maintitle"

    if imgname+ingame != cur_imgname: # change marquee images
        imgpath = "/home/pi/PieMarquee2/marquee/" + imgname + ".png"
        if ingame == "*":
            if pubpath != "":
                imgpath = pubpath+"\n"+imgpath
        os.system('echo "' + imgpath + '" > /tmp/marquee.txt')
        sleep(0.2)
        cur_imgname = imgname+ingame

        change_img(ROOT + "marquee/" + sysname  + "/" + romname + ".png")
        print(ROOT + "marquee/" + sysname  + "/" + romname + ".png")

    sleep(sleep_interval)
