import os, struct, datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import scipy as sp
from scipy.optimize import curve_fit,minimize

def filescan(filename):
    """
    Scans the file and extracts the names and details of the different surveys in the file
    Arguments:
        filename - cg5 file
    """
    
    surveys={'name':[],'operator':[],'date':[],'time':[],'lon':[],'lat':[]}
    with open(filename) as f:
        for line in f:
            if line[2:13] == "Survey name":
                surveys['name'].append(line[18:-1])

                for line in f:
                    if line[2:4] == "Op":
                        surveys['operator'].append(line[18:-1])
                    if line[2:4] == "Da":
                        surveys['date'].append(line[18:-1])
                    if line[2:4] == "Ti":
                        surveys['time'].append(line[18:-1])
                    if line[2:4] == "LO":
                        surveys['lon'].append(line[16:-1])
                    if line[2:4] == "LA":
                        surveys['lat'].append(line[16:-1])                    
                    if line[2:4] == "GM":
                        break
    return pd.DataFrame(surveys)

def func(xs, m, c):
    
    # [m * x +c for x in xs]
    return [m * x +c for x in xs]
    
    
class gravreader_new(object):
    
    def __init__(self, surveyname, filename):
        self.sname=surveyname
        self.fname=filename
        self.properties = None
        self.rawdata = None
        self.basedata = None
        self.drift = None
        self.processing = None
        
    def get_properties(self):
        """
        Return a dictionary of properties. Read from file only if necessary.
        """
        # Check if already hold properties in memory
        if self.properties is None:
            
            self.properties={'name':'','operator':'','date':'','time':'','lon':'','lat':''}
            
            with open(self.fname) as f:
                for line in f:
                    if line[2:13] == "Survey name":
                        if line[18:-1] == self.sname:
                            self.properties['name']=line[18:-1]

                            for line in f:
                                if line[2:4] == "Op":
                                    self.properties['operator']=line[18:-1]
                                if line[2:4] == "Da":
                                    self.properties['date']=line[18:-1]
                                if line[2:4] == "Ti":
                                    self.properties['time']=line[18:-1]
                                if line[2:4] == "LO":
                                    self.properties['lon']=line[16:-1]
                                if line[2:4] == "LA":
                                    self.properties['lat']=line[16:-1]                   
                                if line[2:4] == "GM":
                                    break
    def get_rawdata(self):
        """
        Return a dictionary of properties. Read from file only if necessary.
        """
        # Check if already hold properties in memory
        if self.rawdata is None:
            
            grav_data={'line':[],'station':[],'alt':[],'grav':[],'sd':[],'tiltx':[],
              'tilty':[],'temp':[],'tide':[],'dur':[],'rej':[],'time':[],
              'dec_timedate':[],'terrain':[],'date':[]}
            
            with open(self.fname) as f:
                for line in f:
                    if line[2:13] == "Survey name":
                        if line[18:-1] == self.sname:
                            for line in f:
                                if line[2:13] == 'CG-5 SURVEY':
                                    break
                                # line_tmp=line[:-1].split(sep=' ')
                                line_tmp=line.lstrip()
                                line_tmp=line.strip("\n")
                                line_tmp=line_tmp.split(' ')
                                data_tmp=[]
                                
                                for val in line_tmp:
                                    if val!='':
                                        data_tmp.append(val)
                                        
                                if len(data_tmp) > 10:
                                    # print(data_tmp)
                                    grav_data['line'].append(float(data_tmp[0]))
                                    grav_data['station'].append(float(data_tmp[1]))
                                    grav_data['alt'].append(float(data_tmp[2]))
                                    grav_data['grav'].append(float(data_tmp[3]))
                                    grav_data['sd'].append(float(data_tmp[4]))
                                    grav_data['tiltx'].append(float(data_tmp[5]))
                                    grav_data['tilty'].append(float(data_tmp[6]))
                                    grav_data['temp'].append(float(data_tmp[7]))
                                    grav_data['tide'].append(float(data_tmp[8]))
                                    grav_data['dur'].append(float(data_tmp[9]))
                                    grav_data['rej'].append(float(data_tmp[10]))
                                    grav_data['time'].append(data_tmp[11])
                                    grav_data['dec_timedate'].append(float(data_tmp[12]))
                                    grav_data['terrain'].append(float(data_tmp[13]))
                                    grav_data['date'].append(data_tmp[14])
                                    # dates.append(mdates.datestr2num("{date}T{time}".format(date=data.iloc[i].date,time=data.iloc[i].time)))
        self.rawdata=pd.DataFrame(grav_data)
                                    
                                
    def get_basedata(self,base=999):
        """
        Extracts the base station readings and calculates a linear drift
        """
        
        data=self.rawdata[self.rawdata.station==base]
        self.basedata=data
        
        dates=data.dec_timedate
        
        # dates=[]
        # for i in range(len(data)):
        #     dates.append(mdates.datestr2num("{date}T{time}".format(date=data.iloc[i].date,time=data.iloc[i].time)))

        # dates=dates-dates[0]
        
        popt, pcov = curve_fit(func, dates, data.grav.values)
        print(popt)
        self.drift=popt
        
    def get_processing(self,base=999):
        
        grav_proc={'station':[],'grav':[],'time':[],'detrend':[]}
        
        data=self.rawdata[self.rawdata.station!=base]
        # print(data)
        stations=data.station.unique()
        
        for station in stations:
            data_tmp=self.rawdata[self.rawdata.station==station]
            grav_tmp=data_tmp.grav.mean()
            date_tmp=data_tmp.dec_timedate.mean()
            
            drift_tmp=date_tmp*self.drift[0]+self.drift[1]
            # print(drift_tmp)
            # dates=[]
            # for i in range(len(data_tmp)):
            #     dates.append(mdates.datestr2num("{date}T{time}".format(date=data_tmp.iloc[i].date,time=data_tmp.iloc[i].time)))
            # date_tmp=np.mean(dates)
            
            # print(grav_tmp)
            # print(date_tmp)
            
            grav_proc['station'].append(station)
            grav_proc['grav'].append(grav_tmp)
            grav_proc['time'].append(date_tmp)
            grav_proc['detrend'].append(grav_tmp-drift_tmp)
            
        self.processing=pd.DataFrame(grav_proc)    
        
                          
    def plot(self,type='Raw',fig=None):
        """
        Plot function
        Arguments:
        type - type of gravity data to plot
        """
        
        if fig==None:
            fig = plt.figure(figsize=(10,5))
            
        if type=='Raw':
            data=self.rawdata
            dates=data.dec_timedate
            plt.scatter(dates,data.grav.values,s=5)
            
        if type=='Base':
            data=self.basedata
            dates=data.dec_timedate
            
            ymodel=func(dates,self.drift[0],self.drift[1])
            plt.plot(dates,ymodel,'k--')
            plt.scatter(dates,data.grav.values)
            
        if type=='Processing':
            data=self.processing
            dates=data.time
            
            plt.scatter(dates,data.detrend.values)
            
        plt.xlabel('Time in days')
        plt.ylabel('Gal')
        plt.grid()
        plt.show() 
        
class gravreader(object):
    def __init__(self, name):
        self.name=name
        self.properties = None
        self.raw_grav = None
            
    def get_properties(self,filename):
        """
        Return a dictionary of properties. Read from file only if necessary.
        """
        # Check if already hold properties in memory
        if self.properties is None:
    
            f=open(filename)
            file=f.readlines()

            # Read properties
            self.properties={'type':file[0][2:-1],'name':file[2][18:-2],'meter':file[4][18:-1],
                       'client':file[6][18:-1],'operator':file[8][18:-1],'date':file[10][18:-1],
                        'time':file[12][18:-1],'lon':file[14][16:-1],'lat':file[16][16:-1],
                       'zone':file[18][16:-1],'gmt_diff':file[20][16:-1]}

            f.close()

    def get_rawdata_new(self,filename):
        """
        Read function for a CG5 gravity file
        Arguments:
        filename - cg5 file 
        """
        f=open(filename)

        file=f.readlines()

        grav_data={'line':[],'station':[],'alt':[],'grav':[],'sd':[],'tiltx':[],
              'tilty':[],'temp':[],'tide':[],'dur':[],'rej':[],'time':[],
              'dec_timedate':[],'terrain':[],'date':[]}

        for line in file[24:-1:2]:

            line_tmp=line[:-1].split(sep=' ')

            data_tmp=[]
            for val in line_tmp:
                if val!='':
                    data_tmp.append(val)

            # print(data_tmp)
            grav_data['line'].append(float(data_tmp[0]))
            grav_data['station'].append(float(data_tmp[1]))
            grav_data['alt'].append(float(data_tmp[2]))
            grav_data['grav'].append(float(data_tmp[3]))
            grav_data['sd'].append(float(data_tmp[4]))
            grav_data['tiltx'].append(float(data_tmp[5]))
            grav_data['tilty'].append(float(data_tmp[6]))
            grav_data['temp'].append(float(data_tmp[7]))
            grav_data['tide'].append(float(data_tmp[8]))
            grav_data['dur'].append(float(data_tmp[9]))
            grav_data['rej'].append(float(data_tmp[10]))
            grav_data['time'].append(data_tmp[11])
            grav_data['dec_timedate'].append(float(data_tmp[12]))
            grav_data['terrain'].append(float(data_tmp[13]))
            grav_data['date'].append(data_tmp[14])

        f.close()
        self.raw_grav=pd.DataFrame(grav_data)
        
    def get_rawdata(self,filename):
        """
        Read function for a CG5 gravity file
        Arguments:
        filename - cg5 file 
        """
        f=open(filename)

        file=f.readlines()

        grav_data={'line':[],'station':[],'alt':[],'grav':[],'sd':[],'tiltx':[],
              'tilty':[],'temp':[],'tide':[],'dur':[],'rej':[],'time':[],
              'dec_timedate':[],'terrain':[],'date':[]}

        for line in file[24:-1:2]:

            line_tmp=line[:-1].split(sep=' ')

            data_tmp=[]
            for val in line_tmp:
                if val!='':
                    data_tmp.append(val)

            # print(data_tmp)
            grav_data['line'].append(float(data_tmp[0]))
            grav_data['station'].append(float(data_tmp[1]))
            grav_data['alt'].append(float(data_tmp[2]))
            grav_data['grav'].append(float(data_tmp[3]))
            grav_data['sd'].append(float(data_tmp[4]))
            grav_data['tiltx'].append(float(data_tmp[5]))
            grav_data['tilty'].append(float(data_tmp[6]))
            grav_data['temp'].append(float(data_tmp[7]))
            grav_data['tide'].append(float(data_tmp[8]))
            grav_data['dur'].append(float(data_tmp[9]))
            grav_data['rej'].append(float(data_tmp[10]))
            grav_data['time'].append(data_tmp[11])
            grav_data['dec_timedate'].append(float(data_tmp[12]))
            grav_data['terrain'].append(float(data_tmp[13]))
            grav_data['date'].append(data_tmp[14])

        f.close()
        self.raw_grav=pd.DataFrame(grav_data)
        
    def plot(self,type='Raw',fig=None):
        """
        Plot function
        Arguements:
        type - type of gravity data to plot
        """
        print(self)
        dates=[]
        for i in range(len(self.raw_grav)):
            dates.append(mdates.datestr2num("{date}T{time}".format(date=self.raw_grav.iloc[i].date,time=self.raw_grav.iloc[i].time)))
        data=self.raw_grav.grav.values

        if fig==None:
            fig = plt.figure(figsize=(10,5))
            
        plt.plot(dates-dates[0],data)
        plt.xlabel('Time in days')
        plt.ylabel('Gal')
        plt.grid()
        plt.show()
        
