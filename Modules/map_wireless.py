import os
import os.path
import wx

import wless_commands

dumpfilename = ''


class SnifferGUI(wx.Frame):
    def __init__(self, parent, title):
        super(SnifferGUI, self).__init__(parent, title=title, size=(400, 350))

        self.InitUI()
        self.Centre()
        self.Show()

    def InitUI(self):

        panel = wx.Panel(self)
        # ~ panel.SetBackgroundColour('#4f5049')

        # ~






        # ~ wless_commands.get_monitoring_interfaces()
        # ~ self.comboBox = wx.ComboBox(panel, -1, value='Select SSID', size=(400, 50), pos=(10, 50), choices = ssid_victim)
        # ~ self.valueSlider = wx.Slider(panel, -1, minValue=10, maxValue=200, pos=(10,130), size=(400,50),style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS|wx.SL_LABELS)
        self.nDeviceList = wx.ComboBox(panel, -1, value='Select Net Interface', size=(200, 30), pos=(10, 90),
                                       choices=wless_commands.get_net_devices())
        self.filename = wx.TextCtrl(panel, -1, "File name", size=(250, 30), pos=(10, 20))
        self.actionButton = wx.Button(panel, -1, label='Start Mapping', pos=(10, 135))

        self.stopActionButton = wx.Button(panel, -1, label='Stop Mapping', pos=(150, 135))

        self.generateImage = wx.Button(panel, -1, label='Generate PNG MAP', pos=(10, 175))

        self.closeButton = wx.Button(panel, -1, label='Close', pos=(162, 175))
        # ~
        self.myLabel = wx.StaticText(panel, -1, label='', pos=(10, 210))
        # ~
        # ~
        # ~
        self.actionButton.Bind(wx.EVT_BUTTON, self.executeCommand)
        self.stopActionButton.Bind(wx.EVT_BUTTON, self.stopExecuteCommand)
        self.closeButton.Bind(wx.EVT_BUTTON, self.closeMe)
        self.generateImage.Bind(wx.EVT_BUTTON, self.generateImageAction)

    # ~


    # ~ self.on_timer()
    def closeMe(self, e):
        # ~ os.system('echo "" > ./Modules/deauthSSID.txt')
        self.Close()

    def stopExecuteCommand(self, e):
        os.system("kill  `ps aux | grep airodump-ng | head -1 | awk '{print $2}'`")

    def generateImageAction(self, e):
        global dumpfilename

        mcommand = "airgraph-ng -i Modules/Logs/" + str(dumpfilename) + "/" + str(
            dumpfilename) + "*.csv -o Modules/Logs/" + str(dumpfilename) + "/" + str(dumpfilename) + ".png -g CAPR"

        os.system(mcommand)
        self.myLabel.SetLabel('Location of the file is:\nModules/Logs/%s' % dumpfilename)

    def executeCommand(self, e):

        global dumpfilename

        attackInterface = self.nDeviceList.GetValue()
        dumpfilename = self.filename.GetValue()

        # ~ wlan_ifaces = wless_commands.get_monitoring_interfaces()

        # ~ print '***********'
        # ~ print ssidsplitter[0]
        # ~ print ssidsplitter[1]
        # ~ print ssidsplitter[2]
        # ~ print attackInterface
        # ~ print '***********'
        # ~ print "gnome-terminal -x aireplay-ng --deauth "+str(int(myslider))+" -a "+ssidsplitter[0]+" -e "+str(ssidsplitter[1])+" "+attackInterface+" --ignore-negative-one"
        try:
            os.system('mkdir ./Modules/Logs/' + str(dumpfilename))
        except:
            wx.MessageBox('Choose Different name', 'Information', wx.ICON_INFORMATION)

        try:

            if attackInterface == 'mon0':
                # ~ print 'iw dev '+attackInterface+' interface add mon0 type monitor'
                os.system("airodump-ng -w ./Modules/Logs/" + str(dumpfilename) + "/" + str(
                    dumpfilename) + " " + attackInterface + "&")

            # ~ os.system("airgraph-ng -i "+str(dumpfilename)+"/"+str(dumpfilename)+"*.csv -o "+str(dumpfilename)+"/"+str(dumpfilename)+".png -g CAPR")
            # ~ print 'iwconfig '+attackInterface+' channel '+str(ssidsplitter[2])
            # ~ print "gnome-terminal -x aireplay-ng --deauth "+int(myslider)+" -a "+ssidsplitter[0]+" -e "+str(ssidsplitter[1])+" "+attackInterface+" --ignore-negative-one"
            else:

                os.system('iw dev ' + attackInterface + ' interface add mon0 type monitor')
                os.system("airodump-ng -w ./Modules/Logs/" + str(dumpfilename) + "/" + str(dumpfilename) + " mon0")

            # ~ os.system("airgraph-ng -i "+str(dumpfilename)+"/"+str(dumpfilename)+"*.csv -o "+str(dumpfilename)+"/"+str(dumpfilename)+".png -g CAPR")
        except:
            print 'I need to fix this exception'






        # ~ os.system("gnome-terminal -x aireplay-ng -0 "+int(myslider)+" -a "+ssidsplitter[0]+" -e "+str(ssidsplitter[1])+" "+mon_iface+" --ignore-negative-one")
        # ~
        # ~ os.system('iw dev '+mon_iface+' interface add mon0 type monitor')
        # ~ os.system(os.system("gnome-terminal -x aireplay-ng -0 "+int(myslider)+" -a "+ssidsplitter[0]+" -e "+str(ssidsplitter[1])+" mon0 --ignore-negative-one"))
        # ~

        # ~ except:
        # ~ wx.MessageBox('Make sure to have the wireless card',
        # ~ 'Warning/Error', wx.ICON_ERROR | wx.ICON_INFORMATION)
        # ~

        # ~ def on_timer(self):
        # ~
        # ~ print 'Hello World'
        # ~


# ~ if __name__ == '__main__':

def main():
    app = wx.App(False)
    frame = SnifferGUI(None, 'Map Wireless Network')
    app.MainLoop()
