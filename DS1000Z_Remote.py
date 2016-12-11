#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 09:57:19 2016

@author: christian-dsa
"""
"""
DS1000Z_Remote : 
    set the connection between the scope and the computer
    interface between the user and the rigol function
    
    DS1000Z_Remote control the terminal where the user enter the scope's ip,
    the command like : screenshot, set memory depth and so on
    
Rigol_functions :
    Contain all the function to interface with the rigol scope
    These function are called by DS1000Z_Remote
    
"""
import telnetlib
import os


# Rigol/LXI specific constants

port = 5555;

# Communication constants
short_timeout  = 1
long_timout = 5


# Path to store screenshots
capture_path = "captures/";

# Create the folder if it doesn't exist
if not os.path.exists(capture_path):
    os.makedirs(capture_path)

# Request instrument IP
instr_ip = input("Enter instrument IP : ")

# Open connection
try :
    tn = telnetlib.Telnet(instr_ip,port,short_timeout)
except :
    print("ERROR : Connection Timout")
    pass

# Request Instrument ID
