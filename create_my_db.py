import MySQLdb
from datetime import datetime

dbfile = open('dbconnect.conf', 'r').readlines()

cxn = MySQLdb.connect('localhost',user=str(dbfile[0]).replace('\n',''), passwd=str(dbfile[1]).replace('\n',''))

date = datetime.now()


cxn.query('CREATE DATABASE IF NOT EXISTS InfernalWireless')
#~ cxn = MySQLdb.connect(db='InfernalWireless')

cxn = MySQLdb.connect('localhost',user=str(dbfile[0]).replace('\n',''), passwd=str(dbfile[1]).replace('\n',''))
cxn = MySQLdb.connect(db='InfernalWireless')

cur = cxn.cursor()

cxn.commit()
cxn.close()

PROJECT_TITLE = '''CREATE TABLE IF NOT EXISTS Projects (ProjectId MEDIUMINT NOT NULL AUTO_INCREMENT, ProjectName TEXT, PRIMARY KEY (ProjectId), AuditorName TEXT, TargetName TEXT, date TEXT)'''


cur.execute(PROJECT_TITLE)

report_table = '''CREATE TABLE IF NOT EXISTS Reports (findingID MEDIUMINT NOT NULL AUTO_INCREMENT, finding_name TEXT, phase TEXT, PRIMARY KEY (findingID), risk_level TEXT, risk_category TEXT, Findings_detail TEXT, Notes TEXT, Project_fk_Id MEDIUMINT, FOREIGN KEY (Project_fk_Id) REFERENCES Projects (ProjectId))'''


cur.execute(report_table)

cur.close()
cxn.commit()
cxn.close()
