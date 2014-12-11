import sqlite3
import os
from DataStore import *
import sys
from datetime import *
lastIndex = 0

def makefile(datestamp, datadir):
    d = None
    try:
        d = datestamp.split(" ")[0]
    except:
        return None
    parts = d.split("-")
    path = ""
    for bits in [datadir, "raw", parts[0], parts[0]+"-"+parts[1]]:
        path = os.path.join(path, bits)
        if not os.path.exists(path):
            print "Need to make ", path
            os.mkdir(path)
    return os.path.join(path, d+".txt")
    
    
class dataminder:
    def __init__(self, data):
        self.idx = datetime(2000,1,1,0,0,0)
        self.delay = 1
        self.wind_ave = 0
        self.wind_gust = 0
        self.wind_dir = 0
        self.status = 0
        self.uv = 0
        self.illuminance = 0
        for row in data:
            timestamp=  datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            print timestamp
            if timestamp > self.idx:
                self.idx = timestamp
        
            node = row[1]
            if node ==2:
                t = row[3]
                if t < 40 and t > -10:
                    self.temp_out = self.temp_in = t
                
                h = row[4]
                if h > 0 and h < 100:
                    self.hum_in = self.hum_out = int(h)
                p = row[5]
                if p > 900 and p < 1100:
                    self.abs_pressure = p
                    
            elif node == 3:
                self.idx = row[0]
                self.rain = row[6]
                
            elif node == 10:
                t = row[3]
                if t < 40 and t > -10:
                    self.temp_kitchen =t
            
            elif node == 21:
                t = row[3]
                if t < 40 and t > -10:
                    self.temp_bedroom = t
       
    
    def __str__(self):
        fields = [self.idx,self.delay,self.hum_in,self.temp_in,self.hum_out,
                  self.temp_out,self.abs_pressure,self.wind_ave,self.wind_gust,self.wind_dir,
                self.rain,self.status,self.illuminance,self.uv, self.temp_bedroom, self.temp_kitchen] 
        return ",".join(str(f) for f in fields)

def getLatestDataFromDB(c, startTime):
    sql = "select * from data where date < '{0}' group by node order by date desc limit 20".format(startTime)
    data = c.execute(sql).fetchall()
    return data
    



def doMain(database, datadir):
    global lastIndex
    conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_COLNAMES|sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    
    # get the last entry in the raw data store
    raw_data = data_store(datadir)
    lastData = raw_data.last_entry()
    lastData = getLatestDataFromDB(c, lastData["idx"])
    D = dataminder(lastData)

    # search from the last known good data
    datesearch = "date >= '{0}'".format(D.idx)

    #lastBedroom = c.execute("SELECT temp from data where node==21 {0} order by date asc limit 1".format("and "+datesearch)).fetchone()
        
    allData = c.execute("SELECT * FROM data {0} order by date asc".format("where "+datesearch)).fetchall()

    for row in allData:
        node = row[1]
        if node ==2:
            D.idx = row[0]
            t = row[3]
            if t < 40 and t > -10:
                # no sudden jumps in temp
		if D.temp_out == 0:
                    D.temp_out = D.temp_in = t
                elif t < D.temp_out - 5:
                    "ignoring rediculous jump of {0} in {1}".format(t - D.temp_out, node)
                    D.temp_out = D.temp_in = D.temp_in - 1
                elif t > D.temp_out + 5:
                    "ignoring rediculous jump of {0} in {1}".format(t - D.temp_out, node)
                    D.temp_out = D.temp_in = D.temp_in +1
                else:
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
		if D.temp_kitchen == 0:
                    D.temp_kitchen =t
                elif t < D.temp_kitchen - 5:
                    print "ignoring rediculous jump of {0} in {1}".format(t - D.temp_kitchen , node)
                    D.temp_kitchen -=1
                elif t > D.temp_kitchen + 5:
                    print "ignoring rediculous jump of {0} in {1}".format(t - D.temp_kitchen , node)
                    D.temp_kitchen +=1
                else:
		            D.temp_kitchen =t
        
        elif node == 21:
            t = row[3]
            if t < 40 and t > -10:
		if D.temp_bedroom == 0:
                    D.temp_bedroom = t
                elif t < D.temp_bedroom - 5:
                    "ignoring rediculous jump of {0} in {1}".format(t - D.temp_bedroom, node)
                    D.temp_bedroom -=1
                elif t > D.temp_bedroom + 5:
                    "ignoring rediculous jump of {0} in {1}".format(t - D.temp_bedroom, node)
                    D.temp_bedroom +=1
                else:
                    D.temp_bedroom = t
       
        if D.idx is not 0:
            a = str(D)
            filen = makefile(D.idx, datadir)
            with open(filen, "a") as f:
                f.write(a+"\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: {0} database data_dir".format(sys.argv[0])
        sys.exit(0)
    doMain(sys.argv[1], sys.argv[2])
    




