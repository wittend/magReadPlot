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

# ===== Input Parameters ========================================================
# date = '2021/02/22'
# t_start = '00:00:00'
# t_stop = '23:59:59'
# station_code = 'KD0EAG'
data_dir = '/PSWS/Srawdata'
plot_dir = '/PSWS/Splot'
# ============================================================================

class TopFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: TopFrame.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.fileNotSaved = False
        self.SetSize((1000, 700))
        self.SetTitle("magReadPlot")
        self.homedir = os.environ['HOME'] + data_dir
        #self.homedir = self.homedir + '/PSWS/Srawdata/'
        
        self.config = wx.Config("magReadPlot")

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
        tool = self.topFrameToolbar.AddTool(wx.ID_ANY, "Load", wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (24, 24)), wx.NullBitmap, wx.ITEM_NORMAL, "Select and load log dataset", "Select and load log dataset")
        self.Bind(wx.EVT_TOOL, self.onLoadData, id=tool.GetId())
        tool = self.topFrameToolbar.AddTool(wx.ID_ANY, "Plot", wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE, wx.ART_TOOLBAR, (24, 24)), wx.NullBitmap, wx.ITEM_NORMAL, "Plot data as graph", "Plot data as graph")
        self.Bind(wx.EVT_TOOL, self.onPlotData, id=tool.GetId())
        tool = self.topFrameToolbar.AddTool(wx.ID_ANY, "Print", wx.ArtProvider.GetBitmap(wx.ART_PRINT, wx.ART_TOOLBAR, (24, 24)), wx.NullBitmap, wx.ITEM_NORMAL, "Print plotted data", "Print plotted data")
        self.Bind(wx.EVT_TOOL, self.onPrintPlot, id=tool.GetId())
        tool = self.topFrameToolbar.AddTool(wx.ID_ANY, "Save", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, (24, 24)), wx.NullBitmap, wx.ITEM_NORMAL, "Save plot as bitmap file", "Save plot as bitmap file")
        self.Bind(wx.EVT_TOOL, self.onSavePlot, id=tool.GetId())
        tool = self.topFrameToolbar.AddTool(wx.ID_ANY, "Clear", wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, (24, 24)), wx.NullBitmap, wx.ITEM_NORMAL, "Clear plot and processed data", "Clear plot and processed data")
        self.Bind(wx.EVT_TOOL, self.onPlotClear, id=tool.GetId())
        self.topFrameToolbar.AddSeparator()
        tool = self.topFrameToolbar.AddTool(wx.ID_ANY, "Exit", wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR, (24, 24)), wx.NullBitmap, wx.ITEM_NORMAL, "Exit this program", "Exit this program")
        self.Bind(wx.EVT_TOOL, self.onExit, id=tool.GetId())
        self.SetToolBar(self.topFrameToolbar)
        self.topFrameToolbar.Realize()
        # Tool Bar end

        self.TopSplitterWindow = wx.SplitterWindow(self, wx.ID_ANY)
        self.TopSplitterWindow.SetMinimumPaneSize(20)
        
        self.topLeftSplitterPane = wx.Panel(self.TopSplitterWindow, wx.ID_ANY)
        self.topLeftSplitterPane.SetMinSize((225, -1))
        
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        self.dirTreeCtrl = wx.GenericDirCtrl(self.topLeftSplitterPane, wx.ID_ANY, dir=self.homedir,)
        sizer_1.Add(self.dirTreeCtrl, 1, wx.EXPAND, 0)
        
        self.topRightSplitterPane = wx.Panel(self.TopSplitterWindow, wx.ID_ANY)
        # self.topRightSplitterPane = wx.Panel(self.TopSplitterWindow, wx.ID_ANY)
        
        # sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        # self.panel_1 = wx.Panel(self.topRightSplitterPane, wx.ID_ANY)
        # sizer_2.Add(self.panel_1, 1, wx.EXPAND, 0)
        
        # sizer_3 = wx.BoxSizer(wx.VERTICAL)
        # self.plotPanel = PlotPanel(self.panel_1)
        # sizer_3.Add(self.plotPanel, 1, wx.EXPAND, 0)
        
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        self.plotPanel = PlotPanel(self.topRightSplitterPane)
        sizer_3.Add(self.plotPanel, 1, wx.EXPAND, 0)
        
        #self.panel_1.SetSizer(sizer_3)
        # self.topRightSplitterPane.SetSizer(sizer_2)
        self.topRightSplitterPane.SetSizer(sizer_3)
        self.topLeftSplitterPane.SetSizer(sizer_1)
        self.TopSplitterWindow.SplitVertically(self.topLeftSplitterPane, self.topRightSplitterPane)
        self.TopSplitterWindow.SetSashPosition(225)
        self.Layout()
        self.Bind(wx.EVT_CLOSE, self.OnClose, self)
        # end wxGlade
        tree = self.dirTreeCtrl.GetTreeCtrl()
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelect, id=tree.GetId())       
        #self.plotPanel.init_plot_data()
        #self.plotPanel.plt.show()

    def OnSelect(self, event):
        """
            OnSelect()
        """
        filePath = self.dirTreeCtrl.GetPath()
        if(os.path.isdir(filePath) != True):
            print('self.dirTreeCtrl.GetPath(): ' + self.dirTreeCtrl.GetPath())
            #self.plotPanel.plt.close()
            #self.plotPanel.plt.clf()
            #self.plotPanel.plt.cla()
            self.plotPanel.readData(self.dirTreeCtrl.GetPath())
            self.plotPanel.draw()
            # self.plotPanel.plt.show()
              #self.plotPanel.fit()
            # self.plotPanel.plt.show()
        # else:
        #     print('Not a file: ' + self.dirTreeCtrl.GetPath())
            
    def onFileOpen(self, event):  # wxGlade: TopFrame.<event_handler>
        print("Event handler 'onFileOpen' not implemented!")
        event.Skip()

    def onFileExit(self, event):  # wxGlade: TopFrame.<event_handler>
        #print("Event handler 'onFileExit' not implemented!")
        self.OnClose(event)
 #       event.Skip()

    def onHelpAbout(self, event):  # wxGlade: TopFrame.<event_handler>
        print("Event handler 'onHelpAbout' not implemented!")
        event.Skip()

    def onLoadData(self, event):  # wxGlade: TopFrame.<event_handler>
        #print("Event handler 'onLoadData' not implemented!")
        self.plotPanel.OnWhiz(event)
        #event.Skip()

    def onPlotData(self, event):  # wxGlade: TopFrame.<event_handler>
        print("Event handler 'onPlotData' not implemented!")
        event.Skip()

    def onPrintPlot(self, event):  # wxGlade: TopFrame.<event_handler>
        print("Event handler 'onPrintPlot' not implemented!")
        event.Skip()

    def onSavePlot(self, event):  # wxGlade: TopFrame.<event_handler>
        print("Event handler 'onSavePlot' not implemented!")
        event.Skip()

    def onPlotClear(self, event):  # wxGlade: TopFrame.<event_handler>
        print("Event handler 'onPlotClear' not implemented!")
        event.Skip()

    def onExit(self, event):  # wxGlade: TopFrame.<event_handler>
        #print("Event handler 'onExit' not implemented!")
        self.OnClose(event)
        #event.Skip()

    def OnClose(self, event):
        # if event.CanVeto() and self.fileNotSaved:
        #     if wx.MessageBox("The file has not been saved... continue closing?", "Please confirm", wx.ICON_QUESTION | wx.YES_NO) != wx.YES:
        #         event.Veto()
        #         return
        # self.config.Write("WindowTop", 0)
        # self.config.Write("WindowLeft", 10)
        # self.config.Write("WindowHeight", 100)
        # self.config.Write("WindowWidth", 100)
        self.Destroy()  # you may also do:  event.Skip()
                        # since the default event handler does call Destroy(), too# end of class TopFrame

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
