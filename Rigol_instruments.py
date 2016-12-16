#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 09:14:50 2016

@author: christian-dsa
"""

import csv
import datetime
import time
import numpy as np

# tn : telnetlib.Telnet(ip,port,timeout)
class DS1000Z:

    def __init__(self,tn):
        self.tn = tn
        pass
        
    def set_capture_path(self,path):
        self.capt_path = path
        

    def command(self,SCPI):
        command_timeout = 1

        response = ""

        SCPI = SCPI.encode('ascii')
        

        self.tn.write(b"*OPC?")
        response = self.tn.read_until(b"\n",command_timeout)
        
        if response == b'1\n' :
            self.tn.write(SCPI)
            response = self.tn.read_until(b"\n",command_timeout)
            response = response.decode("utf-8")
        else :
            response = "ERROR: Busy"
            
        return response

    # Value : 
    # 1 CH   : "AUTO","12k","120k","1.2M","12M"
    # 2 CH   : "AUTO","6k","60k","600k","6M"
    # 3,4 CH : "AUTO","3k","30k","300k","3M"
    def set_memory_depth(self,value):
        if value == "12k" : value = "12000"
        elif value == "120k" : value = "120000"
        elif value == "1.2M" : value = "1200000"
        elif value == "12M" : value = "12000000"
        elif value == "6k" : value = "6000"
        elif value == "60k" : value = "60000"
        elif value == "600k" : value = "600000"
        elif value == "6M" : value = "6000000"
        elif value == "3k" : value = "3000"
        elif value == "30k" : value = "30000"
        elif value == "300k" : value = "300000"
        elif value == "3M" : value = "3000000"
        else : pass
        
        self.command(":ACQuire:MDEPth "+value)
        mdep = self.command("ACQ:MDEP?")
        print("Memory set to : "+str(mdep))
        return mdep
  
    def get_memory_depth(self):
        # Define number of horizontal grid divisions for DS1000Z
        h_grid = 12

        # ACQuire:MDEPth
        mdep = self.command("ACQ:MDEP?")

        # if mdep is "AUTO"
        if mdep == "AUTO\n":
            # ACQuire:SRATe
            srate = float(self.command("ACQ:SRAT?"))

            # TIMebase[:MAIN]:SCALe
            scal = float(self.command("TIM:SCAL?"))

            # mdep = h_grid * scal * srate
            mdep = h_grid * scal * srate

        # return mdep
        return int(mdep)
        
    def get_displayed_channels(self):
        # Scan for displayed channels
        channel_list = []
        for channel in ["chan1", "chan2", "chan3", "chan4", "math"]:
            response = self.command(channel + ":display?")

            # Strip '\n' terminator
            response = response[:-1]
            if response == '1':
                channel_list += [channel]
        return channel_list

    # mode : "NORMal"
    #        "MAXimum"
    #        "RAW"
    # Optional : "filename"
    def get_csv(self,mode,*args):
        
        # TMC Header #NXXXXXXXXX
        TMC_Length = 11
        
        # Data array : timestamp, CH1, CH2, CH3, CH4
        data = [[],[],[],[],[]]
        
        # Get Mem Depth
        if mode == "NORMal":
            mdep = 1200
        else:
            self.command(":STOP")
            mdep = self.get_memory_depth()
        # Get Sa Rate
        #srate = float(self.command("ACQ:SRATe?"))
        # Get Scale
        scal = float(self.command("TIM:SCAL?"))
        # Horizontal Grid
        h_grid = 12
        
        # TIMESTAMP #
        # Improvement : Generate the timestamp with numpy = faster
        print("Generate timestamp")
        step = h_grid*scal/mdep
        step = round(step,12)
        
        data[0] = np.arange(0,h_grid*scal,step)
        
        """
        # IF NUMPY IS NOT INSTALLED 
        timstp = ""
        
        for i in range(0,mdep):
            timstp+=str(round(i*step,12))+','
        
        timstp = timstp[:-1]
        timstp = timstp.split(',')        
        data[0]+= timstp
        """
        
        channel_list = self.get_displayed_channels()
        data_index = 1
        
        # ASII Format maximum point = 15625
        # Number of point per batch
        max_pts_batch = 15620
        max_batch = int(mdep // max_pts_batch + (mdep % max_pts_batch >0))
        size_batch = mdep // max_batch
        
        # DATA #
        # For each active channel
        for channel in channel_list:
            print("Getting "+channel+" data")
            
            # Select Source
            self.command(":WAVeform:SOURce "+channel)
            # Set Format to ASCII
            self.command(":WAVeform:FORMat ASC")
            # Set Mode
            self.command(":WAVeform:MODE "+mode)
                       
            # Get the channel data
            buff = ""
            
            for batch in range(0,max_batch):
                start = int(batch*size_batch+1)
                if batch == (max_batch-1):
                    stop = int(mdep)
                else:
                    stop = int((batch+1)*size_batch)
                
                self.command(":WAVeform:STARt "+str(start))
                self.command(":WAVeform:STOP "+str(stop))
                buff += self.command(":WAVeform:DATA?")
            
            # Move data from buffer to list
            buff = buff[TMC_Length:-1]
            buff = str(channel)+","+buff
            buff = buff.split(',')
            data[data_index] = buff
            data_index = data_index +1
        
        # CSV #
        print("Saving CSV")
        # Set filename
        if len(args) > 0:
            filename = self.capt_path+args[0]+".csv"
        else:
            time = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
            filename = self.capt_path+"DS1000Z_"+time+".csv"
        
        # Check the data lenght, keep the minimum
        nb_active_channel = len(channel_list)
        range_active_channel = range(0,(nb_active_channel+1))
        min_val = mdep+1
        for i in range_active_channel:
            l_data = len(data[i])
            temp_min = min(min_val,l_data)
            if temp_min < min_val:
                min_val = temp_min
        
        # Create CSV
        with open(filename,'w',newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
            i = 0
            # Header
            if nb_active_channel == 1:
                spamwriter.writerow(['t',data[1][i]])
            elif nb_active_channel == 2:
                spamwriter.writerow(['t',data[1][i],data[2][i]])
            elif nb_active_channel == 3:
                spamwriter.writerow(['t',data[1][i],data[2][i],data[3][i]])
            elif nb_active_channel == 4:
                spamwriter.writerow(['t',data[1][i],data[2][i],data[3][i],data[4][i]])                    
            i = i+1 
            # Data
            while i < min_val:
                if nb_active_channel == 1:
                    spamwriter.writerow([data[0][i-1],data[1][i]])
                elif nb_active_channel == 2:
                    spamwriter.writerow([data[0][i-1],data[1][i],data[2][i]])
                elif nb_active_channel == 3:
                    spamwriter.writerow([data[0][i-1],data[1][i],data[2][i],data[3][i]])
                elif nb_active_channel == 4:
                    spamwriter.writerow([data[0][i-1],data[1][i],data[2][i],data[3][i],data[4][i]])                    
                i = i+1 

    def get_bmp(self,*args):
        answer_wait_s = 20
        file_size = 1152068

        # filename
        if len(args) > 0:
            filename = self.capt_path+args[0]+".bmp"
        else:
            time_now = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
            filename = self.capt_path+"DS1000Z_"+time_now+".bmp"
        
        # Set timestamp with time
        timeout = time.time()+answer_wait_s
        
        # Get Data
        response = b""
        self.tn.write(b":DISPlay:DATA?")
        while len(response) < file_size:
            response += self.tn.read_eager()
            # Set mecanism to break the loop if it is too long
            if time.time()>timeout:
                print("ERROR : Timeout")
                break
        # Save to bmp
        TMC_header = response[1]-48+2
        scr_file = open(filename, "wb")
        scr_file.write(response[TMC_header:-1])
        scr_file.close()

























                