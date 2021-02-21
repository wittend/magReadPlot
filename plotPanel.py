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
import matplotlib.cm as cm
import matplotlib.cbook as cbook
from matplotlib.backends.backend_wxagg import (FigureCanvasWxAgg as FigureCanvas, NavigationToolbar2WxAgg as NavigationToolbar)
#from matplotlib.figure import Figure
#import numpy as np

import wx
import wx.xrc as xrc

from matplotlib.pylab import *
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
import matplotlib.dates as mdate
import sys
from datetime import date
import datetime
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from moving_average import *
import csv
import bisect
#from Ground_FGM_Subroutines import *
#from DataRead_Kim import generate_datestrings
#import matplotlib.pyplot as plt
ERR_TOL = 1e-5  # floating point slop for peak-detection


# ===== Input Parameters ========================================================
date = '2021/01/16'
t_start = '00:00:00'
t_stop = '23:59:59'
station_code = 'YOUR STATION CODE'
data_dir = 'YOUR DIRECTORY WHERE DATA FILES ARE LOCATED'
plot_dir = 'YOUR DIRECTORY WHERE GENERATED PLOTS WILL BE SAVED'
# ============================================================================

class PlotPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        self.fig = Figure((5, 4), 75)
        self.canvas = FigureCanvas(self, -1, self.fig)
        self.toolbar = NavigationToolbar(self.canvas)  # matplotlib toolbar
        self.toolbar.Realize()

        # Now put all into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # This way of adding to sizer allows resizing
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        # Best to allow the toolbar to resize!
        sizer.Add(self.toolbar, 0, wx.GROW)
        self.SetSizer(sizer)
        self.Fit()

    def init_plot_data(self):
        self.ax             = self.fig.add_subplot(111)
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

        # x = np.arange(120.0) * 2 * np.pi / 60.0
        # y = np.arange(100.0) * 2 * np.pi / 50.0
        # self.x, self.y = np.meshgrid(x, y)
        # z = np.sin(self.x) + np.cos(self.y)
        # self.im = ax.imshow(z, cmap=cm.RdBu, origin='lower')
        # 
        # zmax = np.max(z) - ERR_TOL
        # ymax_i, xmax_i = np.nonzero(z >= zmax)
        # if self.im.origin == 'upper':
        #     ymax_i = z.shape[0] - ymax_i
        # self.lines = ax.plot(xmax_i, ymax_i, 'ko')

        self.toolbar.update()  # Not sure why this is needed - ADS

    def readData(self, fileName):
        # filename = station_code + '-' + year+month+day + '-runmag.log'
        # f=open(data_dir+filename)
        f = open(fileName)
        header_index = 0
        csv_f = csv.reader(f, delimiter=",")
        self.fgm_data = []
        for row in csv_f:
            self.fgm_data.append(row)
        self.date_time_array = np.array([self.year+'-'+self.month+'-'+self.day + ' ' + self.fgm_data[i][0][19:27] for i in range(header_index, len(self.fgm_data))])
        self.pattern = '%Y-%m-%d %H:%M:%S'
        self.epoch_temp = np.array([datetime.datetime.strptime(x, self.pattern) for x in self.date_time_array])
        self.Bx_temp = np.array([float(self.fgm_data[i][3][4:11]) for i in range(header_index, len(self.fgm_data))])
        self.By_temp = np.array([float(self.fgm_data[i][4][4:11]) for i in range(header_index, len(self.fgm_data))])
        self.Bz_temp = np.array([float(self.fgm_data[i][5][4:11]) for i in range(header_index, len(self.fgm_data))])
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
        
        # Plot graph
        fig = plt.figure(1, figsize=(6, 8))  #Plot window size
                       
        # Graph 1
        ax1 = fig.add_subplot(411)
        box = ax1.get_position()
        plt.subplots_adjust(left=box.x0, right=box.x1-0.08, top=box.y1, bottom=0.1, hspace=0.1)
        ax1.plot(self.Epoch, self.Bx, label='Bx', linewidth=0.5)
        ax1.set_xlim([self.ep_start, self.ep_stop]) #without this, the time range will not show up properly because there are missing data.
        title = station_code + ' HamSCI Mag '  + date + ' ' + t_start + ' - ' + t_stop
        ax1.set_title(title)
        ax1.set_ylabel('Bx (nT)')
        ax1.get_xaxis().set_ticklabels([])
        ax1.tick_params(axis='x', direction='out', top='on')
        ax1.tick_params(axis='y', direction='out', right='on')
        ax1.minorticks_on()
        ax1.tick_params(axis='x', which ='minor', direction='out', top='on')
        ax1.tick_params(axis='y', which ='minor', direction='out', right='on')
        ax1.set_ylim(47600, 47800)
        ax1.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        
        ax2 = fig.add_subplot(412)
        ax2.plot(self.Epoch, self.By, label='By', linewidth=0.5)
        ax2.set_xlim([self.ep_start, self.ep_stop]) #without this, the time range will not show up properly because there are missing data.
        ax2.set_ylabel('By (nT)')
        ax2.get_xaxis().set_ticklabels([])
        ax2.tick_params(axis='x', direction='out', top='on')
        ax2.tick_params(axis='y', direction='out', right='on')
        ax2.minorticks_on()
        ax2.tick_params(axis='x', which ='minor', direction='out', top='on')
        ax2.tick_params(axis='y', which ='minor', direction='out', right='on')
        ax2.set_ylim(-100, 100)
        ax2.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        
        ax3 = fig.add_subplot(413)
        ax3.plot(self.Epoch, self.Bz, label='Bz', linewidth=0.5)
        ax3.set_xlim([self.ep_start, self.ep_stop]) #without this, the time range will not show up properly because there are missing data.
        ax3.set_ylabel('Bz (nT)')
        ax3.get_xaxis().set_ticklabels([])
        ax3.tick_params(axis='x', direction='out', top='on')
        ax3.tick_params(axis='y', direction='out', right='on')
        ax3.minorticks_on()
        ax3.tick_params(axis='x', which ='minor', direction='out', top='on')
        ax3.tick_params(axis='y', which ='minor', direction='out', right='on')
        ax3.set_ylim(-15400, -15200)
        ax3.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        
        ax4 = fig.add_subplot(414)
        ax4.plot(self.Epoch, self.Bt, label='Bt', linewidth=0.5)
        ax4.set_xlim([self.ep_start, self.ep_stop]) #without this, the time range will not show up properly because there are missing data.
        ax4.set_ylabel('Bt (nT)')
        ax4.get_xaxis().set_ticklabels([])
        ax4.tick_params(axis='x', direction='out', top='on')
        ax4.tick_params(axis='y', direction='out', right='on')
        ax4.minorticks_on()
        ax4.tick_params(axis='x', which ='minor', direction='out', top='on')
        ax4.tick_params(axis='y', which ='minor', direction='out', right='on')
        ax4.set_ylim(50000, 50200)
        ax4.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
       
        # X-axis
        ax4.set_xlabel('UT (hh:mm)')
        date_fmt = '%H:%M'  #'%d-%m-%y %H:%M:%S'  #Choose your xtick format string
        date_formatter = mdate.DateFormatter(date_fmt)
        ax4.xaxis.set_major_formatter(date_formatter)

    def GetToolBar(self):
        # You will need to override GetToolBar if you are using an
        # unmanaged toolbar in your frame
        return self.toolbar

    def onEraseBackground(self, evt):
        # this is supposed to prevent redraw flicker on some X servers...
        pass

    def draw_graph(self, y_money, x_date):
        year = date[0:4]
        month = date[5:7]
        day = date[8:10]
        hour_start = t_start[0:2]
        minute_start = t_start[3:5]
        second_start = t_start[6:8]
        hour_stop = t_stop[0:2]
        minute_stop = t_stop[3:5]
        second_stop = t_stop[6:8]
        date_time = datetime.datetime(int(year), int(month), int(day), int(hour_start), int(minute_start), int(second_start))
        doy = date_time.timetuple().tm_yday
        filename = station_code + '-' + year+month+day + '-runmag.log'
        f=open(data_dir+filename)
        header_index = 0
        csv_f = csv.reader(f, delimiter=",")
        fgm_data = []
        for row in csv_f:
            fgm_data.append(row)
        date_time_array = np.array([year+'-'+month+'-'+day + ' ' + fgm_data[i][0][19:27] for i in range(header_index, len(fgm_data))])
        pattern = '%Y-%m-%d %H:%M:%S'
        epoch_temp = np.array([datetime.datetime.strptime(x, pattern) for x in date_time_array])
        Bx_temp = np.array([float(fgm_data[i][3][4:11]) for i in range(header_index, len(fgm_data))])
        By_temp = np.array([float(fgm_data[i][4][4:11]) for i in range(header_index, len(fgm_data))])
        Bz_temp = np.array([float(fgm_data[i][5][4:11]) for i in range(header_index, len(fgm_data))])
        #Array slicing/indexing
        start = datetime.datetime(int(year), int(month), int(day), int(hour_start), int(minute_start), int(second_start))
        stop = datetime.datetime(int(year), int(month), int(day), int(hour_stop), int(minute_stop), int(second_stop))
        start_index = bisect.bisect_left(epoch_temp, start)
        stop_index = bisect.bisect_left(epoch_temp, stop)
        Epoch = epoch_temp[start_index:stop_index]
        Bx = 1000*Bx_temp[start_index:stop_index]  #*1000: uT to nT
        By = 1000*By_temp[start_index:stop_index]
        Bz = 1000*Bz_temp[start_index:stop_index]
        
        
        # Specify date_str/time range for x-axis range
        ep_start = datetime.datetime(int(year), int(month), int(day), int(hour_start), int(minute_start), int(second_start))
        ep_stop = datetime.datetime(int(year), int(month), int(day), int(hour_stop), int(minute_stop), int(second_stop))
        
        
        #This is for Pi magnetometer (PNI)
        Bx[np.where(Bx[:] >= 999999.0)] = np.nan
        By[np.where(By[:] >= 999999.0)] = np.nan
        Bz[np.where(Bz[:] >= 999999.0)] = np.nan
        
        
        #Moving average
        N = 10 #WindowWidth in sec
        Bx = np.array(moving_average(Bx, N))
        By = np.array(moving_average(By, N))
        Bz = np.array(moving_average(Bz, N))
        Epoch = np.array(Epoch[0:len(Bx)])  #to match the new array size with the moving averaged array. 
        Bt = np.sqrt(Bx**2+By**2+Bz**2)
        
        
        # Plot graph
        fig = plt.figure(1, figsize=(6, 8))  #Plot window size
                       
        # Graph 1
        ax1 = fig.add_subplot(411)
        box = ax1.get_position()
        plt.subplots_adjust(left=box.x0, right=box.x1-0.08, top=box.y1, bottom=0.1, hspace=0.1)
        ax1.plot(Epoch, Bx, label='Bx', linewidth=0.5)
        ax1.set_xlim([ep_start, ep_stop]) #without this, the time range will not show up properly because there are missing data.
        title = station_code + ' HamSCI Mag '  + date + ' ' + t_start + ' - ' + t_stop
        ax1.set_title(title)
        ax1.set_ylabel('Bx (nT)')
        ax1.get_xaxis().set_ticklabels([])
        ax1.tick_params(axis='x', direction='out', top='on')
        ax1.tick_params(axis='y', direction='out', right='on')
        ax1.minorticks_on()
        ax1.tick_params(axis='x', which ='minor', direction='out', top='on')
        ax1.tick_params(axis='y', which ='minor', direction='out', right='on')
        ax1.set_ylim(47600, 47800)
        ax1.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        
        ax2 = fig.add_subplot(412)
        ax2.plot(Epoch, By, label='By', linewidth=0.5)
        ax2.set_xlim([ep_start, ep_stop]) #without this, the time range will not show up properly because there are missing data.
        ax2.set_ylabel('By (nT)')
        ax2.get_xaxis().set_ticklabels([])
        ax2.tick_params(axis='x', direction='out', top='on')
        ax2.tick_params(axis='y', direction='out', right='on')
        ax2.minorticks_on()
        ax2.tick_params(axis='x', which ='minor', direction='out', top='on')
        ax2.tick_params(axis='y', which ='minor', direction='out', right='on')
        ax2.set_ylim(-100, 100)
        ax2.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        
        ax3 = fig.add_subplot(413)
        ax3.plot(Epoch, Bz, label='Bz', linewidth=0.5)
        ax3.set_xlim([ep_start, ep_stop]) #without this, the time range will not show up properly because there are missing data.
        ax3.set_ylabel('Bz (nT)')
        ax3.get_xaxis().set_ticklabels([])
        ax3.tick_params(axis='x', direction='out', top='on')
        ax3.tick_params(axis='y', direction='out', right='on')
        ax3.minorticks_on()
        ax3.tick_params(axis='x', which ='minor', direction='out', top='on')
        ax3.tick_params(axis='y', which ='minor', direction='out', right='on')
        ax3.set_ylim(-15400, -15200)
        ax3.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        
        ax4 = fig.add_subplot(414)
        ax4.plot(Epoch, Bt, label='Bt', linewidth=0.5)
        ax4.set_xlim([ep_start, ep_stop]) #without this, the time range will not show up properly because there are missing data.
        ax4.set_ylabel('Bt (nT)')
        ax4.get_xaxis().set_ticklabels([])
        ax4.tick_params(axis='x', direction='out', top='on')
        ax4.tick_params(axis='y', direction='out', right='on')
        ax4.minorticks_on()
        ax4.tick_params(axis='x', which ='minor', direction='out', top='on')
        ax4.tick_params(axis='y', which ='minor', direction='out', right='on')
        ax4.set_ylim(50000, 50200)
        ax4.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        
           
        # X-axis
        ax4.set_xlabel('UT (hh:mm)')
        date_fmt = '%H:%M'  #'%d-%m-%y %H:%M:%S'  #Choose your xtick format string
        date_formatter = mdate.DateFormatter(date_fmt)
        ax4.xaxis.set_major_formatter(date_formatter)
         
        
        # ====== Save figure
        t_start_str = t_start[0:2] + t_start[3:5]
        t_stop_str = t_stop[0:2] + t_stop[3:5]
        filename_plot = station_code + '_' + year+month+day + '_' + t_start_str + '_' + t_stop_str + '_MovingAve.jpg'
        plt.savefig(plot_dir + filename_plot, format='jpg', bbox_inches='tight', dpi=600)
        plt.close()


# def moving_average(data,window):
#     """The partitions begin with window-1 None. Then follow partial lists, containing
#        window-sized elements. We do this only up to len(data)-window+1 as the following
#        partitions would have less then window elements."""
#     # parts = [None] * (window-1) + [ data[i : i + window] for i in range(len(data) - window + 1)]
#     # #       The None's           The sliding window of window elements
#     # # we return None if the value is None else we calc the avg
#     # return [ sum(x) / window if x else None for x in parts]
#     
#     parts = [None] * (window - 1) + [ data[i : i + window] for i in range(len(data) - window + 1)]
#     #       The None's           The sliding window of window elements
#     # we return None if the value is None else we calc the avg
#     return [ sum(x) / window if x else None for x in parts]
# 
