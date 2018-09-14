#!/usr/bin/python
import logging
from scapy.all import *

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
import re

client_list = {}


def http_header(packet):
    http_packet = str(packet)
    if http_packet.find('GET') or http_packet.find('POST'):
        return GET_print(packet)


def GET_print(packet1):
    ret = "\n".join(packet1.sprintf("{Raw:%Raw.load%}{IP:%IP.src% -> %IP.dst%\n}\n").split(r"\r\n"))

    if 'User-Agent:' in ret:
        m = re.search('User-Agent: .*', ret)
        useragent = m.group(0)

        # ~ m2 = re.search('[0-9]+(?:\.[0-9]+){3} ', ret)
        # ~ ip_address = m2.group(0)
        if re.search('[0-9]+(?:\.[0-9]+){3} ', ret):
            m2 = re.search('[0-9]+(?:\.[0-9]+){3} ', ret)
            ip_address = m2.group(0)
        else:
            ip_address = 'localhost'

        if ip_address:  # not in client_list:
            if ret not in client_list.values():

                connected_clients = open('./Modules/MiTM_data.txt', 'a')

                client_list[ip_address] = useragent

                payload_array = ret.split('\n')

                for i in payload_array:
                    if 'POST /' in i or 'GET /' in i:
                        connected_clients.write(ip_address + " : " + "\n" + ret + "\n")

                        connected_clients.close()
                    # ~ print client_list
                return ret


sniff(prn=http_header)
