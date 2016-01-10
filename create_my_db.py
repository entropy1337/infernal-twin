import MySQLdb
import db_connect_creds

username, password = db_connect_creds.read_creds()
cxn = MySQLdb.connect('localhost', user=username, passwd=password)

cxn.query('CREATE DATABASE IF NOT EXISTS InfernalWireless')
cxn.commit()
cnx.close()

cxn = MySQLdb.connect('localhost', user=username, passwd=password, db='InfernalWireless')
cur = cxn.cursor()

PROJECT_TITLE = '''CREATE TABLE IF NOT EXISTS Projects (ProjectId MEDIUMINT NOT NULL AUTO_INCREMENT, ProjectName TEXT, PRIMARY KEY (ProjectId), AuditorName TEXT, TargetName TEXT, date TEXT)'''


cur.execute(PROJECT_TITLE)

report_table = '''CREATE TABLE IF NOT EXISTS Reports (findingID MEDIUMINT NOT NULL AUTO_INCREMENT, finding_name TEXT, phase TEXT, PRIMARY KEY (findingID), risk_level TEXT, risk_category TEXT, Findings_detail TEXT, Notes TEXT, Project_fk_Id MEDIUMINT, FOREIGN KEY (Project_fk_Id) REFERENCES Projects (ProjectId))'''


cur.execute(report_table)

cur.close()
cxn.commit()
cxn.close()
