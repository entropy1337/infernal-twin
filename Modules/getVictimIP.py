#!/usr/bin/env python2.7
import os
import wx


class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None)
        self.SetTitle('Client IP and Browser')
        panel = wx.Panel(self)

        open('./Modules/Logs/sniffer/connected_clients.txt', 'w').close()
        os.system('python ./Modules/victim_ip_browser.py &')

        style = wx.TE_MULTILINE | wx.TE_READONLY
        self.text = wx.TextCtrl(panel, value="", style=style, size=(850, 900))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(self.text, 0, wx.EXPAND)
        sizer.AddStretchSpacer(1)
        panel.SetSizer(sizer)
        self.on_timer()

    def on_timer(self):
        with open('./Modules/Logs/sniffer/connected_clients.txt', 'r') as fhandle:
            client_list = fhandle.read()

        self.text.SetValue(str(client_list))
        wx.CallLater(2000, self.on_timer)


def startSniff():
    app = wx.App()
    frame = Frame()
    frame.Show()
    frame.SetSize((850, 600))
    app.MainLoop()
    os.system("kill  `ps aux | grep victim_ip_browser.py | head -1 | awk '{print $2}'`")
    os.system("kill  `ps aux | mitm_sniffer_core.py | head -1 | awk '{print $2}'`")
    os.system("kill  `ps aux | grep MiTM_sniffer.py | head -1 | awk '{print $2}'`")

    os.system("rm ./Modules/Logs/sniffer/connected_clients.txt")
