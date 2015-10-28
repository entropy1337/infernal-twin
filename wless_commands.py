from scapy.all import *
import multiprocessing
import re
import subprocess
import time

__author__      = "Khalilov Mukhammad"
__copyright__   = "GNU V3.0"

def start_probing(packet_num):
	def prob_request():
		
		os.system("airmon-ng start wlan0")
		os.system("airmon-ng start wlan1")
		os.system("airmon-ng start wlan2")
		os.system("airmon-ng start wlan3")
	
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
		
		proc = subprocess.Popen(["ls /sys/class/net"], stdout=subprocess.PIPE, shell=True)
		(out, err) = proc.communicate()

		m = re.search('[wma]\S*', out)

		monitoring_interface =  m.group(0)

#~ print monitoring_interface
		#~ print "Number of packes to capture: " + numPackets
		#~ print 'number of packets' + str(packet_num)		
		sniff(iface=monitoring_interface, prn=sniffProbs, count=packet_num)
		
	prob_request()
	os.system("airmon-ng stop mon0")

#~ start_probing()
 # iwconfig wlan0 mode monitor
  # iwconfig wlan0 channel <i>
  # tshark -i wlan0 subtype probereq
