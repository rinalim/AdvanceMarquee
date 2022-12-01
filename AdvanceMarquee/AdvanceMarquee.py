import os, sys
import xml.etree.ElementTree as ET
from subprocess import *
from time import *
from PIL import ImageFont, Image, ImageOps
from resizeimage import resizeimage
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas

# ssd1322, ssd1306, ili9341, waveshare35a, waveshare35b, framebuffer
SCREEN="ssd1322"

arcade = ['arcade', 'fba', 'fbneo', 'mame-advmame', 'mame-libretro', 'mame-mame4all']

def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output.decode()

def get_os():
    uname = run_cmd("uname -a")
    if "EmuELEC" in uname or "EMUELEC" in uname:
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
    show = show_img(img_path, device)
    device.display(show.convert(device.mode))

OS = get_os()
if OS == "emuelec":
    HOME = "/storage/AdvanceMarquee/"
    ROMPATH = "/storage/roms/"
elif OS == "retropie":
    HOME = "/home/pi/AdvanceMarquee/"
    ROMPATH = "/home/pi/RetroPie/roms/"
device = get_device()
doc = ET.parse(HOME+"AdvanceMarquee/gamelist_short.xml")
root = doc.getroot()

cur_imgname = ""
while True:
    sleep_interval = 1
    ingame = ""
    romname = ""
    sysname = ""
    pubpath = ""
    imgpath = ""
    if OS == "emuelec":
        ps_grep = run_cmd("/usr/bin/ps -ef | grep '{emuelecRunEmu' | grep -v 'grep'")
    elif OS == "retropie":
        ps_grep = run_cmd("ps -ef | grep emulators | grep -v 'grep'")
    if len(ps_grep) > 1: # Ingame
        ingame="*"
        words = ps_grep.split()
        if 'advmame' in ps_grep:
            sysname = "arcade"
            romname = words[-1]
        else:
            if OS == "emuelec":
                path = words[6]
                path = path.replace(ROMPATH,"")
                sysname = path.split("/")[0]
                if sysname in arcade:
                    sysname = "arcade"
                romname = path.split("/")[-1].rsplit('.', 1)[0]
            elif OS == "retropie":
                pid = words[1]
                if os.path.isfile("/proc/"+pid+"/cmdline") == False:
                    continue
                path = run_cmd("strings -n 1 /proc/"+pid+"/cmdline | grep roms")
                path = path.replace(ROMPATH,"")
                if len(path.replace('"','').split("/")) < 2:
                    continue
                sysname = path.replace('"','').split("/")[0]
                if sysname in arcade:
                    sysname = "arcade"
                romname = path.replace('"','').split("/")[-1].split(".")[0]
    else:
        sysname = "system"
        romname = "maintitle"

    if os.path.isfile(HOME + "marquee/" + sysname  + "/" + romname + ".png") == True:
        imgname = sysname + "/" + romname
        '''
        if ingame == "*":
            publisher = get_publisher(romname)
            if os.path.isfile(HOME + "marquee/publisher/" + publisher + ".png") == True:
                pubpath = HOME + "marquee/publisher/" + publisher + ".png"
        '''        
    elif os.path.isfile(HOME + "marquee/system/" + sysname + ".png") == True:
        imgname = "system/" + sysname
    else:
        imgname = "system/maintitle"

    if imgname+ingame != cur_imgname: # change marquee images
        '''
        if ingame == "*":
            if pubpath != "":
                imgpath = pubpath+"\n"+imgpath
        os.system('echo "' + imgpath + '" > /tmp/marquee.txt')
        sleep(0.2)
        '''
        cur_imgname = imgname+ingame
        change_img(HOME + "marquee/" + imgname + ".png")

    sleep(sleep_interval)
