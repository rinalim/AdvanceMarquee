#!/usr/bin/python3

import os, keyboard
from subprocess import *
from time import *
import xml.etree.ElementTree as ET

#INTRO = "/home/pi/PieMarqueeSPI/intro.mp4" # movio intro is disabled
VIEWER = "sudo fbi-marquee -T 2 -a -d /dev/fb1 -noverbose -cachemem 0 /tmp/pause.png /tmp/pause_1.png /tmp/pause_2.png"
INGAME_VIEWER = "sudo fbi-marquee -T 2 -a -blend 500 -t 5 -d /dev/fb1 -noverbose /tmp/pause.png"

arcade = ['arcade', 'fba', 'mame-advmame', 'mame-libretro', 'mame-mame4all']

def run_cmd(cmd):
# runs whatever in the cmd variable
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output.decode()

def update_image(src, dst):
    os.system('echo "' + src + '" >> /tmp/pi.log')
    if os.path.isfile(src) == True:
        prev_size = os.path.getsize(dst)
        os.system('cp "' + src + '" ' + dst)
        counts = 0
        while True:
            if os.path.getsize(dst) > 0 and os.path.getsize(dst) != prev_size:
                keyboard.press("n")
                sleep(0.01)
                keyboard.release("n")
                break
            else:
                counts = counts+1
                if counts >= 5:
                    break
                else:
                    sleep(0.1)
                    
def kill_fbi():
    #os.system("sudo pkill -9 fbi-marquee")
    keyboard.press("q")
    sleep(0.1)
    keyboard.release("q")

def kill_proc(name):
    ps_grep = run_cmd("ps -aux | grep " + name + "| grep -v 'grep'")
    if len(ps_grep) > 1: 
        os.system("killall " + name)
        
def is_running(pname):
    ps_grep = run_cmd("ps -ef | grep " + pname + " | grep -v grep")
    if len(ps_grep) > 1:
        return True
    else:
        return False

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
    
#if os.path.isfile(INTRO) == True:
#    run_cmd("mplayer -vo fbdev2:/dev/fb1 -zoom -xy 480 -demuxer lavf -framedrop " + INTRO + " </dev/null >/dev/null 2>&1")

doc = ET.parse("/opt/retropie/configs/all/PieMarqueeSPI/gamelist_short.xml")
root = doc.getroot()

if os.path.isfile("/tmp/pause.png") == False :
    os.system("touch /tmp/pause.png")
if os.path.isfile("/tmp/pause_1.png") == False :
    os.system("ln -s /tmp/pause.png /tmp/pause_1.png")
if os.path.isfile("/tmp/pause_2.png") == False :
    os.system("ln -s /tmp/pause.png /tmp/pause_2.png")

update_image("/home/pi/PieMarqueeSPI/marquee/system/maintitle.png", "/tmp/pause.png")
os.system(VIEWER + " &")
    
cur_imgname = "system/maintitle"
while True:
    sleep_interval = 1
    ingame = ""
    romname = ""
    sysname = ""
    pubpath = ""
    instpath = ""
    imgpath = ""
    ps_grep = run_cmd("ps -aux | grep emulators | grep -v 'grep'")
    if len(ps_grep) > 1:
        ingame="*"
        words = ps_grep.split()
        if 'advmame' in ps_grep:
            sysname = "arcade"
            romname = words[-1]
        else:
            pid = words[1]
            if os.path.isfile("/proc/"+pid+"/cmdline") == False:
                continue
            path = run_cmd("strings -n 1 /proc/"+pid+"/cmdline | grep roms")
            path = path.replace('/home/pi/RetroPie/roms/','')
            if len(path.replace('"','').split("/")) < 2:
                continue
            sysname = path.replace('"','').split("/")[0]
            if sysname in arcade:
                sysname = "arcade"
            romname = path.replace('"','').split("/")[-1].split(".")[0]
           
    elif os.path.isfile("/tmp/PieMarquee.log") == True: # Modified ES
        f = open('/tmp/PieMarquee.log', 'r')
        line = f.readline()
        f.close()
        words = line.split()
        if len(words) > 1 and words[0] == "Game:": # In the gamelist-> Game: /home/pi/.../*.zip
            path = line.replace('Game: ','')
            path = path.replace('/home/pi/RetroPie/roms/','')
            sysname = path.replace('"','').split("/")[0]
            if sysname in arcade:
                sysname = "arcade"
            romname = path.replace('"','').split("/")[-1].split(".")[0]
            sleep_interval = 0.1 # for quick view
        elif len(words) == 1:
            sysname = "system"
            if words[0] == "SystemView":
                romname = "maintitle"
            else:
                romname = words[0]

    else:
        sysname = "system"
        romname = "maintitle"
   
    if os.path.isfile("/home/pi/PieMarqueeSPI/marquee/" + sysname + "/" + romname + ".png") == True:
        imgname = sysname + "/" + romname
        if ingame == "*":
            publisher = get_publisher(romname)
            if os.path.isfile("/home/pi/PieMarqueeSPI/marquee/publisher/" + publisher + ".png") == True:
                pubpath = "/home/pi/PieMarqueeSPI/marquee/publisher/" + publisher + ".png"
            if os.path.isfile("/home/pi/PieMarqueeSPI/marquee/instruction/" + romname + ".png") == True:
                instpath = "/home/pi/PieMarqueeSPI/marquee/instruction/" + romname + ".png"
    elif os.path.isfile("/home/pi/PieMarqueeSPI/marquee/system/" + sysname + ".png") == True:
        imgname = "system/" + sysname
    else:
        imgname = "system/maintitle"
        
    if imgname+ingame != cur_imgname: # change marquee images
        if ingame == "*":
            kill_fbi()
            imgpath = "/home/pi/PieMarqueeSPI/marquee/" + imgname + ".png"
            update_image(imgpath, "/tmp/pause.png")
            cur_imgname = imgname+ingame
            os.system(INGAME_VIEWER + " " + pubpath + " " + instpath + " &")
        else:
            imgpath = "/home/pi/PieMarqueeSPI/marquee/" + imgname + ".png"
            update_image(imgpath, "/tmp/pause.png")
            if cur_imgname.endswith("*") == True:
                kill_fbi()
            cur_imgname = imgname+ingame

    if is_running("/home/pi/RetroPie-Setup/retropie_packages.sh") == True or is_running("dialog") == True:
        if is_running("fbi-marquee") == True:
            kill_fbi()
    elif is_running("fbi-marquee") == False: # if fbi-marquee failed, execute again
        os.system(VIEWER + " &")

    sleep(sleep_interval)
