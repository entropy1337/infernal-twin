import wx
import os, sys

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
      wx.Frame.__init__(self, parent, id, title)
      
      panel = wx.Panel(self,-1)
      wx.StaticText(panel, -1, 'See Logs for results\ncaptures/key_found.txt', (45, 25), style=wx.ALIGN_CENTRE)
      

      self.CreateStatusBar()
      menuBar = wx.MenuBar()
      menu = wx.Menu()
      menu.Append(99,  "&WPA2 Cracker", "Crack WPA/WPA2 handshakes")
      #~ menu.Append(100, "&NTLM Cracker", "Crack NTLM Hashes")
      #~ menu.Append(101, "&File Dialog", "Shows a File Dialog")
      #~ menu.Append(102, "&Page Setup Dialog", "Shows a Page Setup Dialog")
      #~ menu.Append(103, "&Font Dialog", "Shows a Font Dialog")
      #~ menu.Append(104, "&Directory Dialog", "Shows a Directory Dialog")
      #~ menu.Append(105, "&SingleChoice Dialog", "Shows a SingleChoice Dialog")
      #~ menu.Append(106, "&TextEntry Dialog", "Shows a TextEntry Dialog")
      menuBar.Append(menu, "&Cracker")
      self.SetMenuBar(menuBar)

      self.Bind(wx.EVT_MENU, self.openfile, id=99)
      
      #dlg.Destroy()
      #~ def results_output(self, e):
		  #~ with open('captures/key_found.txt') as f:
			  #~ for i in f:
				  #~ 
				  #~ if i == "":
					  #~ 
					  #~ wx.StaticText(panel, -1, "Key is not found: ", (45, 25), style=wx.ALIGN_CENTRE)
					  #~ self.Centre()
				  #~ else:
					  #~ wx.StaticText(panel, -1, "Key is  found: " + str(i), (45, 25), style=wx.ALIGN_CENTRE)
					  #~ self.Centre()
					  	
				
      #~ self.Bind(wx.EVT_MENU, self.choosecolor, id=100)
      #~ self.Bind(wx.EVT_MENU, self.openfile, id=101)
      #~ self.Bind(wx.EVT_MENU, self.pagesetup, id=102)
      #~ self.Bind(wx.EVT_MENU, self.choosefont, id=103)
      #~ self.Bind(wx.EVT_MENU, self.opendir, id=104)
      #~ self.Bind(wx.EVT_MENU, self.singlechoice, id=105)
      #~ self.Bind(wx.EVT_MENU, self.textentry, id=106)

    #~ def message(self, event):
        #~ dlg = wx.MessageDialog(self, 'To save one life is as if you have saved the world.', 'Talmud', wx.OK|wx.ICON_INFORMATION)
        #~ dlg.ShowModal()
        #~ dlg.Destroy()

    #~ def choosecolor(self, event):
        #~ dlg = wx.ColourDialog(self)
        #~ dlg.GetColourData().SetChooseFull(True)
        #~ if dlg.ShowModal() == wx.ID_OK:
            #~ data = dlg.GetColourData()
            #~ self.SetStatusText('You selected: %s\n' % str(data.GetColour().Get()))
        #~ dlg.Destroy()

    def openfile(self, event):
		
       dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.*", wx.OPEN)
       
       if dlg.ShowModal() == wx.ID_OK:
		   
                path = dlg.GetPath()
                mypath = os.path.basename(path)
                self.SetStatusText("You selected: %s" % mypath)
                os.system("gnome-terminal -x aircrack-ng -w "+str(path)+" captures/*.cap -l captures/key_found.txt")
			
		dlg.Destroy()              
    
		

						
    #~ def pagesetup(self, event):
        #~ dlg = wx.PageSetupDialog(self)
        #~ if dlg.ShowModal() == wx.ID_OK:
            #~ data = dlg.GetPageSetupData()
            #~ tl = data.GetMarginTopLeft()
            #~ br = data.GetMarginBottomRight()
            #~ self.SetStatusText('Margins are: %s %s' % (str(tl), str(br)))
        #~ dlg.Destroy()

    #~ def choosefont(self, event):
        #~ default_font = wx.Font(10, wx.SWISS , wx.NORMAL, wx.NORMAL, False, "Verdana")
        #~ data = wx.FontData()
        #~ if sys.platform == 'win32':
            #~ data.EnableEffects(True)
        #~ data.SetAllowSymbols(False)
        #~ data.SetInitialFont(default_font)
        #~ data.SetRange(10, 30)
        #~ dlg = wx.FontDialog(self, data)
        #~ if dlg.ShowModal() == wx.ID_OK:
            #~ data = dlg.GetFontData()
            #~ font = data.GetChosenFont()
            #~ color = data.GetColour()
            #~ text = 'Face: %s, Size: %d, Color: %s' % (font.GetFaceName(), font.GetPointSize(),  color.Get())
            #~ self.SetStatusText(text)
        #~ dlg.Destroy()
#~ 
    #~ def opendir(self, event):
        #~ dlg = wx.DirDialog(self, "Choose a directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        #~ if dlg.ShowModal() == wx.ID_OK:
            #~ self.SetStatusText('You selected: %s\n' % dlg.GetPath())
        #~ dlg.Destroy()
#~ 
    #~ def singlechoice(self, event):
        #~ sins = ['Greed', 'Lust', 'Gluttony', 'Pride', 'Sloth', 'Envy', 'Wrath']
        #~ dlg = wx.SingleChoiceDialog(self, 'Seven deadly sins', 'Which one?', sins, wx.CHOICEDLG_STYLE)
        #~ if dlg.ShowModal() == wx.ID_OK:
            #~ self.SetStatusText('You chose: %s\n' % dlg.GetStringSelection())
        #~ dlg.Destroy()
#~ 
    #~ def textentry(self, event):
        #~ dlg = wx.TextEntryDialog(self, 'Enter some text','Text Entry')
        #~ dlg.SetValue("Default")
        #~ if dlg.ShowModal() == wx.ID_OK:
            #~ self.SetStatusText('You entered: %s\n' % dlg.GetValue())
        #~ dlg.Destroy()
        

class MyApp(wx.App):
    def OnInit(self):
        myframe = MyFrame(None, -1, "Cracker")
        myframe.CenterOnScreen()
        myframe.Show(True)
        return True
#~ 
