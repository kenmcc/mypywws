import struct
import urllib
import os
import datetime
from datalogger import *
import array, fcntl, sys

import logging
from logging.handlers import TimedRotatingFileHandler

#logging.basicConfig(format='%(asctime)s %(message)s', filename='/data/logs/tempreader.log',level=logging.DEBUG)
log = logging.getLogger("TempReader")
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler = TimedRotatingFileHandler("/data/logs/tempreader.log",
                                       when="d",
                                       interval=1,
                                       backupCount=7)
handler.setFormatter(formatter)
log.addHandler(handler)

fd = os.open("/dev/rfm12b.0.1",  os.O_NONBLOCK|os.O_RDWR)
localURI="http://192.168.1.31/emoncms/input/post.json?apikey=d959950e0385107e37e2457db27b781e&node="
remoteURI="http://emoncms.org/input/post.json?apikey=a6958b2d85dfdfab9406e1e786e38249&node="
goatstownURI="http://goatstownweather.hostoi.com/emoncms/input/post.json?apikey=0f170b829035f4cde06637f953852333&node="

def dbgPrint(theString):
   log.info(theString)
   print theString

if len(sys.argv)== 2:
   if sys.argv[1] == "9600":
     dbgPrint("Setting baudrate to 9600")
     buf = array.array('h',[0x23])
     fcntl.ioctl(fd, 1074033160, buf, 1)

     fcntl.ioctl(fd, -2147192317, buf, 1)
     if buf[0] == 35:
        dbgPrint("Successfully")

logger = dataLogger("/data/weather.db")
fileLogger = fileDataLogger("/data/weatherdata")

run=True
while run == True:
    try:
        data=None
        jsonStr= ""
        data = os.read(fd, 66)
        node, len = struct.unpack("BB", data[:2])
        now=datetime.now().strftime("%Y%m%d_%H:%M")
        #print now, node, len
        if node == 2:
          temp, batt, pressure, humidity = struct.unpack("hhii", data[2:])
          fields = ({"field": "node", "value": str(node)}, 
                    {"field": "batt", "value": str(float(batt)/1000)}, 
                    {"field": "temp", "value": str(float(temp)/1000)},
                    {"field": "pressure", "value": str(float(pressure))},
                    {"field": "humidity", "value": str(int(humidity)/100)})
          logger.insert(fields)
          fileLogger.insert(fields)
          dbgPrint("Temp {0}, batt {1}, pressure {2}, humidity{3}".format(temp, batt, pressure, humidity))

        elif node == 3 and len == 10:
          rain,batt,a,b,c = struct.unpack("hhhhh", data[2:])
          fields = ({"field": "node", "value": str(node)}, 
                    {"field": "batt", "value": str(float(batt)/1000)}, 
                    {"field": "rain", "value": str(float(rain)/100)})
          logger.insert(fields)
          fileLogger.insert(fields)
          dbgPrint("Rain {0}, batt {1}".format(rain, batt))

        elif node == 9 and len == 16:
          dbgPrint("WH1080")
          temp,batt,humidity, wind_avg, wind_gust,wind_dir, rain = struct.unpack("ihhhhhh", data[2:])
          temp=temp/10.0
          fields = ({"field": "node", "value": str(node)}, 
                    {"field": "batt", "value": str(batt)}, 
                    {"field": "humidity", "value": str(humidity)}, 
                    {"field": "wind_avg", "value": str(wind_avg)}, 
                    {"field": "wind_gust", "value": str(wind_gust)}, 
                    {"field": "wind_dir", "value": str(wind_dir)}, 
                    {"field": "temp", "value": str(temp)}, 
                    {"field": "rain", "value": str(float(rain)/10)}
                    )
	  logger.insert(fields)
          fileLogger.insert(fields)
          dbgPrint("WH1080: {0} {1} {2} {3} {4} {5} {6}".format(temp, batt, humidity, wind_avg, wind_gust, wind_dir, rain))
 
        elif node >= 10 and node < 20 and len == 4:
                temp,batt = struct.unpack("hh", data[2:])
                if temp > -2000 and temp < 4000:
                  dbgPrint("Got node {0}, temp {1}, batt {2} ".format(node, temp, batt))
                  fields = ({"field": "node", "value": str(node)}, 
                            {"field": "batt", "value": str(float(batt)/1000)}, 
                            {"field": "temp", "value": str(float(temp)/100)})
                  logger.insert(fields)
                  fileLogger.insert(fields)
                  jsonStr = "temp:"+str(float(temp/100.0))+",batt:"+str(float(batt/1000.0))
        elif node == 20 and len == 8: # this is a pressure sensor 
          dbgPrint("pressure sensor")
          temp, batt, pressure = struct.unpack("hhi", data[2:])
          if temp >-2000 and temp < 40000 and pressure >900 and pressure < 1100:
                 dbgPrint("Got temp {0}, battery {1}, pressure {2} ".format( temp, batt, pressure))
                 jsonStr = "temp:"+str(float(temp/10.0))
                 jsonStr += ",batt:"+str(float(batt/1000.0))
                 jsonStr += ",pressure:"+str(pressure)  
        elif node == 21 and len == 5:
            temp, batt, other = struct.unpack("hhb", data[2:])
            print node, temp, batt, other
            switchstat = ["'OFF'", "'ON'", "'STAY'"]
            fields = ({"field": "node", "value": str(node)}, 
                      {"field": "batt", "value": str(float(batt)/1000)}, 
                      {"field": "temp", "value": str(float(temp)/100)},
                      {"field": "switch", "value": str(switchstat[int(other)])})
            try:
              logger.insert(fields)
              fileLogger.insert(fields)
            except:
              pass

        else:
          dbgPrint("don't know what to do with node {0}, len {1}".format(node, len))
          if node == 3 and len == 10:
                rain, batt, a, b, c = struct.unpack("hhhhh", data[2:])
                dbgPrint("Batt = " + batt + "rain=" +  rain)

    except Exception, e:
        dbgPrint("Exception {0}".format(str(e)))
os.close(fd)
