#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 09:14:50 2016

@author: christian-dsa
"""

#import csv


#tn = telnetlib.telnet(ip,port) object
def command(tn, SCPI):
    command_timeout = 1

    response = ""

    SCPI = SCPI.encode('ascii')
    

    tn.write(b"*OPC?")
    response = tn.read_until(b"\n",command_timeout)
    
    if response == b'1\n' :
        tn.write(SCPI)
        response = tn.read_until(b"\n",command_timeout)
        response = response.decode("utf-8")
    else :
        response = "ERROR: Busy"
        
    return response
    
def get_memory_depth(tn):
    # Define number of horizontal grid divisions for DS1000Z
    h_grid = 12

    # ACQuire:MDEPth
    mdep = command(tn, "ACQ:MDEP?")

    # if mdep is "AUTO"
    if mdep == "AUTO\n":
        # ACQuire:SRATe
        srate = float(command(tn, "ACQ:SRAT?"))

        # TIMebase[:MAIN]:SCALe
        scal = float(command(tn, "TIM:SCAL?"))

        # mdep = h_grid * scal * srate
        mdep = h_grid * scal * srate

    # return mdep
    return int(mdep)
    
def get_displayed_channels(tn):
    # Scan for displayed channels
    channel_list = []
    for channel in ["chan1", "chan2", "chan3", "chan4", "math"]:
        response = command(tn, channel + ":display?")

        # Strip '\n' terminator
        response = response[:-1]
        if response == '1':
            channel_list += [channel]
    return channel_list

# mode : "NORMal"
#        "MAXimum"
#        "RAW"
"""
def get_csv(tn,mode):
    
    # TMC Header #NXXXXXXXXX
    TMC_Length = 11
    
    
    channel_list = get_displayed_channels(tn)
    
    # For each active channel
    for channel in channel_list:
        # Select Source
        command(tn,":WAVeform:SOURce "+channel)
        # Set Format to ASCII
        command(tn,":WAVeform:FORMat ASC")
        # Set Mode
        command(tn,":WAVeform:MODE"+mode)

"""