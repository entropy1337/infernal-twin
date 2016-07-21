import os
import wx
import re

class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None)
        self.SetTitle('Cookie Sniffer')
        panel = wx.Panel(self)

        os.system("touch ./Modules/MiTM_data.txt")
        os.system('python ./Modules/mitm_sniffer_core.py &')

        style = wx.TE_MULTILINE | wx.TE_READONLY
        self.text = wx.TextCtrl(panel, value="", style=style, size=(850, 900))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(self.text, 0, wx.EXPAND)
        sizer.AddStretchSpacer(1)
        panel.SetSizer(sizer)
        self.on_timer()

    def on_timer(self):

        data_array = []
        host_array = []

        mData = open("./Modules/MiTM_data.txt", 'r')

        for i in mData:

            checkRegex = re.search(r'Cookie:*.*', i)

            if checkRegex:
                mCookie = checkRegex.group(0)

                data_array.append(str(mCookie))





        self.text.SetValue(str("\n\n".join(data_array)))

        wx.CallLater(2000, self.on_timer)


# ~ if __name__ == '__main__':
def startSniff():
    app = wx.App()
    frame = Frame()
    frame.Show()
    frame.SetSize((850, 600))
    app.MainLoop()
    os.system("rm ./Modules/MiTM_data.txt")
    os.system("kill  `ps aux | grep mitm_sniffer_core.py | head -1 | awk '{print $2}'`")
    os.system("kill  `ps aux | grep MiTM_sniffer.py | head -1 | awk '{print $2}'`")


# startSniff()
