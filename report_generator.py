import wx
import sys
import os
import ast
import MySQLdb
from datetime import datetime

dbfile = open('dbconnect.conf', 'r').readlines()

cxn = MySQLdb.connect('localhost',user=str(dbfile[0]).replace('\n',''), passwd=str(dbfile[1]).replace('\n',''))

date = datetime.now()

cur = cxn.cursor()


cxn.query('CREATE DATABASE IF NOT EXISTS InfernalWireless')

project_id = []
project_name = []
current_project_id = ''
cxn.commit()
cxn.close()

cxn = MySQLdb.connect(db='InfernalWireless')

cur = cxn.cursor()

current_project_id = 0
current_project_name = ''

cur.execute("SELECT ProjectId,ProjectName FROM Projects")
data = row = cur.fetchall()
for i,y in data:
	project_id.append(i)
	project_name.append(y)
#~ cur.commit()
#~ cur.close()

#~ print project_id
#~ print project_name





class Example(wx.Frame):
	
	
	
    def __init__(self, parent, title):
		
        super(Example, self).__init__(parent, title=title, 
            size=(600, 700))
        
        self.InitUI()
        	
        	
        self.Centre()


        self.Show()
             
    
    global MultiLine
    isProject = False     
    global projectName
    global projectName2
    global current_project_name
    def InitUI(self):
	self.current_project_num = current_project_id	
		
    
        panel = wx.Panel(self)
        
        self.quote = wx.StaticText(panel,-1, label="Report an issue \n", pos=(10, 30))
        self.quote.SetForegroundColour((255,0,0)) # set text color
        
        #~ prjBtn = wx.Button(panel, -1, "Create a Project",size=(150,30), pos=(10,650))
        #~ prjBtn.Bind(wx.EVT_BUTTON, self.create_project)
        
        

        panel.SetBackgroundColour('#4f5049')
        #vbox = wx.BoxSizer(wx.VERTICAL)
        
        
        #~ self.projectname = wx.TextCtrl(panel, -1, "Project Name",size=(250,30), pos=(10,120))
        #~ #self.projectname.SetBackgroundColour('#ededed')
        
        
        self.title = wx.TextCtrl(panel, -1, "Title of the finding",size=(430,30), pos=(10,60))
        #self.author.SetBackgroundColour('#ededed')
        
        #################333 choose category ##############
        section_category = ['Social Engineering', 'Active Exploitation', 'Wireless Security', 'MiTM']
        self.cb = wx.ComboBox(panel,-1,"Choose a category", pos=(10, 140), choices=section_category, style=wx.CB_READONLY)
        
        ######################## choose phase ##############
        section_phase = ['Reconnaisance', 'Exploitation', 'Wireless Security']
        self.cb2 = wx.ComboBox(panel,-1,"Choose a phase", pos=(10, 100), choices=section_phase, style=wx.CB_READONLY)
        
        ############################## choose risk level #################
        section_risk = ['High', 'Medium', 'Low', 'Information']
        self.cb3 = wx.ComboBox(panel,-1,"Choose risk level", pos=(250, 100), choices=section_risk, style=wx.CB_READONLY)
            
        self.findings= wx.MultiLine = wx.TextCtrl(panel, -1,"Enter the findings details", pos = (10, 200), size = (510, 220), style = wx.TE_MULTILINE)
        #self.targetname.SetBackgroundColour('#ededed')
        
        self.notes= wx.MultiLine = wx.TextCtrl(panel, -1,"Notes on the findings", pos = (10, 450), size = (510, 100), style = wx.TE_MULTILINE)
        
        #~ self.datename = wx.TextCtrl(panel, -1, "dd/mm/yy",size=(250,30), pos=(10,240))
        #~ #self.targetname.SetBackgroundColour('#ededed')        
        
        prjBtn = wx.Button(panel, -1, "Add Finding",size=(150,30), pos=(10,600))
        prjBtn.Bind(wx.EVT_BUTTON, self.create_project)
        
        ############### adding a combo box
        #~ projects = ['1','1','1','1','1']
        
        
        
        cb = wx.ComboBox(panel, pos=(200,600), choices=project_name, size=(280,30), value='Select a Project', style=wx.CB_READONLY)
        
        current_project_name = cb.GetValue()
        #~ 
        #~ cb.Bind(wx.EVT_COMBOBOX, get_project_id(current_project_name))
                
        
        prjBtn2 = wx.Button(panel, -1, "Generate Report",size=(150,30), pos=(10,650))
        prjBtn2.Bind(wx.EVT_BUTTON, self.create_std)
        
        prjBtn3 = wx.Button(panel, -1, "Select a Project file",size=(150,30), pos=(200,650))
        prjBtn3.Bind(wx.EVT_BUTTON, self.open_project)
        
        #~ vbox.Add(self.MultiLine, -1,10)
        #~ vbox.Add(prjBtn,-1, border=10)
        #~ panel.SetSizer(vbox)
        
	def get_project_id():
		print project_id
		
	def create_database(self):
		cxn = MySQLdb.connect('localhost',user=str(dbfile[0]).replace('\n',''), passwd=str(dbfile[1]).replace('\n',''))

		date = datetime.now()
		
		
		cxn.query('CREATE DATABASE IF NOT EXISTS InfernalWireless')
		
		cxn.commit()
		cxn.close()
		
		cxn = MySQLdb.connect(db='InfernalWireless')
		
		cur = cxn.cursor()
		current_project_id = 0
	
	def create_report_table(self):
	
		##############3333  THIS IS GOING TO CRAETE A TABLE FOR PROJECT 
		
		
		report_table = '''CREATE TABLE IF NOT EXISTS Reports (findingID MEDIUMINT NOT NULL AUTO_INCREMENT, finding_name TEXT, phase TEXT, PRIMARY KEY (findingID), risk_level TEXT, risk_category TEXT, Findings_detail TEXT, Notes TEXT, Project_fk_Id MEDIUMINT, FOREIGN KEY (Project_fk_Id) REFERENCES Projects (ProjectId))'''
		
		cur.execute(report_table)	
		

    def create_report(self, finding_name, phase, risk_level, risk_category, Findings_detail, Notes):
		cxn = MySQLdb.connect(db='InfernalWireless')
		
		cur = cxn.cursor()

		pID = cur.execute('SELECT LAST_INSERT_ID() FROM Projects')
		REPORT_DETAILS = 'INSERT INTO Reports (finding_name, phase, risk_level, risk_category, Findings_detail, Notes, Project_fk_Id) VALUES ("%s","%s","%s","%s","%s","%s","%d")'%( finding_name, phase, risk_level, risk_category, Findings_detail, Notes, int(pID))
		#~ print 'Current PID is' + str(pID)
		cur.execute(REPORT_DETAILS)
		cxn.commit()
		#~ print 'Current PID is ' + str(pID)
		global current_project_name
		#~ print 'Current project id is' + str(current_project_name)
		
    def open_project(self, e):
		
		dlg = wx.FileDialog(self, "Choose a project file", os.getcwd(), "", "*.*", wx.OPEN)
       
		if dlg.ShowModal() == wx.ID_OK:
				
		   
			path = dlg.GetPath()
			self.mypath = os.path.basename(path)
			self.SetStatusText("You selected: %s" % self.mypath)

		self.capturelist = str(path)
		self.projectName2 = self.capturelist	
		dlg.Destroy()
		
 		
	
    def create_project(self, e):

		
		self.rtitle = self.title.GetValue()
		self.rfindings = self.findings.GetValue()
		#~ print self.projectName2

		
		
		if self.rtitle != " " or self.rfindings !=" ":
			
			#
			self.rtitle = self.title.GetValue()
			self.rphase = self.cb2.GetValue()
			self.rcategory = self.cb.GetValue()
			self.rrisklevel = self.cb3.GetValue()
			self.rfindings = self.findings.GetValue()
			self.rnotes = self.notes.GetValue()
			self.current_project_num = current_project_id
			#~ print (str(self.rtitle), (str(self.rphase), (str(self.rcategory), (str(self.rrisklevel), (str(self.rfindings), (str(self.rnotes), int(self.current_project_num))
			#~ print 'Trying to execute create report'
			self.create_report(str(self.rtitle), str(self.rphase), str(self.rcategory), str(self.rrisklevel), str(self.rfindings), str(self.rnotes))
			#~ self.create_report('Title of the finding','Choose a phase','Choose a category','Choose risk level','Enter the findings details','Notes on the findings')	
			
			#~ print "Report is created"
 			
			textboxes = open('textboxes.txt','a')
			
			result_data = """<table style="width: 1250px; height: 187px;" border="1">
	      <tbody>
	        <tr>
	          <td id="title" style="width: 909.12px;">%s<br>
	          </td>
	          <td id="phase" style="width: 522.883px; height: 55.867px;" colspan="2"
	            rowspan="1">%s<br>
	            <br>
	          </td>
	        </tr>
	        <tr>
	          <td id="findings">%s <br>
	          </td>
	          <td><span style="font-weight: bold;">Risk Level</span><br>
	          </td>
	          <td><span style="font-weight: bold;">Category</span><br>
	          </td>
	        </tr>
	        <tr>
	          <td id="notes">%s<br>
	          </td>
	          <td id="risklevel">%s<br>
	          </td>
	          <td id="category">%s data<br>
	          </td>
	        </tr>
	      </tbody>
	    </table></br></br></br>"""%(self.rtitle, self.rphase, self.rfindings, self.rnotes, self.rrisklevel,self.rcategory)
			
			textboxes.write(result_data)
			textboxes.close()
			wx.MessageBox('Finding has been added', 'Information', wx.OK)

		else:
			wx.MessageBox('Title or Findings Section is empty', 'Warning/Error', wx.ICON_ERROR | wx.ICON_INFORMATION)

	
		
    def create_std(self, e):
		
		openproject = open(self.projectName2,'r')
		myProject = openproject.readlines()
		openproject.close()
		projectDict = {}
		#~ projectDict.update(dict(str(myProject[0])))
		#~ print projectDict['Project']
		#~ print dict(myProject[0])
		mydict3 = ast.literal_eval(str(myProject[0]))
		
		mydict3['Project']
		mydict3['Target name']
		mydict3['Authors Full Name']
		mydict3['Date']
		
		#~ mydata = open('textboxes.txt','r').read()
		#~ htmldata = mydata
		#~ mydata.close()
		
		self.fname = self.title.GetValue()
		os.system("mkdir "+str(self.fname).replace(' ','_'))
		myhtml = open(str(self.fname).replace(' ','_')+"/"+str(self.fname).replace(' ','_')+".html",'a')
		
		prependdata = """<!DOCTYPE html>
<html>
  <head>
    <meta content="text/html; charset=utf-8" http-equiv="content-type">
    <meta http-equiv="X-UA-Compatible" content="chrome=1">
    <title>Report</title>
    <style type="text/css">
#title {  
  color: #cf0b17;
}

#findings {  
  color: #0e0ab5;
}

#notes {  
  color: #0e0ab5;
}

#phase {  
  color: #800611;  
  font-weight: bold;
}

#risklevel {  
  font-weight: bolder;  
  color: #d80a1c;
}

#category {  
  color: #d80a1c;  
  font-weight: bolder;
}

</style></head>
  <body><h1>Report </h1><br><br><br><br><br>
    <p>Project: %s<br>
    </p><p>Target Name: %s<br>
    </p><p>Author's full name: '%s<br>
    </p><p>Date: %s<br>
    </p>"""%(mydict3['Project'],mydict3['Target name'],mydict3['Authors Full Name'],mydict3['Date'])
		
		myhtml.write(prependdata)
		
		
		with open('textboxes.txt') as f:
			for i in f:
				myhtml.write(i)
		
		appenddata = """    <p><br>
    </p>
  </body>
</html>"""	
		myhtml.write(appenddata)
		myhtml.close()
		os.system("echo '' > textboxes.txt")
		wx.MessageBox('Report is generated', 'Information', wx.OK)	
		os.system('firefox '+str(self.fname).replace(' ','_')+"/"+str(self.fname).replace(' ','_')+".html"+" &")
		#~ data = ""
		#~ with open('textboxes.txt','r') as myfile:
			#~ data = myfile.readlines()
		
		
		
		
		#~ report_all = open('REPORT.html','wb')
		#~ htmldata = str(data).replace('\n','')
		#~ report_all.write(htmldata)
		#~ report_all.close()
		
		#~ isProject = False
		#~ print isProject
		#~ #print self.projectName
		

	
    #~ def returnproject(self):
		#~ return self.projectName	
		
		
	

#if __name__ == '__main__':
	
def create_new_project():
  
    app = wx.App()
    Example(None, title='Create a Report')
    app.MainLoop()
    




if __name__ == '__main__':
	cur.close()
	cxn.commit()
	cxn.close()
	create_new_project()
	
	



