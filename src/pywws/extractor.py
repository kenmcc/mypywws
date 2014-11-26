import sqlite3
import os
from DataStore import *
import sys

lastIndex = 0

def makefile(datestamp, datadir):
    d = None
    try:
        d = datestamp.split(" ")[0]
    except:
        return None
    parts = d.split("-")
    path = datadir+"/raw/"+parts[0]
    if not os.path.exists(path):
        os.mkdir(path)
    
    path += "/"+parts[0]+"-"+parts[1]
    if not os.path.exists(path):
        os.mkdir(path)
        
    path += "/"+d+".txt"
    return path

class dataminder:
    idx = lastIndex
    delay   = 1
    hum_in = 0 if lastIndex == 0 else lastData["hum_in"]
    temp_in =  0 if lastIndex == 0 else lastData["temp_in"]
    hum_out =  0 if lastIndex == 0 else lastData["hum_out"]
    temp_out =  0 if lastIndex == 0 else lastData["temp_out"]
    abs_pressure =  0 if lastIndex == 0 else lastData["abs_pressure"]
    wind_ave =  0 if lastIndex == 0 else lastData["wind_ave"]
    wind_gust =  0 if lastIndex == 0 else lastData["wind_gust"]
    wind_dir =  0 if lastIndex == 0 else lastData["wind_dir"]
    rain =  0 if lastIndex == 0 else lastData["rain"]
    status =  0 if lastIndex == 0 else lastData["status"]
    illuminance=  0 if lastIndex == 0 else lastData["illuminance"]
    uv = 0 if lastIndex == 0 else lastData["uv"]
    temp_bedroom =  0 if lastIndex == 0 else lastData["temp_bedroom"]
    temp_kitchen=  0 if lastIndex == 0 else lastData["temp_kitchen"]
    
    def __str__(self):
        fields = [self.idx,self.delay,self.hum_in,self.temp_in,self.hum_out,
                  self.temp_out,self.abs_pressure,self.wind_ave,self.wind_gust,self.wind_dir,
                self.rain,self.status,self.illuminance,self.uv, self.temp_bedroom, self.temp_kitchen] 
        return ",".join(str(f) for f in fields)


def doMain(database, datadir):
    global lastIndex
    conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_COLNAMES|sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    
    raw_data = data_store(datadir)
    lastData = raw_data.last_entry()
    datesearch = ""
    lastIndex = 0
    if lastData is not None:
        lastIndex = lastData["idx"]
        datesearch = "where date > '{0}'".format(lastIndex)
        
    allData = c.execute("SELECT * FROM data {0} order by date asc".format(datesearch)).fetchall()

    D = dataminder()   
    
    
    for row in allData:
        node = row[1]
        if node ==2:
            D.idx = row[0]
            t = row[3]
            if t < 40 and t > -10:
                D.temp_out = D.temp_in = t
            h = row[4]
            if h > 0 and h < 100:
                D.hum_in = D.hum_out = int(h)
            p = row[5]
            if p > 900 and p < 1100:
                D.abs_pressure = p
                
        elif node == 3:
            D.idx = row[0]
            D.rain += row[6]
            
        elif node == 10:
            t = row[3]
            if t < 40 and t > -10:
                D.temp_kitchen =t
        
        elif node == 21:
            t = row[3]
            if t < 40 and t > -10:
                D.temp_bedroom =t
       
        a = str(D)
        if D.idx is not 0:
            filen = makefile(D.idx, datadir)
            with open(filen, "a") as f:
                f.write(a+"\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: {0} database data_dir".format(sys.argv[0])
        sys.exit(0)
    doMain(sys.argv[1], sys.argv[2])
    




