# ~ import infernal_wireless_gui_project
import MySQLdb
import os
import os.path
import sys
import wx
from datetime import datetime

from Modules import db_connect_creds
from Modules import db_setup

os.system('/etc/init.d/apache2 start >/dev/null 2>&1')
os.system('/etc/init.d/mysql start >/dev/null 2>&1')

if not os.path.exists('./Modules/dbconnect.conf'):
    # ~ print "DB Config 'dbconnect.conf' file doesn't seem to exist."

    print ""
    sys.exit(1)
if not os.path.exists('./Modules/Projects'):
    os.mkdir('./Modules/Projects')

date = datetime.now()
current_project_id = 0

# TODO - cleanup this too.
username, password = db_connect_creds.read_creds()
cxn = MySQLdb.connect('localhost', username, password)
cur = cxn.cursor()
db_setup.create_db(cur, db_setup.INFERNAL_DB, username, password)
cxn.commit()
cxn.close()

cxn = MySQLdb.connect('localhost', username, password, db=db_setup.INFERNAL_DB)
cur = cxn.cursor()
db_setup.create_projects_table(cur)
db_setup.create_reports_table(cur)


class Example(wx.Frame):
    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title,
                                      size=(600, 450))

        self.InitUI()

        self.Centre()
        self.Show()

    global MultiLine
    isProject = False
    global projectName

    # ~ self.projectIDNumber = 0
    def InitUI(self):
        panel = wx.Panel(self)

        self.quote = wx.StaticText(panel, -1, label="PROJECT DETAILS \n", pos=(10, 30))
        self.quote.SetForegroundColour((255, 0, 0))  # set text color

        start_image = wx.Image("Modules/img/logo2.png")
        start_image.Rescale(450, 450)
        image = wx.BitmapFromImage(start_image)
        pic = wx.StaticBitmap(panel, -1, image, pos=(150, 0), style=wx.BITMAP_TYPE_PNG)

        # ~ prjBtn = wx.Button(panel, -1, "Create a Project",size=(150,30), pos=(10,650))
        # ~ prjBtn.Bind(wx.EVT_BUTTON, self.create_project)
        # ~ start_image = wx.Image("img/logo2.png")
        # ~ start_image.Rescale(180, 140)
        # ~ image = wx.BitmapFromImage(start_image)
        # ~ pic=wx.StaticBitmap(pnl, -1, image, pos=(250, 50), style=wx.BITMAP_TYPE_PNG)

        panel.SetBackgroundColour('#4f5049')
        # vbox = wx.BoxSizer(wx.VERTICAL)

        self.projectname = wx.TextCtrl(panel, -1, "Project Name", size=(250, 30), pos=(10, 120))
        # self.projectname.SetBackgroundColour('#ededed')

        self.author = wx.TextCtrl(panel, -1, "Author's Full Name'", size=(250, 30), pos=(10, 160))
        # self.author.SetBackgroundColour('#ededed')

        self.targetname = wx.TextCtrl(panel, -1, "Target Name", size=(250, 30), pos=(10, 200))
        # self.targetname.SetBackgroundColour('#ededed')

        self.datename = wx.TextCtrl(panel, -1, "dd/mm/yy", size=(250, 30), pos=(10, 240))
        # self.targetname.SetBackgroundColour('#ededed')

        prjBtn = wx.Button(panel, -1, "Create a Project", size=(150, 30), pos=(10, 300))

        prjBtn.Bind(wx.EVT_BUTTON, self.create_project)

        prjBtn2 = wx.Button(panel, -1, "Stand alone", size=(150, 30), pos=(10, 350))
        prjBtn2.Bind(wx.EVT_BUTTON, self.create_std)

        # ~ vbox.Add(self.MultiLine, -1,10)
        # ~ vbox.Add(prjBtn,-1, border=10)
        # ~ panel.SetSizer(vbox)

    def project_details(self, projectname, Authors_name, TargetName, date):
        PROJECT_DETAILS = 'INSERT INTO Projects (ProjectName, AuditorName, TargetName, date) VALUES ("%s","%s","%s","%s")' % (
        projectname, Authors_name, TargetName, date)
        cur.execute(PROJECT_DETAILS)
        current_project_id_tmp = cur.lastrowid
        current_project_id = current_project_id_tmp

    # ~ cur.close()
    # ~ cxn.commit()
    # ~ cxn.close()
    # ~ print "report is generated"

    def create_project(self, e):
        isProject = True
        # ~ print isProject
        self.projectName = self.projectname.GetValue()
        # print self.projectName
        dic_project = {"Project": str(self.projectName), "Authors Full Name": str(self.author.GetValue()),
                       "Target name": str(self.targetname.GetValue()), "Date": str(self.datename.GetValue())}
        os.system("mkdir Modules/Projects/%s" % str(self.projectName).replace(" ", "_"))
        dic_project['Filename'] = str(self.projectName).replace(" ", "_")

        pFile = open("./Modules/Projects/" + self.projectName.replace(" ", "_") + "Project Info.txt", "wb")
        pFile.write(str(dic_project))
        pFile.close()

        prID = self.project_details(str(self.projectName), str(self.author.GetValue()), str(self.targetname.GetValue()),
                                    str(self.datename.GetValue()))
        cur.close()
        cxn.commit()
        cxn.close()

        self.closeWindow(self)
        infernal_wireless_gui_project.main()

    def closeWindow(self, event):
        self.Destroy()

    def create_std(self, e):
        isProject = False
        # ~ print isProject
        # print self.projectName
        self.closeWindow(self)
        infernal_wireless_gui_project.main()

    def returnproject(self):
        return self.projectName


def create_new_project():
    app = wx.App()
    Example(None, title='Infernal Wireless - Create A project')
    app.MainLoop()


if __name__ == '__main__':
    from Modules import infernal_wireless_gui_project

    create_new_project()
    cur.close()
    cxn.commit()
    cxn.close()
