import wx
#~ import infernal_wireless_gui_project
import os
import os.path 
import MySQLdb
from datetime import datetime

os.system('/etc/init.d/apache2 start')
os.system('/etc/init.d/mysql start')

if os.path.exists('dbconnect.conf'):
	print 'DB Config files is found'
else:
	print 'Creating DB config file'
	import db_connect_creds


dbfile = open('dbconnect.conf', 'r').readlines()

cxn = MySQLdb.connect('localhost',str(dbfile[0]).replace('\n',''),str(dbfile[1]).replace('\n',''))

date = datetime.now()


cxn.query('CREATE DATABASE IF NOT EXISTS InfernalWireless')

cxn.commit()
cxn.close()

cxn = MySQLdb.connect(db='InfernalWireless')

cur = cxn.cursor()

current_project_id = 0
#~ os.system("airmon-ng start wlan0")

def create_project_table():
	

	##############3333  THIS IS GOING TO CRAETE A TABLE FOR PROJECT 

	
	
	#~ cur.execute("CREATE TABLE mytable (id AUTO_INCREMENT")
	
	PROJECT_TITLE = '''CREATE TABLE IF NOT EXISTS Projects (ProjectId MEDIUMINT NOT NULL AUTO_INCREMENT, ProjectName TEXT, PRIMARY KEY (ProjectId), AuditorName TEXT, TargetName TEXT, date TEXT)'''
	

	cur.execute(PROJECT_TITLE)
	#~ print 'Project table is created'

#~ def create_report_table(self):
#~ 
	#~ ##############3333  THIS IS GOING TO CRAETE A TABLE FOR PROJECT 
	#~ 
	#~ 
	#~ report_table = '''CREATE TABLE IF NOT EXISTS Reports (findingID MEDIUMINT NOT NULL AUTO_INCREMENT, finding_name TEXT, phase TEXT, PRIMARY KEY (findingID), risk_level TEXT, risk_category TEXT, Findings_detail TEXT, Notes TEXT, Project_fk_Id MEDIUMINT, FOREIGN KEY (Project_fk_Id) REFERENCES Projects (ProjectId))'''
	#~ cur.execute(report_table)	
    #~ print 'Report table is created'
#~ 

def create_report_table():
	

	##############3333  THIS IS GOING TO CRAETE A TABLE FOR PROJECT 

	
	
	#~ cur.execute("CREATE TABLE mytable (id AUTO_INCREMENT")
	
	report_table = '''CREATE TABLE IF NOT EXISTS Reports (findingID MEDIUMINT NOT NULL AUTO_INCREMENT, finding_name TEXT, phase TEXT, PRIMARY KEY (findingID), risk_level TEXT, risk_category TEXT, Findings_detail TEXT, Notes TEXT, Project_fk_Id MEDIUMINT, FOREIGN KEY (Project_fk_Id) REFERENCES Projects (ProjectId))'''
	

	cur.execute(report_table)
	#~ print 'Report table is created'
create_project_table()
create_report_table()


class Example(wx.Frame):
	
	
	
    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title, 
            size=(600, 400))

        #~ self.create_project_table()
        #~ self.create_report_table()
                    
        self.InitUI()
       

        self.Centre()
        self.Show()
             
    
    global MultiLine
    isProject = False     
    global projectName
    #~ self.projectIDNumber = 0
    def InitUI(self):
		
		
    
        panel = wx.Panel(self)
        
        self.quote = wx.StaticText(panel,-1, label="PROJECT DETAILS \n", pos=(10, 30))
        self.quote.SetForegroundColour((255,0,0)) # set text color
        
        #~ prjBtn = wx.Button(panel, -1, "Create a Project",size=(150,30), pos=(10,650))
        #~ prjBtn.Bind(wx.EVT_BUTTON, self.create_project)
        
        

        panel.SetBackgroundColour('#4f5049')
        #vbox = wx.BoxSizer(wx.VERTICAL)
        
        
        self.projectname = wx.TextCtrl(panel, -1, "Project Name",size=(250,30), pos=(10,120))
        #self.projectname.SetBackgroundColour('#ededed')
        
        
        self.author = wx.TextCtrl(panel, -1, "Author's Full Name'",size=(250,30), pos=(10,160))
        #self.author.SetBackgroundColour('#ededed')
        
        self.targetname = wx.TextCtrl(panel, -1, "Target Name",size=(250,30), pos=(10,200))
        #self.targetname.SetBackgroundColour('#ededed')
        
        self.datename = wx.TextCtrl(panel, -1, "dd/mm/yy",size=(250,30), pos=(10,240))
        #self.targetname.SetBackgroundColour('#ededed')        
        
        prjBtn = wx.Button(panel, -1, "Create a Project",size=(150,30), pos=(10,300))
        
        prjBtn.Bind(wx.EVT_BUTTON, self.create_project)
                
        
        prjBtn2 = wx.Button(panel, -1, "Stand alone",size=(150,30), pos=(10,350))
        prjBtn2.Bind(wx.EVT_BUTTON, self.create_std)
        
        #~ vbox.Add(self.MultiLine, -1,10)
        #~ vbox.Add(prjBtn,-1, border=10)
        #~ panel.SetSizer(vbox)
	
	

    
    def create_project_table(self):
		
	
		##############3333  THIS IS GOING TO CRAETE A TABLE FOR PROJECT 
	
		
		
		#~ cur.execute("CREATE TABLE mytable (id AUTO_INCREMENT")
		
		PROJECT_TITLE = '''CREATE TABLE IF NOT EXISTS Projects (ProjectId MEDIUMINT NOT NULL AUTO_INCREMENT, ProjectName TEXT, PRIMARY KEY (ProjectId), AuditorName TEXT, TargetName TEXT, date TEXT)'''
		
	
		cur.execute(PROJECT_TITLE)
		#~ print 'Project table is created'
    
	#~ def create_report_table(self):
#~ 
		#~ ##############3333  THIS IS GOING TO CRAETE A TABLE FOR PROJECT 
		#~ 
		#~ 
		#~ report_table = '''CREATE TABLE IF NOT EXISTS Reports (findingID MEDIUMINT NOT NULL AUTO_INCREMENT, finding_name TEXT, phase TEXT, PRIMARY KEY (findingID), risk_level TEXT, risk_category TEXT, Findings_detail TEXT, Notes TEXT, Project_fk_Id MEDIUMINT, FOREIGN KEY (Project_fk_Id) REFERENCES Projects (ProjectId))'''
		#~ cur.execute(report_table)	
	    #~ print 'Report table is created'
    #~ 

    def create_report_table(self):
		
	
		##############3333  THIS IS GOING TO CRAETE A TABLE FOR PROJECT 
	
		
		
		#~ cur.execute("CREATE TABLE mytable (id AUTO_INCREMENT")
		
		report_table = '''CREATE TABLE IF NOT EXISTS Reports (findingID MEDIUMINT NOT NULL AUTO_INCREMENT, finding_name TEXT, phase TEXT, PRIMARY KEY (findingID), risk_level TEXT, risk_category TEXT, Findings_detail TEXT, Notes TEXT, Project_fk_Id MEDIUMINT, FOREIGN KEY (Project_fk_Id) REFERENCES Projects (ProjectId))'''
		
	
		cur.execute(report_table)
		#~ print 'Report table is created'




    def project_details(self, projectname, Authors_name, TargetName, date):
	
		PROJECT_DETAILS = 'INSERT INTO Projects (ProjectName, AuditorName, TargetName, date) VALUES ("%s","%s","%s","%s")'%(projectname, Authors_name, TargetName, date)
		cur.execute(PROJECT_DETAILS)
		current_project_id_tmp = cur.lastrowid
		current_project_id = current_project_id_tmp
		#~ cur.close()
		#~ cxn.commit()
		#~ cxn.close() 
		#~ print "report is generated"
    
    def create_project(self, e):
		isProject = True
		#~ print isProject
		self.projectName = self.projectname.GetValue()
		#print self.projectName
		
		dic_project = {"Project":str(self.projectName),"Authors Full Name":str(self.author.GetValue()),"Target name":str(self.targetname.GetValue()),"Date":str(self.datename.GetValue())}
		
		os.system("mkdir %s"%str(self.projectName).replace(" ","_"))
		dic_project['Filename']=str(self.projectName).replace(" ","_")
		
		pFile = open(self.projectName.replace(" ","_")+"/Project Info.txt","wb")
		pFile.write(str(dic_project))
		pFile.close()
		
		
		
		prID = self.project_details(str(self.projectName),str(self.author.GetValue()),str(self.targetname.GetValue()),str(self.datename.GetValue()))
		cur.close()
		cxn.commit()
		cxn.close()
		
		self.closeWindow(self)
		infernal_wireless_gui_project.main()
		
		
    def closeWindow(self, event):
		self.Destroy()			
		

	
		
    def create_std(self, e):
		isProject = False
		#~ print isProject
		#print self.projectName
		self.closeWindow(self)
		infernal_wireless_gui_project.main()
	
    def returnproject(self):
		return self.projectName	
		
		
	

#if __name__ == '__main__':
	
def create_new_project():
	

    app = wx.App()
    
    Example(None, title='Create A project')
    
    app.MainLoop()
	
    




if __name__ == '__main__':
	
	import infernal_wireless_gui_project
	
	create_new_project()
	cur.close()
	cxn.commit()
	cxn.close()
	
	

	


