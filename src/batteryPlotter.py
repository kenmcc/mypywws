import sqlite3

con = sqlite3.connect("weather.db")
con.isolation_level = None
cur = con.cursor()


NODENAMES = {"2":"PTH","3":"Rain","10":"Kitchen", "21":"Bedroom"}

nodes = []
d = cur.execute("select distinct node from data")
for x in d:
    nodes.append(x[0])
    
for x in nodes:
   with open("/tmp/battery_{0}.txt".format(x), "a+") as f:
       existingData = f.readlines()
       dateQualifier = ""
       lastDate = ""
       if existingData:
           lastDate = existingData[-1:][0].split("\t")[0]
           dateQualifier = " and date > '{0}' ".format(lastDate)
    
       statement = "select t.date, t.batt from data t join(select max(tt.date) 'maxtimestamp' from data tt where node={0} {1} group by date(tt.date)) m on m.maxtimestamp = t.date".format(x, dateQualifier)
       #print statement
       d = cur.execute(statement)
       for y in d:
           date = y[0].split(" ")[0]
           val = str(y[1])
           if date > lastDate:
               f.write("{0}\t{1}\n".format(date, val))
        
        
with open("/tmp/plotter.sh", "w") as f:
    f.write("set term png\n")
    f.write("set output 'battery_levels.png'\n")
    f.write("set xdata time\n")
    f.write("set timefmt '%Y-%m-%d'\n")
    f.write("set format x '%d/%m'\n")
    f.write("set yrange [2.5:5]\n")
    plots = []
    plotnum = 1
    for x in nodes:
        plots.append('"battery_{0}.txt" using 1:2 title "{2}" smooth unique lc {1} lw 1'.format(x, plotnum, NODENAMES[str(x)]+"("+str(x)+")" if str(x) in NODENAMES else x))
        plotnum += 1
    f.write("plot " + ",".join(plots) + "\n")
    
        
