from scapy.all import *
import os
from random import randint
import thread
from threading import Thread 
from wx.lib.pubsub import pub as Publisher
import wx

client_macs = []
client_probe_mac = []
packet_capture = False

refresh_threader = True
connected_seen_clients = []
nDevices = 0
nProbes = 0

ssids = set()
tssid = None
found_probe_request = []
found_client_mac = []
ssid_dictionary = {}
mylist = set()
essid_details = set()
probe_dict = {}

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
				temp = temp.getlayer(Dot11Elt)
				cap = pkt.sprintf("{Dot11Beacon:%Dot11Beacon.cap%}" "{Dot11ProbeResp:%Dot11ProbeResp.cap%}").split('+')
				
				
				if temp and temp.ID == 0 and (pkt.addr3 not in ssids):
					global essid
					global bssid
					global ssid_dictionary
				
					
					if essid != '':
						essid = pkt.info
						ssid_dictionary[bssid] = essid
						
					else:
						essid = 'Unknown'
						ssid_dictionary[bssid] = essid
						
					bssid = pkt.addr3
					ssid_dictionary[bssid] = essid
					ssids.add(bssid)
					
				elif temp and temp.ID == 221:
					encryption = 'WPA/WPA2'
					
			
					
					
					global tssid
					
					
					tssid = str(str(bssid) + ' : ' + str(essid) + ' : ' + str(encryption))
					ssid_dictionary[bssid]=essid
					#~ print ssid_dictionary
					######### write to file #######
						
					
					#
					if tssid not in new_ssid:
						
						global found_ssids
						
						new_ssid.append(tssid)
						found_ssids = tssid
						
						######## write to file #######
						with open('access_list.txt','a') as f:
							f.write(tssid+'\n')
						######## write to file #######
						
					
				
					
					
					
					break
					 	
					
				temp = temp.payload
			##################### WIFI SNIFFER WITH ENCRYPTION #################	
		
		if pkt.haslayer(Dot11):
					
			###################### PROBE SNIFFER ##############
			if pkt.type == 0 and pkt.subtype == 4:
				if pkt.addr2 + ' : '+pkt.info not in found_probe_request:
					
					
					
					
					if pkt.info != '':
						found_probe_request.append(pkt.addr2 + ' : '+pkt.info)
						
						######### write to file #######
						global found_probes
						global probe_dict
						global client_macs
						
						found_probes = pkt.addr2 + ' : '+pkt.info
						
						client_macs.append(pkt.addr2)
						
						
						with open('probe_list.txt','a') as f:
							f.write(pkt.addr2 + ' : '+pkt.info+'\n')
						######### write to file #######
						
						if pkt.addr2 not in probe_dict.keys():
							probe_dict[pkt.addr2] = pkt.info
							global nDevices
							nDevices = nDevices + 1
							#print probe_dict
							
						else:
							tmp = probe_dict[pkt.addr2]
							probe_dict[pkt.addr2] = tmp + ';' + pkt.info
							#print probe_dict
							
				
						
							
			###################### PROBE SNIFFER ##############
			
			
			###################### CONNECTION SNIFFER ##############			
			if pkt.type == 2 and pkt.subtype == 4:
				if pkt.addr1 + ' : ' + pkt.addr2 not in found_client_mac:
					if pkt.addr1 in ssid_dictionary.keys():
						found_client_mac.append(pkt.addr1 + ' : ' + pkt.addr2)
						with open('connection_list.txt','a') as f:
							
							f.write(pkt.addr1 + ' : ' + pkt.addr2 + ' : ' + ssid_dictionary[pkt.addr1]+'\n')
							

			###################### CONNECTION SNIFFER ##############
				
	
class SnifferGUI(wx.Frame):
	def __init__(self, parent, title):
		super(SnifferGUI, self).__init__(parent, title=title, size=(1100,700))
		
		self.InitUI()
		self.Centre()
		self.Show()
	
	def InitUI(self):
    		
		panel = wx.Panel(self)
		panel.SetBackgroundColour('#4f5049')
		
		global SSID_textControl
		global ConnectionsTextControl
		global probeTextControl
		
		
		menubar = wx.MenuBar()
		fileMenu = wx.Menu()
		fitem = fileMenu.Append(-1, 'Start Sniffer', 'Start sniffer')
		fitem2 = fileMenu.Append(-1, 'Stop Sniffer', 'Stop Sniffer')
		fitem3 = fileMenu.Append(-1, 'Quit Sniffer', 'Quit Sniffer')
		
		menubar.Append(fileMenu, 'Action')
		
		self.SetMenuBar(menubar)
		
		self.Bind(wx.EVT_MENU, self.OnStartSniff, fitem)
		self.Bind(wx.EVT_MENU, self.OnStopSniff, fitem2)
		self.Bind(wx.EVT_MENU, self.onQuitApp, fitem3)


		
		
		
			
		self.ssidText = wx.StaticText(panel,-1, 'Found Probe Requesting Devices: ' + str(nDevices),pos=(5,5))	
		self.ssidText.SetForegroundColour((0,255,0))
		
		self.SSID_textControl = wx.TextCtrl(panel, size=(540, 400), pos=(5,30), style=wx.TE_MULTILINE | wx.TE_READONLY)
		self.SSID_textControl = wx.TreeCtrl(panel,-1, size=(540, 400), pos=(5,30), style=wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_EDIT_LABELS)
        
		self.root = self.SSID_textControl.AddRoot('Probe Requests')
		
		ConnectionText = wx.StaticText(panel,-1, 'Found Connection List to Access Points',pos=(550,5))	
		ConnectionText.SetForegroundColour((255,0,0))
		
		
		
		self.ConnectionsTextControl = wx.TextCtrl(panel,size=(540, 400), pos=(550,30),  style=wx.TE_MULTILINE| wx.TE_READONLY)
		
		
		
		
		self.probeTextControl = wx.TextCtrl(panel, size=(1084, 222), pos=(5,435), style=wx.TE_MULTILINE | wx.TE_READONLY)
		
		
		self.on_timer()
		
		
		
		
	


		
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
		os.system('echo ""> connection_list.txt;echo ""> access_list.txt;echo ""> probe_list.txt')
		os.system("kill `ps aux | grep wifi_snifferv1 | head -1 | awk '{print $2}'`")
	
	def AddProbeClients(self):
		self.SSID_textControl.DeleteChildren(self.root)

		for client_mac in probe_dict.keys():

			client_mac_found = self.SSID_textControl.AppendItem(self.root,"%s"%(client_mac))
			ssid_list2 = probe_dict[client_mac].split(';')
			for i in ssid_list2:
				
				try: 
					i = i.encode('ascii', 'ignore')
					self.SSID_textControl.AppendItem(client_mac_found, i)
				except UnicodeDecodeError:
					print ':'.join(x.encode('hex') for x in i)
					
			
			
	
	def channelHopper2(self):
		
		
		while threadder:
			rChannel = randint(1,14)
			os.system('iwconfig mon0 channel %d'%rChannel)
			
		
	def on_timer(self):
		global ssid_list
		global probe_list 
		global connection_list
		
		self.AddProbeClients()

		rChannel = randint(1,14)
		os.system('iwconfig mon0 channel %d'%rChannel)
		os.system('touch probe_list.txt; touch connection_list.txt; touch access_list.txt')
		probe_list = open('probe_list.txt','r').readlines()
		
		connection_list = open('connection_list.txt','r').read()
		ssid_list = str(open('access_list.txt','r').read())
		probe_info = ''
		global client_macs
		global client_probe_mac

		self.ConnectionsTextControl.SetValue(connection_list)
		self.ssidText.SetLabel('Probing Devices Found: ' + str(nDevices))

		self.probeTextControl.SetValue(ssid_list)
		
		
		
		
		if refresh_threader == True:
			wx.CallLater(2000, self.on_timer)
			
			rChannel = randint(1,14)
			os.system('iwconfig mon0 channel %d'%rChannel)
		
		
	
if __name__ == '__main__':
	packet_capture = False
	
	app = wx.App(False)
	frame = SnifferGUI(None, 'Wireless Scanner')
	app.MainLoop()
	


os.system('rm connection_list.txt; rm access_list.txt; rm probe_list.txt')
