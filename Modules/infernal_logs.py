#!/usr/bin/env python2.7
import os
import wx

import MySQLdb
# import threading

import db_connect_creds

# import db_setup




class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None)
        self.SetTitle('Infenral wireless Logs')



        panel = wx.Panel(self)

        # panel = wx.lib.scrolledpanel.ScrolledPanel(self, -1, size=(1110, 1400), pos=(0, 28))  # wx.Panel(self)
        # panel.SetBackgroundColour('#98a3b2')
        # panel.SetupScrolling()



        style = wx.TE_MULTILINE | wx.TE_READONLY
        self.text = wx.TextCtrl(panel, value="", style=style, size=(450, 600))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(self.text, 0, wx.EXPAND)
        sizer.AddStretchSpacer(1)
        panel.SetSizer(sizer)
        self.on_timer()

    def on_timer(self):
        WPA_CRACK_DB = 'wpa_crack'
        username, password = db_connect_creds.read_creds()
        db_connection = MySQLdb.connect(host='localhost', user=username,
                                        passwd=password)
        cursor = db_connection.cursor()
        # db_setup.create_db(cursor, WPA_CRACK_DB, username, password)
        cursor.execute('USE %s' % WPA_CRACK_DB)
        cursor.execute('''SELECT * from content;''')
        data = cursor.fetchall()

        # print 'executing log 2 '

        tmpArray = []

        for row in data:
            if row[0] != '' or row[1] != '':
                tmpArray.append(row[0] + ' : ' + row[1])

            #     with open('./Modules/connected_clients.txt', 'r') as fhandle:
            # client_list = fhandle.read()
        array_to_string = "\n\n".join(tmpArray)

        self.text.SetValue(str(array_to_string))
        wx.CallLater(5000, self.on_timer)


def checkLog():
    app = wx.App()
    frame = Frame()
    frame.Show()
    frame.SetSize((450, 600))
    app.MainLoop()