#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 09:14:50 2016

@author: christian-dsa
"""

#import csv

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
        response = "ERROR"
        
    return response
    