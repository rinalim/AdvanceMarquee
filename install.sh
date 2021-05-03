sudo apt-get update
sudo apt-get install libjpeg8 -y
sudo apt-get install imagemagick -y
sudo apt-get install fbi -y
sudo apt-get install mplayer -y
sudo pip3 install wheel
sudo pip3 install keyboard

sudo cp /usr/bin/fbi /usr/bin/fbi-marquee

rm -rf /opt/retropie/configs/all/PieMarqueeSPI/
mkdir /opt/retropie/configs/all/PieMarqueeSPI/
cp -f -r ./PieMarqueeSPI /opt/retropie/configs/all/

sudo sed -i '/PieMarqueeSPI.py/d' /opt/retropie/configs/all/autostart.sh
sudo sed -i '1i\\sudo /usr/bin/python3 /opt/retropie/configs/all/PieMarqueeSPI/PieMarqueeSPI.py &' /opt/retropie/configs/all/autostart.sh

echo
echo "Setup Completed. Reboot after 3 Seconds."
sleep 3
reboot
