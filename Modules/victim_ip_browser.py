#!/usr/bin/python
from scapy.all import *
import re

client_list = {}

def http_header(packet):
    http_packet = str(packet)
    if http_packet.find('GET'):
        return GET_print(packet)

def GET_print(packet1):
    ret = "\n".join(packet1.sprintf("{Raw:%Raw.load%}{IP:%IP.src% -> %IP.dst%\n}\n").split(r"\r\n"))
    if 'User-Agent:' not in ret:
        return

    match = re.search(r'User-Agent: .*', ret)
    useragent = match.group(0)
    match2 = re.search(r'[0-9]+(?:\.[0-9]+){3} ', ret)
    ip_address = match2.group(0)

    if ip_address in client_list:
        return

    with open('./Modules/connected_clients.txt', 'a') as fhandle:
        client_list[ip_address] = useragent
        fhandle.write(ip_address + " : " + useragent +"\n")

    print client_list
    return ret

sniff(prn=http_header)
