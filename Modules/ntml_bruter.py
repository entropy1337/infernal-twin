import os
import subprocess
import wx


class wpa2enterprise_cracker(wx.Frame):
    def __init__(self, parent, title):

        # ~ wx.Frame.__init__(self, parent, id)
        # ~
        super(wpa2enterprise_cracker, self).__init__(parent, title=title)

        # ~ self.InitUI()
        self.Centre()
        self.Show()

        panel = wx.Panel(self, -1)
        # wx.StaticText(panel, -1, 'See Logs for results\ncaptures/key_found.txt', (45, 25), style=wx.ALIGN_CENTRE)

        g_challenge = ""
        g_response = ""
        filepath = ""

        self.CreateStatusBar()

        # ~ menuBar = wx.MenuBar()
        # ~ menu = wx.Menu()
        # ~ menu.Append(99,  "&WPA2 Cracker", "Crack WPA/WPA2 handshakes")
        # ~ menuBar.Append(menu, "&Load Dictionary File")
        # ~ self.SetMenuBar(menuBar)
        # ~ self.Bind(wx.EVT_MENU, self.openfile, id=99)


        wbtn = wx.Button(panel, -1, label='Choose wordlist', pos=(10, 40))
        wbtn.Bind(wx.EVT_BUTTON, self.openfile)

        challenge = wx.TextCtrl(panel, -1, "Enter the Challenge", size=(250, 30), pos=(10, 80))
        response = wx.TextCtrl(panel, -1, "Enter the Response", size=(250, 30), pos=(10, 120))

        self.g_challenge = challenge
        self.g_response = response

        # ~ capbtn = wx.Button(panel, label='Choose capture file',pos=(10,80))
        # ~ capbtn.Bind(wx.EVT_BUTTON, self.openhash)

        brutebtn = wx.Button(panel, -1, label='Start bruteforce', pos=(10, 155))
        brutebtn.Bind(wx.EVT_BUTTON, self.bruteforce)

    wordlist = ""

    def openhash(self, event):

        dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.*", wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.mypath = os.path.basename(path)
            self.SetStatusText("You selected: %s" % self.mypath)

        self.wordlist = str(path)
        print self.wordlist

        dlg.Destroy()

    def openfile(self, event):

        dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.*", wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.mypath = os.path.basename(path)
            self.SetStatusText("You selected: %s" % self.mypath)

            # os.system("gnome-terminal -x aircrack-ng -w "+str(path)+" captures/*.cap -l captures/key_found.txt")
            self.capturelist = str(path)
            dlg.Destroy()
            # ~ print self.capturelist+str(self.mypath)
            self.filepath = self.capturelist

    def bruteforce(self, event):

        # ~ print self.g_challenge.GetValue()
        # ~ print self.g_response.GetValue()
        # ~ print self.wordlist
        # ~ print 'wordlist should be here'


        # ~ os.system("gnome-terminal -x asleap -C "+self.g_challenge+" -R "+self.g_response+" -W "+self.wordlist+ " read")
        try:

            print str(self.wordlist)
            test = subprocess.Popen(
                ["asleap", "-C", str(self.g_challenge.GetValue()), "-R", str(self.g_response.GetValue()), "-W",
                 str(self.filepath)], stdout=subprocess.PIPE)
            output = test.communicate()[0]
            tmpoutput = output[79:]

        except Exception:
            wx.MessageBox('Make sure to Correct Challenge/Response or provide a dictionary', 'Error', wx.ICON_ERROR)
            # ~ mychall = self.g_challenge.GetValue()
            # ~ myres = self.g_response.GetValue()

        if "Sorry it didn't work out" not in output:
            wx.MessageBox('Found Password\n' + tmpoutput, 'Result', wx.ICON_INFORMATION)
        else:
            wx.MessageBox('Password not in the dictionary', 'Result', wx.ICON_ERROR | wx.ICON_INFORMATION)

            # ~ print self.g_challenge
            # ~ print self.g_response


def launch_ntlm_cracker():
    app = wx.App()
    wpa2enterprise_cracker(None, title='NTLM Cracker')
    app.MainLoop()
