from scapy.all import *
import logging
import multiprocessing
import os
import re
import subprocess
import time

__author__      = "Khalilov Mukhammad"
__copyright__   = "GNU V3.0"

def start_probing(packet_num):
	def prob_request():
		start_airmon()
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
		

		monitoring_interfaces = get_monitoring_interfaces()
#~ print monitoring_interface
		#~ print "Number of packes to capture: " + numPackets
		#~ print 'number of packets' + str(packet_num)		
		sniff(iface=monitoring_interfaces[0], prn=sniffProbs, count=packet_num)
		
	prob_request()
	os.system("airmon-ng stop mon0")

def _parse_iw_scan(iw_output):
	"""Parse output of % iw <iface> scan; command."""
	parsed = []
	iw_net = {
		'BSS': None,
		'SSID': None,
		'ciphers': None,
	}
	reBSS = re.compile(r'^BSS [\w\d]{2}:.+\(')
	reGroup = re.compile(r'Group cipher: ')
	for line in iw_output.splitlines():
		line = line.strip()
		if line == '':
			continue

		if line.startswith('BSS '):
			match = reBSS.search(line)
			if not match:
				continue
			elif iw_net['BSS']:
				parsed.append(iw_net.copy())
				for key in iw_net:
					iw_net[key] = None

			iw_net['BSS'] = line.split('(', 1)[0].replace('BSS ', '')
		elif line.startswith('SSID: '):
			iw_net['SSID'] = line.split(':', 1)[1][1:]
		elif reGroup.search(line):
			iw_net['ciphers'] = line.split(':', 1)[1][1:]
		else:
			continue

	if iw_net['BSS']:
		parsed.append(iw_net.copy())

	return parsed

def bring_wlan_devs_up(devices=[]):
	"""Bring up all wlan interfaces."""
	if not devices:
		devices = sorted(get_net_devices())

	for dev in devices:
		if re.search(r'^wlan[0-9]$', dev):
			logging.debug('ifup at %s', dev)
			os.system("ifconfig %s up" % dev)

def get_net_device_info(device):
	"""Return information about given network device."""
	dev_path = '/sys/class/net/%s' % device
	if not os.path.isdir(dev_path):
		return None

	dev_info = {
		'mac_address': None,
		'link_state': None,
		'wireless': False,
	}
	if os.path.isdir('%s/wireless' % dev_path):
		dev_info['wireless'] = True

	dev_addr_path = '%s/address' % dev_path
	if os.path.exists(dev_addr_path):
		with open(dev_addr_path, 'r') as fh:
			dev_info['mac_address'] = fh.readline().strip()

	dev_state_path = '%s/operstate' % dev_path
	if os.path.exists(dev_state_path):
		with open(dev_state_path, 'r') as fh:
			dev_info['link_state'] = fh.readline().strip()

	return dev_info

def get_net_devices():
	"""Return list of network devices."""
	with open('/proc/net/dev', 'r') as fhandle:
		lines = [line.lstrip() for line in fhandle.readlines()]

	return [line.split(':', 1)[0] for line in lines
		if not (line.startswith('face') or line.startswith('Inter-'))]

def get_monitoring_interfaces():
	return [dev for dev in sorted(get_net_devices())
		if re.match(r'[wma]\S*', dev)]

def get_wireless_scan(device):
	"""Return parsed wireless scan from given interface."""
	logging.debug('WiFi scan in progress at %s.', device)
	bring_wlan_devs_up([device])
	proc1 = subprocess.Popen(['iw', device, 'scan'],
			stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = proc1.communicate()
	if proc1.returncode != 0:
		raise ValueError

	logging.debug('WiFi scan complete.')
	return _parse_iw_scan(out)

def start_airmon(devices=[]):
	"""Start airmon at all wlan interfaces."""
	if not devices:
		devices = sorted(get_net_devices())

	for dev in devices:
		if re.match(r'^wlan[0-9]$', dev):
			os.system("airmon-ng start %s" % dev)

#~ start_probing()
 # iwconfig wlan0 mode monitor
  # iwconfig wlan0 channel <i>
  # tshark -i wlan0 subtype probereq
