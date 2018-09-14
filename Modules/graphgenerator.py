import re
import random
import os
def add_ssid():
	replacestring = ''
	graphdata=[]
	ssid_list = open('./Modules/Logs/sniffer/access_list.txt','r').readlines()
	for line in ssid_list:
		searchline = line.strip()
		try:
			ssid = re.search( r"\[ESSID\]-> \'*.*\'", searchline).group(0).replace("[ESSID]->","").replace('\'','').strip()
			beacon = re.search( r"Beacon:*.*[0-9]\ ", searchline).group(0).replace("Beacon: ","")
			concat = "'"+ssid+"'"+","+beacon.strip()+","+str(random.randint(1,100))+",'"+ssid+"',"+beacon.strip()
			graphdata.append('['+concat+'],')
		except:
			pass
	
	searchssid = open('./Modules/Logs/sniffer/wirelesschart.html','r').read()
	newgraphfile = open('./Modules/Logs/sniffer/wirelesschart2.html','w')

	myreplace= graphdata
	substring= str(myreplace).replace('["','').replace(']"','').replace('"','').replace(', ','\n')[:-1]
	
	replace_regext = "<!--start-->([^:]*)<!--replaceme-->"

	replacestring = re.sub(replace_regext,'<!--start-->\n'+substring+'\n<!--replaceme-->',searchssid)
	newgraphfile.write(replacestring)
	
	replacefile = open("./Modules/Logs/sniffer/wirelesschart.html","w")
	replacefile.write(replacestring)
	replacefile.close()
	os.system("firefox ./Modules/Logs/sniffer/wirelesschart.html&")
	
	
	


