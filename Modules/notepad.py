try:
    import wx
    from wxPython.wx import *
    import wx.html
except ImportError as error:
    # ~ raise ImportError("Detected Python3 +")
    print ''


class MyHtmlFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title)
        html = wx.html.HtmlWindow(self)
        html.SetPage(
            "blah <b>About</b>  <font color=\"red\">wxPython</font> !!!! "
            "<br>blah<font color=\"red\">blah</font>")


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        # wx.Frame.__init__(self, parent, -1, title, pos=(150, 150), size=(350, 250))
        self.flag = 0
        # Menu Bar
        self.frame_1_menubar = wx.MenuBar()
        self.SetMenuBar(self.frame_1_menubar)
        self.File = wx.Menu()
        self.New = wx.MenuItem(self.File, wx.NewId(), "&New", "", wx.ITEM_NORMAL)
        self.File.AppendItem(self.New)
        self.Save = wx.MenuItem(self.File, wx.NewId(), "Save &As", "", wx.ITEM_NORMAL)
        self.File.AppendItem(self.Save)
        self.open = wx.MenuItem(self.File, wx.NewId(), "&Open", "", wx.ITEM_NORMAL)
        self.File.AppendItem(self.open)
        self.About = wx.MenuItem(self.File, wx.NewId(), "A&bout", "", wx.ITEM_NORMAL)
        self.File.AppendItem(self.About)
        self.Exit = wx.MenuItem(self.File, wx.NewId(), "&Exit", "", wx.ITEM_NORMAL)
        self.File.AppendItem(self.Exit)
        self.frame_1_menubar.Append(self.File, "&File")
        # Menu Bar end
        # Tool Bar
        # self.frame_1_toolbar = wx.ToolBar(self, -1, style=wx.TB_HORIZONTAL|wx.TB_FLAT|wx.TB_DOCKABLE|wx.TB_3DBUTTONS|wx.TB_TEXT|wx.TB_NOICONS|wx.TB_NODIVIDER|wx.TB_NOALIGN|wx.TB_HORZ_LAYOUT|wx.TB_HORZ_TEXT)
        # self.SetToolBar(self.frame_1_toolbar)
        # Tool Bar end
        self.frame_1_statusbar = self.CreateStatusBar(1, 0)
        self.__set_properties()
        self.__do_layout()
        self.SetStatusText("Notepad ")
        self.Bind(wx.EVT_MENU, self.file_save, self.Save)
        self.Bind(wx.EVT_MENU, self.open_file, self.open)
        self.Bind(wx.EVT_MENU, self.file_new, self.New)
        self.Bind(wx.EVT_MENU, self.file_exit, self.Exit)
        self.Bind(wx.EVT_MENU, self.about, self.About)

    # end wxGlade
    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("Notepad")
        # self.frame_1_toolbar.SetToolBitmapSize((0, 0))
        # self.frame_1_toolbar.Realize()
        self.frame_1_statusbar.SetStatusWidths([-1])
        # statusbar fields
        frame_1_statusbar_fields = ["frame_1_statusbar"]
        for i in range(len(frame_1_statusbar_fields)):
            self.frame_1_statusbar.SetStatusText(frame_1_statusbar_fields[i], i)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)
        self.Layout()

    # end wxGlade
    def file_save(self, event):  # wxGlade: MyFrame.<event_handler>
        if self.flag == 1:
            dialog = wxFileDialog(None, style=wxSAVE)
            # Show the dialog and get user input
            if dialog.ShowModal() == wxID_OK:
                file_path = dialog.GetPath()
                file = open(file_path, 'w')
                file_content = self.text_ctrl_1.GetValue()
                file.write(file_content)
            else:
                print 'Nothing was selected.'
                # Destroy the dialog
                self.SetStatusText("Your file has been saved")
                dialog.Destroy()
        else:
            dlg = wxMessageDialog(self, "open a new file !!!!", "New File", wxOK | wxICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()

    def open_file(self, event):  # wxGlade: MyFrame.<event_handler>
        if self.flag == 1:
            filters = 'Text files (*.txt)|*.txt'
            dialog = wxFileDialog(None, message='Open something....', wildcard=filters, style=wxOPEN | wxMULTIPLE)
            if dialog.ShowModal() == wxID_OK:
                filename = dialog.GetPath()
                file = open(filename, 'r')
                file_content = file.read()
                self.text_ctrl_1.SetValue(file_content)
            else:
                print 'Nothing was selected.'
            dialog.Destroy()
        else:
            dlg = wxMessageDialog(self, "  open a new file !!!!", "New File", wxOK | wxICON_INFORMATION)
            dlg.ShowModal()
        # Destroy the dialog
        self.SetStatusText("Your file is opened")
        dlg.Destroy()

    def file_new(self, event):  # wxGlade: MyFrame.<event_handler>
        self.flag = 1
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.text_ctrl_1 = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_MULTILINE | wx.SUNKEN_BORDER)
        sizer_1.Add(self.text_ctrl_1, 0, wx.ALL | wx.EXPAND | wx.ALIGN_RIGHT | wx.ADJUST_MINSIZE, 0)
        self.text_ctrl_1.SetMinSize((500, 500))
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)
        self.Layout()
        self.text_ctrl_1.SetFocus()

    def file_exit(self, event):  # wxGlade: MyFrame.<event_handler>
        """Bring up a wx.MessageDialog with a quit message."""
        alert = wx.MessageDialog(self, "Do you really want to quit")
        response = alert.ShowModal()
        alert.Destroy()
        if response == wx.ID_OK:
            print "The user clicked the 'OK' button."
            self.Close()
        else:
            print "The user clicked the 'Cancel' button."
            event.Skip()

    def about(self, event):
        frm = MyHtmlFrame(None, "About ....")
        frm.Show()


# dlg = wxMessageDialog(self, "This is test implementation of Simple Notepad using wxPython !!!!",
# "New File", wxOK | wxICON_INFORMATION)
# dlg.ShowModal()
# dlg.Destroy()
# end of class MyFrame
class MyNotepad(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        frame_1 = MyFrame(None, -1, "Notepad")
        self.SetTopWindow(frame_1)
        frame_1.Show()
        return 1


# end of class MyNotepad
# ~ if __name__ == "__main__":
def openit():
    app = MyNotepad(0)
    app.MainLoop()
