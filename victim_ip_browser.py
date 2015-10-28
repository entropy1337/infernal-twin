#!/usr/bin/python
from scapy.all import *
import re

client_list = {}

def http_header(packet):
	
        http_packet=str(packet)
        if http_packet.find('GET'):
                return GET_print(packet)

def GET_print(packet1):
    ret = "\n".join(packet1.sprintf("{Raw:%Raw.load%}{IP:%IP.src% -> %IP.dst%\n}\n").split(r"\r\n"))
    
        
    if 'User-Agent:' in ret:
		m = re.search('User-Agent: .*', ret)
		useragent =  m.group(0)
			
		m2 = re.search('[0-9]+(?:\.[0-9]+){3} ', ret)
		ip_address = m2.group(0)
			
		
		if ip_address not in client_list:
			
			connected_clients = open('connected_clients.txt', 'a')
			
			client_list[ip_address] = useragent
			connected_clients.write(ip_address + " : " + useragent +"\n")
			connected_clients.close()
			print client_list
			return ret

sniff(prn=http_header)
