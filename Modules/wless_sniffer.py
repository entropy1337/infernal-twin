from scapy.all import *
import multiprocessing
import time

__author__      = "Khalilov Mukhammad"
__copyright__   = "GNU V3.0"

def start_probing():
	def prob_request():
		
		os.system("airmon-ng start wlan0")
	
		prob_log = open('prob_request.txt','a')
		#interface = str(monitor)
	
		probReqs = []
		def sniffProbs(p):
			if p.haslayer(Dot11):
				if p.type == 0 and p.subtype == 8:
					if p.addr2 not in probReqs:
						probReqs.append(p.addr2)
						print "AP MAC: %s with SSID %s" %(p.addr2, p.info)
		
				
		sniff(iface='mon0', prn=sniffProbs)
	prob_request()
	os.system("airmon-ng stop mon0")

start_probing()
