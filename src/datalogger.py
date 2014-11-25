import sqlite3
from pywws.DataStore import *


class weatherdata:
    idx = 0  
    delay = 1
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


class dataLogger:
    def __init__(self, db):
        self.liveData = {}
        self.dbName = db
        self.conn = sqlite3.connect(db)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS data (date text DEFAULT CURRENT_TIMESTAMP, 
                                                           node int  NOT NULL, 
                                                           batt float NOT NULL, 
                                                           temp float DEFAULT x, 
                                                           humidity float DEFAULT x, 
                                                           pressure float DEFAULT x, 
                                                           rain float DEFAULT x, 
                                                           wind_dir int DEFAULT x,  
                                                           wind_avg float DEFAULT x,  
                                                           wind_gust float DEFAULT x, 
                                                           switch text DEFAULT x)''')
        self.conn.commit()
        self.weatherdata = weatherdata()
        raw_data = data_store("weatherdb")
        print raw_data.last_entry()
        

	

    def updatelive(self, value_list):
	for x in value_list:
	    if x["field"] == "humidity":
		self.weatherdata.humidity = x["value"]
	    elif x["field"] == "temp":
		self.weatherdata.temp_out = x["value"]
	    elif x["field"] == "pressure":
		self.weatherdata.pressure = x["value"]
	    elif x["field"] == "rain":
		self.weatherdata.rain = x["value"]
	    else:
		print "ignoring", x["field"]
    	
    def insert(self, value_list):
	fields = []
        values = []
        for d in value_list:
           fields.append(d["field"])
           values.append(d["value"])
        insert_string =  "INSERT INTO data ({0}) VALUES({1})".format(",".join(fields), ",".join(values))
        self.c.execute(insert_string)
        self.conn.commit()
	self.updatelive(value_list)
        
if __name__ == "__main__":
    
  
  
  
  logger = dataLogger("test.db")
  logger.insert(({"field": "node", "value": "3"}, {"field": "batt", "value": "3000"}, {"field": "rain", "value": "18.3"}))
  logger.insert(({"field": "node", "value": "2"}, {"field": "batt", "value": "3000"}, {"field": "humidity", "value": "98.3"}, {"field": "temp", "value": "17.6"}))

