#!/usr/bin/python



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
        
        refreshBtn = wx.Button(panel, -1, "Refresh Log")
        refreshBtn.Bind(wx.EVT_BUTTON, self.refresh)
        
        clearBtn = wx.Button(panel, -1, "clear Log")
        clearBtn.Bind(wx.EVT_BUTTON, self.clearlog)
        
        bruteBtn = wx.Button(panel, -1, "Brute Foce")
        bruteBtn.Bind(wx.EVT_BUTTON, self.brutentlm)
        
        
        closeBtn = wx.Button(panel, -1, "Close")
        closeBtn.Bind(wx.EVT_BUTTON, self.closeme)



        panel.SetBackgroundColour('#4f5049')
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.MultiLine = wx.TextCtrl(panel, -1, "",style = wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_AUTO_URL)
        self.MultiLine.SetBackgroundColour('#ededed')
        
        
        
        vbox.Add(self.MultiLine, 1, wx.EXPAND | wx.ALL, 10)
        vbox.Add(refreshBtn)
        vbox.Add(clearBtn)
        vbox.Add(bruteBtn)
        vbox.Add(closeBtn)
        panel.SetSizer(vbox)
	
    def clearlog(self, e):
        open('/usr/local/var/log/radius/freeradius-server-wpe.log', 'w').close()
	
    def brutentlm(self, e):
        import ntml_bruter 
        ntml_bruter.launch_ntlm_cracker()
	
    def closeme(self, e):
        self.Close()
		
    def refresh(self, e):
		pathtofile ="/usr/local/var/log/radius/freeradius-server-wpe.log"
		if os.path.exists(pathtofile) and os.path.getsize(pathtofile) > 5:
			with open(pathtofile) as f:
				for i in f:
					self.MultiLine.AppendText(i)
		else:
			self.MultiLine.AppendText("No Logs Found Yet :(\n")
			



#if __name__ == '__main__':
	
def launch_ntlm_cracker():
  
    app = wx.App()
    Example(None, title='NTLM Cracker')
    app.MainLoop()


#~ launch_ntlm_cracker()
