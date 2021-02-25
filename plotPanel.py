#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#============================================================================================
# RM3100_MagReadPlot.py
# 
# This routine reads ascii file data from HamSCI DASI magnetometers (RM3100) and plot graphs. 
# 
# Hyomin Kim, New Jersey Institute of Technology, hmkim@njit.edu 
# 02/01/2021
#============================================================================================
import sys
import csv
import wx
import numpy as np
import datetime
from datetime import date
import bisect

# from moving_average import *

from matplotlib.backends.backend_wxagg import (FigureCanvasWxAgg as FigureCanvas, NavigationToolbar2WxAgg as NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib.pyplot as plot
from matplotlib import ticker
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import matplotlib.dates as mdate

ERR_TOL = 1e-5  # floating point slop for peak-detection

# ===== Input Parameters ========================================================
date = '2021/01/16'
t_start = '00:00:00'
t_stop = '23:59:59'
station_code = 'KD0EAG'
# data_dir = '/PSWS/Srawdata'
# plot_dir = '/PSWS/Splot'
# ============================================================================

#------------------------------------------------------------------------------
#  PlotPanel Class
#------------------------------------------------------------------------------
class PlotPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.createPlot()
        self.Fit()

    def createPlot(self):
        self.fgm_data       = []
        self.year           = date[0:4]
        self.month          = date[5:7]
        self.day            = date[8:10]
        self.hour_start     = t_start[0:2]
        self.minute_start   = t_start[3:5]
        self.second_start   = t_start[6:8]
        self.hour_stop      = t_stop[0:2]
        self.minute_stop    = t_stop[3:5]
        self.second_stop    = t_stop[6:8]
        self.date_time      = datetime.datetime(int(self.year), int(self.month), int(self.day), int(self.hour_start), int(self.minute_start), int(self.second_start))
        self.doy            = self.date_time.timetuple().tm_yday

        self.plt = plot
        self.fig = self.plt.figure(1, figsize=(5, 4))       # Plot window size
        self.canvas = FigureCanvas(self, -1, self.fig)
        self.toolbar = NavigationToolbar(self.canvas)       # matplotlib toolbar
        self.toolbar.Realize()

        # Now put all into a sizer
        # sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        # This way of adding to sizer allows resizing
        # sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        # Best to allow the toolbar to resize!
        # sizer.Add(self.toolbar, 0, wx.GROW)
        self.sizer.Add(self.toolbar, 0, wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()
        # self.plt.show()
        # self.resize_event()

    #--------------------------------------------------
    #  readData()
    #--------------------------------------------------
    def readData(self, fileName):
        # filename = station_code + '-' + year+month+day + '-runmag.log'
        # f=open(data_dir+filename)
        self.f = open(fileName)
        self.header_index = 0
        self.csv_f = csv.reader(self.f, delimiter=",")
        # self.fgm_data = []
        for row in self.csv_f:
            self.fgm_data.append(row)
        self.date_time_array = np.array([self.year+'-'+self.month+'-'+self.day + ' ' + self.fgm_data[i][0][19:27] for i in range(self.header_index, len(self.fgm_data))])
        self.pattern = '%Y-%m-%d %H:%M:%S'
        self.epoch_temp = np.array([datetime.datetime.strptime(x, self.pattern) for x in self.date_time_array])
        self.Bx_temp = np.array([float(self.fgm_data[i][3][4:11]) for i in range(self.header_index, len(self.fgm_data))])
        self.By_temp = np.array([float(self.fgm_data[i][4][4:11]) for i in range(self.header_index, len(self.fgm_data))])
        self.Bz_temp = np.array([float(self.fgm_data[i][5][4:11]) for i in range(self.header_index, len(self.fgm_data))])
        #Array slicing/indexing
        self.start = datetime.datetime(int(self.year), int(self.month), int(self.day), int(self.hour_start), int(self.minute_start), int(self.second_start))
        self.stop = datetime.datetime(int(self.year), int(self.month), int(self.day), int(self.hour_stop), int(self.minute_stop), int(self.second_stop))
        self.start_index = bisect.bisect_left(self.epoch_temp, self.start)
        self.stop_index = bisect.bisect_left(self.epoch_temp, self.stop)
        self.Epoch = self.epoch_temp[self.start_index : self.stop_index]
        self.Bx = 1000*self.Bx_temp[self.start_index : self.stop_index]  #*1000: uT to nT
        self.By = 1000*self.By_temp[self.start_index : self.stop_index]
        self.Bz = 1000*self.Bz_temp[self.start_index : self.stop_index]
               
        # Specify date_str/time range for x-axis range
        self.ep_start = datetime.datetime(int(self.year), int(self.month), int(self.day), int(self.hour_start), int(self.minute_start), int(self.second_start))
        self.ep_stop = datetime.datetime(int(self.year), int(self.month), int(self.day), int(self.hour_stop), int(self.minute_stop), int(self.second_stop))
        
        #This is for Pi magnetometer (PNI)
        self.Bx[np.where(self.Bx[:] >= 999999.0)] = np.nan
        self.By[np.where(self.By[:] >= 999999.0)] = np.nan
        self.Bz[np.where(self.Bz[:] >= 999999.0)] = np.nan
        
        #Moving average
        self.N = 10 #WindowWidth in sec
        self.Bx = np.array(moving_average(self.Bx, self.N))
        self.By = np.array(moving_average(self.By, self.N))
        self.Bz = np.array(moving_average(self.Bz, self.N))
        self.Epoch = np.array(self.Epoch[0:len(self.Bx)])  #to match the new array size with the moving averaged array. 
        self.Bt = np.sqrt(self.Bx**2 + self.By**2 + self.Bz**2)

        # Subplot 1
        self.ax1 = self.fig.add_subplot(411)
        self.box = self.ax1.get_position()
        self.plt.subplots_adjust(left=self.box.x0, right=self.box.x1-0.08, top=self.box.y1, bottom=0.1, hspace=0.1)
        
        self.ax1.plot(self.Epoch, self.Bx, label='Bx', linewidth=0.5)
        self.title = station_code + ' HamSCI Mag '  + date + ' ' + t_start + ' - ' + t_stop
        self.ax1.set_title(self.title)
        
        self.ax1.set_xlim([self.ep_start, self.ep_stop])    #without this, the time range will not show up properly because there are missing data.
        self.ax1.set_ylabel('Bx (nT)')
        self.ax1.get_xaxis().set_ticklabels([])
        self.ax1.tick_params(axis='x', direction='out', top='on')
        self.ax1.tick_params(axis='y', direction='out', right='on')
        self.ax1.minorticks_on()
        self.ax1.tick_params(axis='x', which ='minor', direction='out', top='on')
        self.ax1.tick_params(axis='y', which ='minor', direction='out', right='on')
        self.ax1.set_ylim(47600, 47800)
        self.ax1.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        
        # Subplot 2
        self.ax2 = self.fig.add_subplot(412)
        self.ax2.plot(self.Epoch, self.By, label='By', linewidth=0.5)

        self.ax2.set_xlim([self.ep_start, self.ep_stop])     #without this, the time range will not show up properly because there are missing data.       
        self.ax2.set_ylabel('By (nT)')
        self.ax2.get_xaxis().set_ticklabels([])
        self.ax2.tick_params(axis='x', direction='out', top='on')
        self.ax2.tick_params(axis='y', direction='out', right='on')
        self.ax2.minorticks_on()
        self.ax2.tick_params(axis='x', which ='minor', direction='out', top='on')
        self.ax2.tick_params(axis='y', which ='minor', direction='out', right='on')
        self.ax2.set_ylim(-100, 100)
        self.ax2.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        
        # Subplot 3
        self.ax3 = self.fig.add_subplot(413)
        self.ax3.plot(self.Epoch, self.Bz, label='Bz', linewidth=0.5)

        self.ax3.set_xlim([self.ep_start, self.ep_stop])     #without this, the time range will not show up properly because there are missing data.
        self.ax3.set_ylabel('Bz (nT)')
        self.ax3.get_xaxis().set_ticklabels([])
        self.ax3.tick_params(axis='x', direction='out', top='on')
        self.ax3.tick_params(axis='y', direction='out', right='on')
        self.ax3.minorticks_on()
        self.ax3.tick_params(axis='x', which ='minor', direction='out', top='on')
        self.ax3.tick_params(axis='y', which ='minor', direction='out', right='on')
        self.ax3.set_ylim(-15400, -15200)
        self.ax3.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        
        # Subplot 4
        self.ax4 = self.fig.add_subplot(414)
        self.ax4.plot(self.Epoch, self.Bt, label='Bt', linewidth=0.5)
        self.ax4.set_xlim([self.ep_start, self.ep_stop])     #without this, the time range will not show up properly because there are missing data.
        self.ax4.set_ylabel('Bt (nT)')
        self.ax4.get_xaxis().set_ticklabels([])
        self.ax4.tick_params(axis='x', direction='out', top='on')
        self.ax4.tick_params(axis='y', direction='out', right='on')
        self.ax4.minorticks_on()
        self.ax4.tick_params(axis='x', which ='minor', direction='out', top='on')
        self.ax4.tick_params(axis='y', which ='minor', direction='out', right='on')
        self.ax4.set_ylim(50000, 50200)
        self.ax4.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
       
        # X-axis
        self.ax4.set_xlabel('UT (hh:mm)')
        self.date_fmt = '%H:%M'  #'%d-%m-%y %H:%M:%S'  #Choose your xtick format string
        self.date_formatter = mdate.DateFormatter(self.date_fmt)
        self.ax4.xaxis.set_major_formatter(self.date_formatter)

        self.toolbar.update()       # Not sure why this is needed - ADS

        
    #--------------------------------------------------
    #  resetPlot()
    #--------------------------------------------------
    def resetPlot(self):
        self.plt.close()
        self.plt = None
        self.createPlot()
        self.Fit()

    #--------------------------------------------------
    #  OnSavePlot()
    #--------------------------------------------------
    def OnSavePlot(self, event):
        t_start_str = t_start[0:2] + t_start[3:5]
        t_stop_str = t_stop[0:2] + t_stop[3:5]
        filename_plot = station_code + '_' + year+month+day + '_' + t_start_str + '_' + t_stop_str + '_MovingAve.jpg'
        plt.savefig(plot_dir + filename_plot, format='jpg', bbox_inches='tight', dpi=600)
        plt.close()

    #--------------------------------------------------
    #  GetToolBar()
    #--------------------------------------------------
    def GetToolBar(self):
        # You will need to override GetToolBar if you are using an
        # unmanaged toolbar in your frame
        return self.toolbar

    #--------------------------------------------------
    #  onEraseBackground()
    #--------------------------------------------------
    def onEraseBackground(self, evt):
        # this is supposed to prevent redraw flicker on some X servers...
        pass

#------------------------------------------------------------------------------
# Perform moving average
# Hyomin Kim 7/10/2020
# Source:
#   https://stackoverflow.com/questions/13728392/moving-average-or-running-mean
#------------------------------------------------------------------------------
def moving_average(data, windowsize):
    cumsum, moving_aves = [0], []
    for i, x in enumerate(data, 1):
        cumsum.append(cumsum[i-1] + x)
        if i>=windowsize:
            moving_ave = (cumsum[i] - cumsum[i-windowsize])/windowsize
            moving_aves.append(moving_ave)
    return moving_aves
