import MySQLdb
from datetime import datetime

dbfile = open('dbconnect.conf', 'r').readlines()

cxn = MySQLdb.connect('localhost',user=str(dbfile[0]).replace('\n',''), passwd=str(dbfile[1]).replace('\n',''))

date = datetime.now()


cxn.query('CREATE DATABASE IF NOT EXISTS InfernalWireless')

cxn.commit()
cxn.close()

cxn = MySQLdb.connect(db='InfernalWireless')

cur = cxn.cursor()

current_project_id = 0


	
#~ cxn = MySQLdb.connect('localhost','root',"")
#~ 
#~ date = datetime.now()
#~ 
#~ 
#~ cxn.query('CREATE DATABASE IF NOT EXISTS InfernalWireless')
#~ 
#~ cxn.commit()
#~ cxn.close()
#~ 
#~ cxn = MySQLdb.connect(db='InfernalWireless')
#~ 
#~ cur = cxn.cursor()
#~ 
#~ current_project_id = 0

def create_project_table():
	
	##############3333  THIS IS GOING TO CRAETE A TABLE FOR PROJECT 

	
	
	#~ cur.execute("CREATE TABLE mytable (id AUTO_INCREMENT")
	
	PROJECT_TITLE = '''CREATE TABLE IF NOT EXISTS Projects (
	ProjectId MEDIUMINT NOT NULL AUTO_INCREMENT, ProjectName TEXT, PRIMARY KEY (ProjectId), AuditorName TEXT, TargetName TEXT, date TEXT)'''
	

	cur.execute(PROJECT_TITLE)
	

create_project_table()	


def project_details(projectname, Authors_name, TargetName, date):
	
	PROJECT_DETAILS = 'INSERT INTO Projects (ProjectName, AuditorName, TargetName, date) VALUES ("%s","%s","%s","%s")'%(projectname, Authors_name, TargetName, date)
	cur.execute(PROJECT_DETAILS)
	current_project_id_tmp = cur.lastrowid
	current_project_id = current_project_id_tmp 
	print "report is generated"
	return current_project_id_tmp
	


		
		

	
	
def create_report_table():
	
	##############3333  THIS IS GOING TO CRAETE A TABLE FOR PROJECT 
	
	
	report_table = '''CREATE TABLE IF NOT EXISTS Reports (findingID MEDIUMINT NOT NULL AUTO_INCREMENT, finding_name TEXT, phase TEXT, PRIMARY KEY (findingID), risk_level TEXT, risk_category TEXT, Findings_detail TEXT, Notes TEXT, Project_fk_Id MEDIUMINT, FOREIGN KEY (Project_fk_Id) REFERENCES Projects (ProjectId))'''
	
	cur.execute(report_table)	


create_report_table()



def create_report(self, finding_name, phase, risk_level, risk_category, Findings_detail, Notes, Project_fk_Id):
	########## THIS IS GOING TO INSERT DATA INTO FINDINGS TABLE
	
	
	pID = current_project_id
	REPORT_DETAILS = 'INSERT INTO Reports (finding_name, phase, risk_level, risk_category, Findings_detail, Notes, Project_fk_Id) VALUES ("%s","%s","%s","%s","%s","%s","%s")'%( finding_name, phase, risk_level, risk_category, Findings_detail, Notes, Project_fk_Id)
	cur.execute(REPORT_DETAILS)
	print pID
	
	

def print_hello(test_data):
	print test_data
	



################ DB POPULATE DATABASE ###########
#~ prID = project_details('test','est','23s','12/12/12')	
#~ 
#~ create_report('Title of the finding','Choose a phase','Choose a category','Choose risk level','Enter the findings details','Notes on the findings',int(prID))	
###################################################################  DUMMY DATABASE QUERIES ##############
#~ print type(prID)	
cur.close()
cxn.commit()
cxn.close()

print "DB has been updated"
	
