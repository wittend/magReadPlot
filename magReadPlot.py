#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#============================================================================================
# magReadPlot.py
# 
# This routine reads ascii file data from HamSCI DASI magnetometers (RM3100) and plot graphs. 
# 
# Hyomin Kim, New Jersey Institute of Technology, hmkim@njit.edu 
# 02/01/2021
#============================================================================================
import wx

# begin wxGlade: extracode
import os
import sys
from pathlib import Path
from plotPanel import *
# end wxGlade

class TopFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: TopFrame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((1000, 750))
        self.SetTitle("magReadPlot")

        # Menu Bar
        self.topFrameMenubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Open", "Open a Logfile")
        self.Bind(wx.EVT_MENU, self.onFileOpen, item)
        wxglade_tmp_menu.AppendSeparator()
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Exit", "Exit this program")
        self.Bind(wx.EVT_MENU, self.onFileExit, item)
        self.topFrameMenubar.Append(wxglade_tmp_menu, "File")
        wxglade_tmp_menu = wx.Menu()
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "About", "Information about the program")
        self.Bind(wx.EVT_MENU, self.onHelpAbout, item)
        self.topFrameMenubar.Append(wxglade_tmp_menu, "Help")
        self.SetMenuBar(self.topFrameMenubar)
        # Menu Bar end

        # Tool Bar
        self.topFrameToolbar = wx.ToolBar(self, -1)
        self.SetToolBar(self.topFrameToolbar)
        self.topFrameToolbar.Realize()
        # Tool Bar end

        self.TopSplitterWindow = wx.SplitterWindow(self, wx.ID_ANY)
        self.TopSplitterWindow.SetMinimumPaneSize(20)

        self.topLeftSplitterPane = wx.Panel(self.TopSplitterWindow, wx.ID_ANY)
        self.topLeftSplitterPane.SetMinSize((275, -1))

        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)

        self.dirTreeCtrl = wx.GenericDirCtrl(self.topLeftSplitterPane, wx.ID_ANY)
        sizer_1.Add(self.dirTreeCtrl, 1, wx.EXPAND, 0)

        self.topRightSplitterPane = wx.Panel(self.TopSplitterWindow, wx.ID_ANY)

        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)

        self.panel_1 = wx.Panel(self.topRightSplitterPane, wx.ID_ANY)
        sizer_2.Add(self.panel_1, 1, wx.EXPAND, 0)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)

        #self.plotPanel = PlotPanel(self.panel_1, wx.ID_ANY)
        self.plotPanel = PlotPanel(self.panel_1)
        sizer_3.Add(self.plotPanel, 1, wx.EXPAND, 0)

        self.panel_1.SetSizer(sizer_3)

        self.topRightSplitterPane.SetSizer(sizer_2)

        self.topLeftSplitterPane.SetSizer(sizer_1)

        self.TopSplitterWindow.SplitVertically(self.topLeftSplitterPane, self.topRightSplitterPane)

        self.Layout()

        # end wxGlade

    def onFileOpen(self, event):  # wxGlade: TopFrame.<event_handler>
        print("Event handler 'onFileOpen' not implemented!")
        event.Skip()
    def onFileExit(self, event):  # wxGlade: TopFrame.<event_handler>
        print("Event handler 'onFileExit' not implemented!")
        event.Skip()
    def onHelpAbout(self, event):  # wxGlade: TopFrame.<event_handler>
        print("Event handler 'onHelpAbout' not implemented!")
        event.Skip()
# end of class TopFrame

class TheApp(wx.App):
    def OnInit(self):
        self.topFrame = TopFrame(None, wx.ID_ANY)
        self.SetTopWindow(self.topFrame)
        self.topFrame.Show()
        return True

# end of class wx.App

if __name__ == "__main__":
    magReadPlot = TheApp(0)
    magReadPlot.MainLoop()
