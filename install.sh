pip3 install luma.oled
pip3 install luma.lcd
pip3 install python-resize-image

rm -rf /opt/retropie/configs/all/AdvanceMarquee/
mkdir /opt/retropie/configs/all/AdvanceMarquee/
cp -f -r ./AdvanceMarquee /opt/retropie/configs/all/

sudo sed -i '/AdvanceMarquee.py/d' /opt/retropie/configs/all/autostart.sh
sudo sed -i '1i\\sudo /usr/bin/python3 /opt/retropie/configs/all/AdvanceMarquee/AdvanceMarquee.py &' /opt/retropie/configs/all/autostart.sh

echo
echo "Setup Completed. Reboot after 3 Seconds."
sleep 3
reboot
