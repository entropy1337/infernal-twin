import os,re

def generate_probe():
	
	dictProbes = {}
	machines = []
	ssidlist = []
	
	htmlSSID = []
	htmlProbe = []
	
	readProbe = open('./Modules/Logs/sniffer/probe_list.txt','r')
	
	for probe in readProbe:
		if len(probe) > 2:
			 
			splitSSID= probe.strip().replace("'","").split(' : ')
			htmlSSID.append("['"+splitSSID[0]+"'"+','+"'"+splitSSID[1]+"'"+",''],")
			
			if splitSSID[1] not in ssidlist:
				ssidlist.append(splitSSID[1])
				htmlProbe.append("['"+splitSSID[1]+"', 'Probe Request', ''],")
	
	ssidreplace= str(htmlProbe).replace('["','').replace('", ','').replace('"]','').replace('"','')
	
	probereplace =str(htmlSSID).replace('["','').replace('", ','').replace('"]','').replace('"','')
	
	
	searchssid = open('./Modules/Logs/sniffer/probeChart.html','r').read()
	
	newgraphfile = open('./Modules/Logs/sniffer/probeChart2.html','w')
	
	replace_regext = "<!--start-->([^*]*)<!--replaceme-->"
	
	replacestring = re.sub(replace_regext,'<!--start-->\n'+ssidreplace+probereplace+'\n<!--replaceme-->',searchssid)
	newgraphfile.write(replacestring)
	
	replacefile = open("./Modules/Logs/sniffer/probeChart.html","w")
	replacefile.write(replacestring)
	replacefile.close()
	os.system("firefox ./Modules/Logs/sniffer/probeChart.html&")		
		


