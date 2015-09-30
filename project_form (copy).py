import wx
import infernal_wireless_gui_project
import os
class Example(wx.Frame):
	
	
	
    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title, 
            size=(600, 400))
            
        self.InitUI()
        self.Centre()
        self.Show()     
    
    global MultiLine
    isProject = False     
    global projectName
    def InitUI(self):
		
		
    
        panel = wx.Panel(self)
        
        self.quote = wx.StaticText(panel,-1, label="PROJECT DETAILS \n", pos=(10, 30))
        self.quote.SetForegroundColour((255,0,0)) # set text color
        
        #~ prjBtn = wx.Button(panel, -1, "Create a Project",size=(150,30), pos=(10,650))
        #~ prjBtn.Bind(wx.EVT_BUTTON, self.create_project)
        
        

        panel.SetBackgroundColour('#4f5049')
        #vbox = wx.BoxSizer(wx.VERTICAL)
        
        
        self.projectname = wx.TextCtrl(panel, -1, "Project Name",size=(250,30), pos=(10,120))
        #self.projectname.SetBackgroundColour('#ededed')
        
        
        self.author = wx.TextCtrl(panel, -1, "Author's Full Name'",size=(250,30), pos=(10,160))
        #self.author.SetBackgroundColour('#ededed')
        
        self.targetname = wx.TextCtrl(panel, -1, "Target Name",size=(250,30), pos=(10,200))
        #self.targetname.SetBackgroundColour('#ededed')
        
        self.datename = wx.TextCtrl(panel, -1, "dd/mm/yy",size=(250,30), pos=(10,240))
        #self.targetname.SetBackgroundColour('#ededed')        
        
        prjBtn = wx.Button(panel, -1, "Create a Project",size=(150,30), pos=(10,300))
        prjBtn.Bind(wx.EVT_BUTTON, self.create_project)        
        
        prjBtn2 = wx.Button(panel, -1, "Stand alone",size=(150,30), pos=(10,350))
        prjBtn2.Bind(wx.EVT_BUTTON, self.create_std)
        
        #~ vbox.Add(self.MultiLine, -1,10)
        #~ vbox.Add(prjBtn,-1, border=10)
        #~ panel.SetSizer(vbox)
	
	
    def create_project(self, e):
		isProject = True
		print isProject
		self.projectName = self.projectname.GetValue()
		#print self.projectName
		
		dic_project = {"Project":str(self.projectName),"Authors Full Name":str(self.author.GetValue()),"Target name":str(self.targetname.GetValue()),"Date":str(self.datename.GetValue())}
		
		os.system("mkdir %s"%str(self.projectName).replace(" ","_"))
		dic_project['Filename']=str(self.projectName).replace(" ","_")
		
		pFile = open(self.projectName.replace(" ","_")+"/Project Info.txt","wb")
		pFile.write(str(dic_project))
		pFile.close()
		
		
		infernal_wireless_gui_project.main()
		

	
		
    def create_std(self, e):
		isProject = False
		print isProject
		#print self.projectName
		
		infernal_wireless_gui_project.main()
	
    def returnproject(self):
		return self.projectName	
		
		
	

#if __name__ == '__main__':
	
def create_new_project():
  
    app = wx.App()
    Example(None, title='Create A project')
    app.MainLoop()
    




if __name__ == '__main__':
	create_new_project()


