import wx
import os

class MainWindow(wx.Frame):
    def __init__(self, parent, id=-1):
        wx.Frame.__init__(self,parent,id, size=(800,600))

        self.panel = wx.Panel(self,wx.ID_ANY)     
        bsizer = wx.BoxSizer()
        read_only_txtCtrl = wx.TextCtrl(self.panel,-1, "", style=wx.TE_MULTILINE|wx.TE_READONLY, size=(800,600))
        
        def print_ip():
			os.system("touch connected_clients.txt")
			client_list = open("connected_clients.txt", 'r').read()
			read_only_txtCtrl = wx.TextCtrl(self,-1, client_list, style=wx.TE_MULTILINE|wx.TE_READONLY)
			bsizer.Add(read_only_txtCtrl, 1, wx.EXPAND)
               
        

        #~ editable_txtCtrl = wx.TextCtrl(self,-1,
                        #~ "This textCtrl is editable",
                        #~ style=wx.TE_MULTILINE)

        bsizer.Add(read_only_txtCtrl, 1, wx.EXPAND)
        #~ bsizer.Add(editable_txtCtrl, 1, wx.EXPAND)

        self.SetSizerAndFit(bsizer)
        
        os.system('python victim_ip_browser.py &')
        
        
        print_ip()
        
		

if __name__ == "__main__":
	
	

    app = wx.App()
    
    frame = MainWindow(None)
    #~ frame.SetSize((800,600))
    frame.Show()
    app.MainLoop()
    os.system("kill  `ps aux | grep victim_ip_browser.py | head -1 | awk '{print $2}'`")
