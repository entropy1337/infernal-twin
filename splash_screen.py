##
## DO NOT EDIT
##
#----------------------------------------------------------------------#
# This is a minimal wxPython program to show a SplashScreen widget.
#
# Tian Xie
# 3/8/2005
#----------------------------------------------------------------------#

import wx

class MyGUI(wx.Frame):
    """
Hello World!
    """
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
# Put more GUI code here for a fancier application.
#----------------------------------------------------------------------#

class MySplashScreen(wx.SplashScreen):
    """
Create a splash screen widget.
    """
    def __init__(self, parent=None):
        # This is a recipe to a the screen.
        # Modify the following variables as necessary.
        aBitmap = wx.Image(name = "ninja_tux.png").ConvertToBitmap()
        splashStyle = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT
        splashDuration = 2000 # milliseconds
        # Call the constructor with the above arguments in exactly the
        # following order.
        wx.SplashScreen.__init__(self, aBitmap, splashStyle,
                                 splashDuration, parent)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        wx.Yield()
#----------------------------------------------------------------------#

    def OnExit(self, evt):
        self.Hide()
        # MyFrame is the main frame.
        MyFrame = MyGUI(None, -1, "Hello from wxPython")
        app.SetTopWindow(MyFrame)
        MyFrame.Show(True)
        # The program will freeze without this line.
        evt.Skip()  # Make sure the default handler runs too...
#----------------------------------------------------------------------#

class MyApp(wx.App):
    def OnInit(self):
        MySplash = MySplashScreen()
        MySplash.Show()

        return True
#----------------------------------------------------------------------#

app = MyApp(redirect=True, filename = "infernal_wireless_gui.py")
app.MainLoop()
