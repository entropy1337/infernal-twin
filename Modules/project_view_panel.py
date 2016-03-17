import wx
import wx.html
from wx.lib.wordwrap import wordwrap
 
class MyForm(wx.Frame):
 
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title='My Form')
 
        # Add a panel so it looks correct on all platforms
        self.panel = wx.Panel(self, wx.ID_ANY)
 
        
        aboutHtmlBtn = wx.Button(self.panel, wx.ID_ANY, "Open HtmlAboutBox")
        self.Bind(wx.EVT_BUTTON, self.onAboutHtmlDlg, aboutHtmlBtn)
 
        
 
        # Create Sizers
        topSizer = wx.BoxSizer(wx.VERTICAL)
 
        
        topSizer.Add(aboutHtmlBtn, 0, wx.ALL|wx.CENTER, 5)
        
        self.statusBar = self.CreateStatusBar()
 
        self.panel.SetSizer(topSizer)
        self.SetSizeHints(250,300,500,400)
        self.Fit()
        self.Refresh()
 
    
    def onAboutHtmlDlg(self, event):
        aboutDlg = AboutDlg(None)
        aboutDlg.Show()
 
   
 
class AboutDlg(wx.Frame):
 
    def __init__(self, parent):
 
        wx.Frame.__init__(self, parent, wx.ID_ANY, title="About", size=(400,400))
 
        html = wxHTML(self)
 
        html.SetPage(
            ''
 
            "<h2>About the About Tutorial</h2>"
 
            "<p>This about box is for demo purposes only. It was created in June 2006"
 
            "by Mike Driscoll.</p>"
 
            "<p><b>Software used in making this demo:</h3></p>"
 
            '<p><b><a href="http://www.python.org">Python 2.4</a></b></p>'
 
            '<p><b><a href="http://www.wxpython.org">wxPython 2.8</a></b></p>'
            )
 
class wxHTML(wx.html.HtmlWindow):
     def OnLinkClicked(self, link):
         webbrowser.open(link.GetHref())
 
 
# Run the program
def myMain():
    app = wx.PySimpleApp()
    frame = MyForm().Show()
    app.MainLoop()


myMain()
