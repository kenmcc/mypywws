#!/bin/bash

git pull
python batteryPlotter.py

gnuplot < /ramtemp/plotter.sh

python -m pywws.Upload /data/weatherdata /ramtemp/battery_levels.png
python -m pywws.Upload /data/weatherdata /ramtemp/battery_2.txt
python -m pywws.Upload /data/weatherdata /ramtemp/battery_10.txt
python -m pywws.Upload /data/weatherdata /ramtemp/battery_3.txt
python -m pywws.Upload /data/weatherdata /ramtemp/battery_21.txt
python -m pywws.Upload /data/weatherdata /ramtemp/battery_summary.txt

now=`date +"%Y%m%d%H"
if [ "$now" -eq "2016090611" ]; then
    sudo reboot
fi

