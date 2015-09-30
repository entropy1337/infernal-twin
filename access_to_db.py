import MySQLdb
import wx,os

class Example(wx.Frame):
	
	
	
    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title, 
            size=(600, 900))
            
        self.InitUI()
        self.Centre()
        self.Show()     
    
    global MultiLine
  
    
        
    def InitUI(self):
		
		
    
        panel = wx.Panel(self)
        
        refreshBtn = wx.Button(panel, -1, "Connect to DB")
        refreshBtn.Bind(wx.EVT_BUTTON, self.refresh)
        
        clearBtn = wx.Button(panel, -1, "Clear DB")
        clearBtn.Bind(wx.EVT_BUTTON, self.clearlog)

        panel.SetBackgroundColour('#4f5049')
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.MultiLine = wx.TextCtrl(panel, -1, "",style = wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_AUTO_URL)
        self.MultiLine.SetBackgroundColour('#ededed')
        
        vbox.Add(self.MultiLine, 1, wx.EXPAND | wx.ALL, 10)
        vbox.Add(refreshBtn)
        vbox.Add(clearBtn)
        panel.SetSizer(vbox)
	
    def clearlog(self, e):
		
		try:
			#
			dbfile = open('dbconnect.conf', 'r').readlines()
		
			db = MySQLdb.connect("localhost",str(dbfile[0]).replace('\n',''),str(dbfile[1]).replace('\n',''),"wpa_crack" )
		
			# prepare a cursor object using cursor() method
			cursor = db.cursor()
	
			# execute SQL query using execute() method.
			cursor.execute("truncate content")	
		except:
			wx.MessageBox('Could not connect to DB', 'Warning/Error', wx.ICON_ERROR | wx.ICON_INFORMATION)
			
				
    def refresh(self, e):
		
		try:
			#
			# Open database connection
			dbfile = open('dbconnect.conf', 'r').readlines()
			
			db = MySQLdb.connect("localhost",str(dbfile[0]).replace('\n',''), str(dbfile[1]).replace('\n',''),"wpa_crack" )
		
			# prepare a cursor object using cursor() method
			cursor = db.cursor()
	
			# execute SQL query using execute() method.
			results = cursor.execute("SELECT * FROM content")
	
			# Fetch a single row using fetchone() method.
			#~ data = cursor.fetchone()
	
			#~ self.MultiLine.AppendText("Username:\t\tpassword\n")
			#~ self.MultiLine.AppendText("_________________________\n")
			
			if not results:
				self.MultiLine.AppendText("No Content has been updated")
				
			else:
				self.MultiLine.AppendText("Username:\t\tpassword\n")
				self.MultiLine.AppendText("_________________________\n")
	
			
			for row in cursor.fetchall() :
				if row[0]!="" or row[1] != "":
					
					self.MultiLine.AppendText(row[0]+":::\t\t"+row[1]+"\n")
			
					
					
					
	
					#~ self.MultiLine.AppendText(i)
			db.close()
		except:
			wx.MessageBox('Could not connect to DB', 'Warning/Error', wx.ICON_ERROR | wx.ICON_INFORMATION)
			


#if __name__ == '__main__':
	
def access_to_database():
  
    app = wx.App()
    Example(None, title='Access To DB')
    app.MainLoop()

#~ access_to_database()






