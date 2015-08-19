#!/bin/bash

python batteryPlotter.py

gnuplot < /ramtemp/plotter.sh

python -m pywws.Upload /data/weatherdata /ramtemp/battery_levels.png


