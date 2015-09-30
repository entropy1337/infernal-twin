from scapy.all import *
import multiprocessing
import time

__author__      = "Khalilov Mukhammad"
__copyright__   = "GNU V3.0"

def start_probing():
	def prob_request():
		
		os.system("airmon-ng start wlan2")
	
		prob_log = open('prob_request.txt','a')
		#interface = str(monitor)
	
		probReqs = []
		def sniffProbs(p):
			if p.haslayer(Dot11ProbeReq):
				netName = p.getlayer(Dot11ProbeReq).info 
				if netName not in probReqs:
					probReqs.append(netName)
					print str(netName)
					prob_log.write(netName+'\n')
				
		sniff(iface='mon0', prn=sniffProbs, count=3000)
	prob_request()
	os.system("airmon-ng stop mon0")

#~ start_probing()
 # iwconfig wlan0 mode monitor
  # iwconfig wlan0 channel <i>
  # tshark -i wlan0 subtype probereq
