import wx

class wpa_cracker(wx.Frame):
    def __init__(self, parent, id):
      wx.Frame.__init__(self, parent, id)
      
      panel = wx.Panel(self,-1)
      wx.StaticText(panel, -1, 'See Logs for results\ncaptures/key_found.txt', (45, 25), style=wx.ALIGN_CENTRE)
      

      self.CreateStatusBar()
      menuBar = wx.MenuBar()
      menu = wx.Menu()
      menu.Append(99,  "&WPA2 Cracker", "Crack WPA/WPA2 handshakes")
      menuBar.Append(menu, "&Load Dictionary File")
      self.SetMenuBar(menuBar)
      self.Bind(wx.EVT_MENU, self.openfile, id=99)
	
    def openfile(self, event):
		
       dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.*", wx.OPEN)
       
       if dlg.ShowModal() == wx.ID_OK:
		   
                path = dlg.GetPath()
                mypath = os.path.basename(path)
                self.SetStatusText("You selected: %s" % mypath)
                os.system("gnome-terminal -x aircrack-ng -w "+str(path)+" captures/*.cap -l captures/key_found.txt")
			
		dlg.Destroy()


	
	
