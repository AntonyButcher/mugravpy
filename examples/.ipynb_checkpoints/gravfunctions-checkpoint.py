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
        self.topo = None
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
                                    
    def check_rawdata(self,station):
        """
        Displays individual station reading.
        """
        data_tmp=self.rawdata[self.rawdata.station==station]
        
        plt.scatter(data_tmp.index.values,data_tmp.grav)
        
        plt.scatter(data_tmp.index.values.mean(),data_tmp.grav.mean(),marker='*',s=150)
        plt.grid()
        plt.xlabel('Index Value')
        plt.ylabel('Gal')
        plt.show()
    
    def remove_rawdata(self,indexs=[]):
        """
        Removes individual station readings.
        indexs - list of readings to remove.
        """
        
        for ix in indexs:
            self.rawdata=self.rawdata.drop(ix)
        
    
    def get_basedata(self,base=999):
        """
        Extracts the base station readings and calculates a linear drift
        """
        
        data=self.rawdata[self.rawdata.station==base]
        self.basedata=data
        
        dates=data.dec_timedate
        
        popt, pcov = curve_fit(func, dates, data.grav.values)
        print(popt)
        self.drift=popt
    
    def get_topo(self, topofile):
        """
        Imports the topo data
        """
        if self.topo is None:
            self.topo=pd.read_csv(topofile,usecols=[0,1,2,3],names=('station','height','easting','northing'),skiprows=[0])
            
        plt.scatter(self.topo.easting,self.topo.height)
        plt.xlabel('Easting (m)')
        plt.ylabel('Height (m)')
        plt.show()
        
    def get_processing(self, base=999,rho=1.9):
        
        grav_proc={'station':[],'grav':[],'dec_timedate':[],'detrend':[]}
        
        data=self.rawdata[self.rawdata.station!=base]
        # print(data)
        stations=data.station.unique()
        
        for station in stations:
            data_tmp=self.rawdata[self.rawdata.station==station]
            grav_tmp=data_tmp.grav.mean()
            date_tmp=data_tmp.dec_timedate.mean()
            
            drift_tmp=date_tmp*self.drift[0]+self.drift[1]
           
            grav_proc['station'].append(str(station).split('.')[0])
            grav_proc['grav'].append(grav_tmp)
            grav_proc['dec_timedate'].append(date_tmp)
            grav_proc['detrend'].append(grav_tmp-drift_tmp)
            
        self.processing=pd.DataFrame(grav_proc)  
        
        if self.topo is None:
            print('No topo data present, please use get_topo function.')
        else:
            self.processing=self.processing.merge(self.topo,how = 'inner',on='station')
            
            self.processing.insert(7,'fc',self.processing.height*0.3086)
            self.processing.insert(8,'bc',self.processing.height*0.04191*rho)
            self.processing.insert(9,'ba',self.processing.detrend+self.processing.fc-self.processing.bc)
        
    def detrend_ba(self,exclude=[]):
        
        data_tmp=self.processing
        
        for ix in exclude:
            data_tmp=data_tmp.drop(ix)
            
        popt, pcov = curve_fit(func, data_tmp.easting, data_tmp.ba.values)
        
        ymodel=func(self.processing.easting,popt[0],popt[1])
    
        plt.figure(figsize=[10,5])
        plt.plot(self.processing.easting,ymodel,'k--')
        plt.scatter(self.processing.easting,self.processing.ba)
        plt.grid()
        plt.xlabel('Easting')
        plt.ylabel('Gal')
        plt.show()
                   
        detrend_tmp=self.processing.ba.values-ymodel
        self.processing['ba_detrend']=detrend_tmp
        
        plt.figure(figsize=[10,5])
        plt.plot(self.processing.easting,self.processing.ba_detrend*1000)
        plt.scatter(self.processing.easting,self.processing.ba_detrend*1000)
        plt.grid()
        plt.xlabel('Easting')
        plt.ylabel('MicroGal')
        plt.show()
            
            
            
    
    
    def plot(self,type='raw',xaxis='time',fig=None):
        """
        Plot function
        Arguments:
        type - type of gravity data to plot
        xaxis - column to use as x-axis
        """
        
        if fig==None:
            fig = plt.figure(figsize=(10,5))
            
        if xaxis=='time':
            xn='dec_timedate'
            plt.xlabel('Time in days')
            
        if xaxis=='distance':
            xn='easting'
            plt.xlabel('Distance (m)')
            
        if xaxis=='station':
            xn='station'
            plt.xlabel('Station name')
            
        if xaxis=='index':
            xn='index'
            plt.xlabel('Index')
            
            
        if type=='raw':
            data=self.rawdata
            plt.scatter(data[xn],data.grav.values,s=5)
            
        if type=='base':
            data=self.basedata            
            ymodel=func(dates,self.drift[0],self.drift[1])
            plt.plot(xn,ymodel,'k--')
            plt.scatter(data[xn],data.grav.values)
            
        if type=='detrend':
            data=self.processing            
            plt.scatter(data[xn],data.detrend.values)
        
        if type=='ba':
            data=self.processing            
            plt.scatter(data[xn].values,data.ba.values)
        
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
        
