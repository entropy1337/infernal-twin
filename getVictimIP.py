#!/usr/bin/env python2.7
import random
import wx
import os

class Frame(wx.Frame):

    def __init__(self):
        super(Frame, self).__init__(None)
        self.SetTitle('Client IP and Browser')
        panel = wx.Panel(self)

        open('./connected_clients.txt', 'w').close()
        os.system('python victim_ip_browser.py &')

        style = wx.TE_MULTILINE|wx.TE_READONLY
        self.text = wx.TextCtrl(panel, value="", style=style, size=(850, 900))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(self.text, 0, wx.EXPAND)
        sizer.AddStretchSpacer(1)
        panel.SetSizer(sizer)
        self.on_timer()

    def on_timer(self):
        with open('./connected_clients.txt', 'r') as fhandle:
            client_lis = fhandle.read()

        self.text.SetValue(str(client_list))
        wx.CallLater(2000, self.on_timer)


def startSniff():
    app = wx.App()
    frame = Frame()
    frame.Show()
    frame.SetSize((850,600))
    app.MainLoop()
    os.system("kill  `ps aux | grep victim_ip_browser.py | head -1 | awk '{print $2}'`")
