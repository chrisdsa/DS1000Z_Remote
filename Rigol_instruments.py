#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 09:14:50 2016

@author: christian-dsa
"""

import csv

# tn : telnetlib.Telnet(ip,port,timeout)
class DS1000Z:

    def __init__(self,tn):
        self.tn = tn
        pass

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
    """
    def get_csv(self,mode):
        
        # TMC Header #NXXXXXXXXX
        TMC_Length = 11
        
        # Data array : timestamp, CH1, CH2, CH3, CH4
        data = [['t'],[],[],[],[]]
        
        # Get Mem Depth
        if mode == NORMal:
            mdep = 1200
        else:
            mdep = self.get_memory_depth()
        # Get Sa Rate
        srate = float(self.command("ACQ:SRATe?"))
        # Get Scale
        scal = float(self.command("TIM:SCAL?"))
        # Horizontal Grid
        h_grid = 12
        
        # Timestamp
        step = h_grid*scal/mdep
        step = round(step,12)
        timstp = ""
        
        for i in range(0,mdep):
            timstp+=str(round(i*step,12))+','
        
        timstp = timstp.split(',')
        timstp = timstp[:-1]
        
        data[0]+= timstp
        
        channel_list = self.get_displayed_channels()
        data_index = 1
        # For each active channel
        for channel in channel_list:
            # Select Source
            self.command(":WAVeform:SOURce "+channel)
            # Set Format to ASCII
            self.command(":WAVeform:FORMat ASC")
            # Set Mode
            self.command(":WAVeform:MODE"+mode)
            
            data[data_index] += channel
            buff = ""
          
            # ASII Format maximum point = 15625
            # Number of point per batch
            max_pts_batch = 15620
            max_batch = int(mdep // max_pts_batch + (mdep % max_pts_batch >0))
            size_batch = mdep // max_batch
            
            for batch in range(0,max_batch):
                start = int(batch*size_batch+1)
                if batch == (max_batch-1):
                    stop = int(mdep)
                else:
                    stop = int((batch+1)*size_batch)
                print("start = "+str(start)+"  stop= "+str(stop))
                #self.command(":WAVeform:STARt"+str(start))
                #self.command(":WAVeform:STARt"+str(stop))
            data_index = data_index +1
            print(data_index)
            
    """            