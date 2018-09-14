#!/usr/bin/env python2.7
import os
import wx


class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None)
        self.SetTitle('Pop Up Proxy Logs')
        panel = wx.Panel(self)

        open('/var/www/html/creds.log', 'w').close()
        # os.system('python ./Modules/victim_ip_browser.py &')

        style = wx.TE_MULTILINE | wx.TE_READONLY
        self.text = wx.TextCtrl(panel, value="", style=style, size=(850, 900))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(self.text, 0, wx.EXPAND)
        sizer.AddStretchSpacer(1)
        panel.SetSizer(sizer)
        self.on_timer()

    def on_timer(self):
        with open('/var/www/html/creds.log', 'r') as fhandle:
            client_list = fhandle.read()

        self.text.SetValue(str(client_list))
        wx.CallLater(2000, self.on_timer)


def popLog():
    app = wx.App()
    frame = Frame()
    frame.Show()
    frame.SetSize((850, 600))
    app.MainLoop()

