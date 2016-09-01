import sqlite3
import time

import smtplib
from datetime import datetime as dt

import os
# Import the email modules we'll need
from email.mime.text import MIMEText
try:
    con = sqlite3.connect("/data/weather.db")
except:
    con = sqlite3.connect("weather.db")
con.isolation_level = None
cur = con.cursor()


NODENAMES = {"2":"PTH","3":"Rain","10":"Kitchen", "21":"Bedroom"}
THRESHOLD=float(2.75)

nodes = []
success = False

pathroot = "/tmp" if not os.path.exists("/ramtemp") else "/ramtemp"
print pathroot


def lowBatteryAlert(node, val):
    msg = MIMEText("NODE {0} has a low battery, value {1}".format(NODENAMES[str(node)]+"("+str(node)+")" if str(x) in NODENAMES else node, val))
    me = "ken.mccullagh@gmail.com"
    you = "ken.mccullagh@gmail.com"
    msg['Subject'] = 'Weather Station Low Battery {0}'.format(NODENAMES[str(node)]+"("+str(node)+")" if str(x) in NODENAMES else node)
    msg['From'] = me
    msg['To'] = you
    
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(me, [you], msg.as_string())
    s.quit()
success=False

while not success:
  try:
    d = cur.execute("select distinct node from data")
    success = True
  except:
    print "failed to get nodes, sleeping"
    time.sleep(10)

for x in d:
   nodes.append(x[0])
 
#nodes=[2,3,10,21]
   
lastStoredVal = None    
for x in nodes:
   lastStoredVal = None
   with open(pathroot+"/battery_{0}.txt".format(x), "w+") as f:
       f.seek(0,0)
       existingData = f.readlines()
       
       dateQualifier = ""
       lastDate = ""
       lastVal = ""
       if existingData:
           lastDate = existingData[-1:][0].split("\t")[0]
           lastVal = existingData[-1:][0].split("\t")[1]
           dateQualifier = " and date > '{0}' ".format(lastDate)
    
       #statement = "select t.date, t.batt from data t join(select max(tt.date) 'maxtimestamp' from data tt where node={0} {1} group by date(tt.date)) m on m.maxtimestamp = t.date".format(x, dateQualifier)
       statement = "select * from( select t.date, t.batt from data t where node={0} order by t.date desc limit 1000) order by date asc".format(x)
       print statement
       success = False
       while not success:
          try:
             d = cur.execute(statement)
             success = True
          except Exception, e:
             print "failed to execute query, sleeping", e
             time.sleep(10)
            
            
       val = ""     
       for y in d:
           date = y[0].split(":")[0]
           d_t = dt.strptime(date, "%Y-%m-%d %H")
           
           val = str(y[1])
           if date > lastDate:
               if d_t != lastStoredVal:
                  lastStoredVal = d_t   
                  f.write("{0}\t{1}\n".format(dt.strftime(d_t, "%Y-%m-%d_%H"), val))
       # if the value now is less than the threshold, and the one from 'yesterday' isn't let's send an email
       try:
           if float(val) <= THRESHOLD  and float(lastVal) > THRESHOLD:
             lowBatteryAlert(x, val)
       except:
           pass
        
        
#with open("/ramtemp/plotter.sh", "w") as f:
with open(pathroot+"/plotter.sh", "w") as f:
    f.write("set term png\n")
    f.write("set output '{0}/battery_levels.png'\n".format(pathroot))
    f.write("set xdata time\n")
    f.write("set timefmt '%Y-%m-%d_%H'\n")
    f.write('set format x "%d/%m"\n')
    f.write("set yrange [2.5:5]\n")
    plots = []
    plotnum = 1
    for x in nodes:
        #plots.append('"/ramtemp/battery_{0}.txt" using 1:2 title "{2}" smooth unique lc {1} lw 1'.format(x, plotnum, NODENAMES[str(x)]+"("+str(x)+")" if str(x) in NODENAMES else x))
        plots.append('"{3}/battery_{0}.txt" using 1:2 title "{2}" smooth unique lc {1} lw 1'.format(x, plotnum, NODENAMES[str(x)]+"("+str(x)+")" if str(x) in NODENAMES else x, pathroot))
        plotnum += 1
    f.write("plot " + ",".join(plots) + "\n")
    
        
