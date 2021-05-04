import sys, os
from pathlib import Path
from subprocess import *

def run_cmd(cmd):
# runs whatever in the cmd variable
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output.decode()
  
source_path = sys.argv[1]
dest_path = sys.argv[2]

source_path = str(Path(__file__).resolve().parent.joinpath('', sys.argv[1]))
dest_path = str(Path(__file__).resolve().parent.joinpath('', sys.argv[2]))
if source_path.endswith("/") == False:
    source_path = source_path+"/"
if dest_path.endswith("/") == False:
    dest_path = dest_path+"/"

if os.path.isdir(source_path) == False:
    print("source path is not valid")
else:
    if os.path.isdir(dest_path) == False:
        os.mkdir(dest_path)
    file_list = os.listdir(source_path)
    file_list.sort()
    for f in file_list:
        if ".png" in f:
            run_cmd('convert "' + source_path + f + '" -background black -alpha remove -resize 200x64^ -gravity center -extent 256x64 "' + dest_path + f + '"')
            print('convert "' + source_path + f + '" -background black -alpha remove -resize 200x64^ -gravity center -extent 256x64 "' + dest_path + f + '"')
        elif ".jpg" in f:
            run_cmd('convert "' + source_path + f + '" -resize 200x64^ -gravity center -extent 256x64 "' + dest_path + f.replace("jpg","png") + '"')
            print('convert "' + source_path + f + '" -resize 200x64^ -gravity center -extent 256x64 "' + dest_path + f.replace("jpg","png") + '"')
