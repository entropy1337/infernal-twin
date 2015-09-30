#!/usr/bin/python
# -*- coding: utf-8 -*-
#~ 
import MySQLdb as mdb
import wx
import wx.html
from wx.lib.wordwrap import wordwrap
import generate_pdf_file

dbfile = open('dbconnect.conf', 'r').readlines()

con = mdb.connect('localhost',str(dbfile[0]).replace('\n',''),str(dbfile[1]).replace('\n',''), 'InfernalWireless');

cur = con.cursor()
cur.execute("SELECT ProjectId,ProjectName FROM Projects")
data = row = cur.fetchall()


project_data = []

projects_id = {}
projects = []

for i in data:
	projects.append(str(i[1]))
	projects_id[str(i[0])]=str(i[1])

#~ print data
#~ print projects_id
mypdfcreate = generate_pdf_file.create_pdf()

myHTML = ""



    
htmlAppend = """    <p><br>
    </p>
  </body>
</html>"""
class AboutDlg(wx.Frame):
 
    def __init__(self, parent):
 
        wx.Frame.__init__(self, parent, wx.ID_ANY, title="About", size=(900,1000))
 
        html = wxHTML(self)
 
        html.SetPage(myHTML)
 
class wxHTML(wx.html.HtmlWindow):
     def OnLinkClicked(self, link):
         webbrowser.open(link.GetHref())
 
 
 
class Example(wx.Frame):
           
    def __init__(self, *args, **kw):
        super(Example, self).__init__(*args, **kw) 
        
        self.InitUI()
        
    def InitUI(self):   

        pnl = wx.Panel(self)
        
        
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
        for key,value in projects_id.iteritems():
			if str(value) == str(i):
				print 'The key is ' + str(key)
				
				cur.execute("SELECT * FROM Projects WHERE ProjectId ="+str(key))
				myPrData = cur.fetchall() 
				global project_data
				project_data = myPrData
				cur.execute("SELECT * FROM Reports WHERE Project_fk_Id ="+str(key))
				data = row = cur.fetchall()
				
				
				break
			else:
				print "Database is not found"
        
        
        
        
        #~ mypdfcreate.add_pdf_text('1','1','1','1','1','1')
        
        htmlPrepend = """<!DOCTYPE html>
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
    </p>"""%(myPrData[0][1],myPrData[0][3],myPrData[0][2],myPrData[0][4],)

        
        global myHTML
        myTMPHTML = []
        for i in data:
			
			#~ mypdfcreate.add_pdf_text(i[1],i[2],i[3],i[4],i[5],i[6])
			
			#~ tmpdata = str(i[1]+' '+i[2]+' '+i[3]+' '+i[4]+' '+i[5]+' '+i[6])
			AboutDlg(self)
			tmpdata = """<table width="850" style="width: 1250px; height: 187px;" border="1">
	      <tbody>
	        <tr>
	          <td id="title" style="width: 100.12px;">%s<br>
	          </td>
	          <td id="phase" style="width: 100.883px; height: 55.867px;" colspan="2"
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
	    </table><p></p>"""%(i[1],i[2],i[3],i[4],i[5],i[6])
			
			
			myTMPHTML.append(tmpdata)
	
	htmltables = ' '.join(map(str, myTMPHTML))
	myHTML = htmlPrepend + htmltables + htmlAppend
	
	aboutDlg = AboutDlg(None)
	aboutDlg.Show()
        
        #~ mypdfcreate.create_final()
        
        
        
def main():
    
    ex = wx.App()
    Example(None)
    ex.MainLoop()    

#~ if __name__ == '__main__':
    #~ main()   

