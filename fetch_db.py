#!/usr/bin/python
# -*- coding: utf-8 -*-
#~ 
import MySQLdb as mdb
import wx
import generate_pdf_file
import view_projects

dbfile = open('dbconnect.conf', 'r').readlines()

con = mdb.connect('localhost', str(dbfile[0]).replace('\n',''), str(dbfile[1]).replace('\n',''), 'InfernalWireless');

cur = con.cursor()
cur.execute("SELECT ProjectId,ProjectName FROM Projects")
data = row = cur.fetchall()

projects_id = {}
global projects
projects = []

for i in data:
	projects.append(str(i[1]))
	projects_id[str(i[0])]=str(i[1])

#~ print data
#~ print projects_id
mypdfcreate = generate_pdf_file.create_pdf()

class Example(wx.Frame):
	
	
           
    def __init__(self, *args, **kw):
        super(Example, self).__init__(*args, **kw) 
        
        self.InitUI()
    global projects
        
    def InitUI(self):   

        pnl = wx.Panel(self)
        
        global projects
        cb = wx.ComboBox(pnl, pos=(50, 30), choices=projects, size=(280,30), value='Select a Project', style=wx.CB_READONLY)

        self.st = wx.StaticText(pnl, label='', pos=(50, 140))
        cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
        
        self.SetSize((400, 230))
        self.SetTitle('wx.ComboBox')
        self.Centre()
        self.Show(True)          
        
    def OnSelect(self, e):
        
        i = e.GetString()
        self.st.SetLabel(i)
        cxn = mdb.connect(db='InfernalWireless')
        cur = cxn.cursor()

        for key,value in projects_id.iteritems():
			if str(value) == str(i):
				print 'The key is ' + str(key)
				cur.execute("SELECT * FROM Reports WHERE Project_fk_Id ="+str(key))
				data = row = cur.fetchall()
				break
			else:
				print "Database is not found"
        
        
        
        
        #~ mypdfcreate.add_pdf_text('1','1','1','1','1','1')
        
        for i in data:
			
			mypdfcreate.add_pdf_text(i[1],i[2],i[3],i[4],i[5],i[6])
			print i[1]+' '+i[2]+' '+i[3]+' '+i[4]+' '+i[5]+' '+i[6]
        
        mypdfcreate.create_final()
        
        
        
def main():
    
    ex = wx.App()
    Example(None)
    ex.MainLoop()    

#~ if __name__ == '__main__':
    #~ main()   
