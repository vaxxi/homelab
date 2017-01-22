#!/usr/bin/python

import netsnmp
import time
import socket
import subprocess
import json
import sys

#
# monitored host settings
#

# can be set to 127.0.0.1 if the script is executed on the Microserver
HOST='127.0.0.1'
# should be set to the ILO interface IP address
ILOHOST=''
# SNMP community and version to be used
SNMP_COMMUNITY='public'
SNMP_VERSION=2
# 1 if IPMI information should be queried, 0 otherwise
USE_IPMI=1
# unique server name 
SERVER_NAME='microserver'
# separator used for Carbon metrics
SEPARATOR='.'
# Carbon server and port where the data should be sent
CARBON_SERVER=''
CARBON_PORT=2003
# change DEBUG to 1 if you wish to print messages sent to Carbon in console
DEBUG=1

# open Carbon socket and keep it open while pushing data
sock = socket.socket()
sock.connect((CARBON_SERVER, CARBON_PORT))


# initiate SNMP session
session = netsnmp.Session(DestHost=HOST, Version=SNMP_VERSION, Community=SNMP_COMMUNITY)

# define monitoring variable
measurements = {}

# get disk IDs in the system
def GetDisk():
  global session
  vars = netsnmp.VarList(netsnmp.Varbind('dskIndex'),netsnmp.Varbind('dskDevice'),netsnmp.Varbind('dskTotal'),netsnmp.Varbind('dskAvail'),netsnmp.Varbind('dskUsed'))
  result = session.walk(vars)
  for i in range(0, len(result), 5):
    if result[i+1].find("/dev/") != -1:
      measurements[SERVER_NAME+SEPARATOR+"disk"+SEPARATOR+result[i+1].replace('/dev/','')+SEPARATOR+"total"]= result[i+2]
      measurements[SERVER_NAME+SEPARATOR+"disk"+SEPARATOR+result[i+1].replace('/dev/','')+SEPARATOR+"avail"]= result[i+3]
      measurements[SERVER_NAME+SEPARATOR+"disk"+SEPARATOR+result[i+1].replace('/dev/','')+SEPARATOR+"used"]= result[i+4]

def GetNet():
  global session
  vars = netsnmp.VarList(netsnmp.Varbind('ifIndex'),netsnmp.Varbind('ifDescr'),netsnmp.Varbind('ifHCInOctets'),netsnmp.Varbind('ifHCOutOctets'))
  result = session.walk(vars)
  for i in range(0, len(result), 4):
    measurements[SERVER_NAME+SEPARATOR+"net"+SEPARATOR+result[i+1]+SEPARATOR+"in"]= result[i+2]
    measurements[SERVER_NAME+SEPARATOR+"net"+SEPARATOR+result[i+1]+SEPARATOR+"out"]= result[i+3]    

def GetMem():
  global session
  vars = netsnmp.VarList(netsnmp.Varbind('memTotalReal'),netsnmp.Varbind('memAvailReal'),
         netsnmp.Varbind('memTotalSwap'),netsnmp.Varbind('memAvailSwap'),netsnmp.Varbind('memTotalFree'),
         netsnmp.Varbind('memShared'), netsnmp.Varbind('memBuffer'), netsnmp.Varbind('memCached'))
  result = session.walk(vars)
  measurements[SERVER_NAME+SEPARATOR+"mem"+SEPARATOR+"memTotalReal"] = result[0]
  measurements[SERVER_NAME+SEPARATOR+"mem"+SEPARATOR+"memAvailReal"] = result[1]  
  measurements[SERVER_NAME+SEPARATOR+"mem"+SEPARATOR+"memTotalSwap"] = result[2]
  measurements[SERVER_NAME+SEPARATOR+"mem"+SEPARATOR+"memAvailSwap"] = result[3]
  measurements[SERVER_NAME+SEPARATOR+"mem"+SEPARATOR+"memTotalFree"] = result[4]
  measurements[SERVER_NAME+SEPARATOR+"mem"+SEPARATOR+"memShared"] = result[5]
  measurements[SERVER_NAME+SEPARATOR+"mem"+SEPARATOR+"memBuffer"] = result[6]
  measurements[SERVER_NAME+SEPARATOR+"mem"+SEPARATOR+"memCached"] = result[7]

def GetCPU():
  global session
  vars = netsnmp.VarList(netsnmp.Varbind('ssCpuRawUser'), netsnmp.Varbind('ssCpuRawNice'),netsnmp.Varbind('ssCpuRawSystem'),netsnmp.Varbind('ssCpuRawIdle'),netsnmp.Varbind('ssCpuRawWait'),netsnmp.Varbind('ssCpuRawKernel'),netsnmp.Varbind('ssCpuRawInterrupt'))
  result = session.walk(vars)
  measurements[SERVER_NAME+SEPARATOR+"cpu"+SEPARATOR+"raw"+SEPARATOR+"ssCpuRawUser"] = result[0]
  measurements[SERVER_NAME+SEPARATOR+"cpu"+SEPARATOR+"raw"+SEPARATOR+"ssCpuRawNice"] = result[1]  
  measurements[SERVER_NAME+SEPARATOR+"cpu"+SEPARATOR+"raw"+SEPARATOR+"ssCpuRawSystem"] = result[2]
  measurements[SERVER_NAME+SEPARATOR+"cpu"+SEPARATOR+"raw"+SEPARATOR+"ssCpuRawIdle"] = result[3]
  measurements[SERVER_NAME+SEPARATOR+"cpu"+SEPARATOR+"raw"+SEPARATOR+"ssCpuRawWait"] = result[4]
  measurements[SERVER_NAME+SEPARATOR+"cpu"+SEPARATOR+"raw"+SEPARATOR+"ssCpuRawKernel"] = result[5]
  measurements[SERVER_NAME+SEPARATOR+"cpu"+SEPARATOR+"raw"+SEPARATOR+"ssCpuRawInterrupt"] = result[6]
  vars = netsnmp.VarList(netsnmp.Varbind('laLoadInt'), netsnmp.Varbind('hrProcessorLoad'))
  result = session.walk(vars)
  measurements[SERVER_NAME+SEPARATOR+"cpu"+SEPARATOR+"load"+SEPARATOR+"1"] = result[0]
  measurements[SERVER_NAME+SEPARATOR+"cpu"+SEPARATOR+"load"+SEPARATOR+"5"] = result[1]
  measurements[SERVER_NAME+SEPARATOR+"cpu"+SEPARATOR+"load"+SEPARATOR+"15"] = result[2]
  measurements[SERVER_NAME+SEPARATOR+"cpu"+SEPARATOR+"core"+SEPARATOR+"0"] = result[3]
  measurements[SERVER_NAME+SEPARATOR+"cpu"+SEPARATOR+"core"+SEPARATOR+"1"] = result[4]
  
def GetILOTemp():
  if USE_IPMI==1:
    ipmi_sdr=subprocess.check_output(['ipmitool','sdr']).strip().split("\n")
    ipmi_values_dict = {}
    ipmi_status_dict = {}
    for sdr_row in ipmi_sdr:
      vals = sdr_row.split("|")
      vals = map(lambda s: s.strip(), vals)
      ipmi_values_dict[vals[0]]=vals[1]
      ipmi_status_dict[vals[0]]=vals[2]    
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.inlet"] = ipmi_values_dict["01-Inlet Ambient"].strip(" degrees C")
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.cpu"] = ipmi_values_dict["02-CPU"].strip(" degrees C")
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.dimm"] = ipmi_values_dict["03-P1 DIMM 1-2"].strip(" degrees C")
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.chipset"] = ipmi_values_dict["05-Chipset"].strip(" degrees C")
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.chipsetzone"] = ipmi_values_dict["06-Chipset Zone"].strip(" degrees C")
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.vrzone"] = ipmi_values_dict["07-VR P1 Zone"].strip(" degrees C")
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.ilozone"] = ipmi_values_dict["09-iLO Zone"].strip(" degrees C")
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.pcizone"] = ipmi_values_dict["11-PCI 1 Zone"].strip(" degrees C")
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.exhaust"] = ipmi_values_dict["12-Sys Exhaust"].strip(" degrees C")
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.fan"] = ipmi_values_dict["Fan 1"].strip(" percent")
  else:    
    session = netsnmp.Session(DestHost=HOST, Version=SNMP_VERSION, Community=SNMP_COMMUNITY)
    temp_inlet="enterprises.232.6.2.6.8.1.4.0.1"
    temp_cpu="enterprises.232.6.2.6.8.1.4.0.2"
    temp_dimm="enterprises.232.6.2.6.8.1.4.0.3"
    temp_chipset="enterprises.232.6.2.6.8.1.4.0.5"
    temp_chipsetzone="enterprises.232.6.2.6.8.1.4.0.6"
    temp_vrzone="enterprises.232.6.2.6.8.1.4.0.7"
    temp_ilozone="enterprises.232.6.2.6.8.1.4.0.9"
    temp_pci="enterprises.232.6.2.6.8.1.4.0.11"
    temp_pcizone="enterprises.232.6.2.6.8.1.4.0.12"
    vars = netsnmp.VarList(netsnmp.Varbind(temp_inlet),netsnmp.Varbind(temp_cpu),netsnmp.Varbind(temp_dimm),netsnmp.Varbind(temp_chipset),netsnmp.Varbind(temp_chipsetzone),netsnmp.Varbind(temp_vrzone),netsnmp.Varbind(temp_ilozone),netsnmp.Varbind(temp_pci),netsnmp.Varbind(temp_pcizone))
    result = session.walk(vars)
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.inlet"] =result[0]
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.cpu"] = result[1]
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.dimm"] = result[2]
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.chipset"] = result[3]
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.chipsetzone"] = result[4]
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.vrzone"] = result[5]
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.ilozone"] = result[6]
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.pci"] = result[7]
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.pcizone"] = result[8]
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.exhaust"] = result[9]
    measurements[SERVER_NAME+SEPARATOR+"env"+SEPARATOR+"ilo.fan"] = result[10]


while True:
  # get measurements
  GetDisk()
  GetNet()
  GetMem()
  GetCPU()
  GetILOTemp()
  if DEBUG == 1:
    print json.dumps(measurements, sort_keys=True, indent=4)

  # send data
  currtime = int(time.time())
  for key, value in measurements.items():
    carbonmsg=key + ' ' + value + ' ' + str(currtime) + '\n'
    if DEBUG == 1:
      print carbonmsg
    sock.sendall(carbonmsg)  

  # sleep before a new batch of data
  time.sleep(60)

# close the socket  
sock.close()
