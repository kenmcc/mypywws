import sqlite3
import os

conn = sqlite3.connect("../../weatherparser/weather.db", detect_types=sqlite3.PARSE_COLNAMES|sqlite3.PARSE_DECLTYPES)
c = conn.cursor()

allData = c.execute("SELECT * FROM data where node < 10 order by date asc").fetchall()


def makefile(datestamp):
    d = None
    try:
        d = datestamp.split(" ")[0]
    except:
        print datestamp
    parts = d.split("-")
    if not os.path.exists("weatherdb/raw/"+parts[0]):
        os.mkdir("weatherdb/raw/"+parts[0])
        print "making year"
    if not os.path.exists("weatherdb/raw/"+parts[0]+"/"+parts[0]+"-"+parts[1]):
        os.mkdir("weatherdb/raw/"+parts[0]+"/"+parts[0]+"-"+parts[1])
        print "making year-month"
    return "weatherdb/raw/"+parts[0]+"/"+parts[0]+"-"+parts[1]+"/"+d+".txt"

class dataminder:
    idx = 0  
    delay   = 1
    hum_in = 0
    temp_in = 0
    hum_out = 0
    temp_out = 0
    abs_pressure = 0
    wind_ave = 0
    wind_gust = 0
    wind_dir = 0
    rain = 0
    status = 0
    illuminance= 0
    uv = 0
    
    def __str__(self):
        fields = [self.idx,self.delay,self.hum_in,self.temp_in,self.hum_out,
                  self.temp_out,self.abs_pressure,self.wind_ave,self.wind_gust,self.wind_dir,
                self.rain,self.status,self.illuminance,self.uv] 
        return ",".join(str(f) for f in fields)
    
    
    
D = dataminder()   

temp_out = 0
temp_in = 0
humidity=0
pressure = 0
rain = 0
wind_dir = 0
wind_avg = 0
wind_gust =0
for row in allData:
    D.idx = row[0]
    node = row[1]
    if node ==2:
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
        D.rain += row[6]
    a = str(D)
    print a
    filen = makefile(D.idx)
    with open(filen, "a") as f:
        f.write(a+"\n")




