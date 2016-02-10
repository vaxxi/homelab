#!/usr/bin/python

import netsnmp
import time
import socket
import subprocess
import json

# monitored host settings
HOST='127.0.0.1'
ILOHOST='192.168.1.23'
SNMP_COMMUNITY='public'
SNMP_VERSION=2
USE_IPMI=1

# change this array to match your network interface index numbers
INTERFACE_ID=(2,3)

# change to your Carbon server hostname and port
CARBON_SERVER='deb3'
CARBON_PORT=2003

# open Carbon socket and keep it open while pushing data
sock = socket.socket()
sock.connect((CARBON_SERVER, CARBON_PORT))

def QueryLoad(ccname,host,community,version,mibname):
  qval=netsnmp.snmpget(netsnmp.Varbind(mibname), Version = version, DestHost = host, Community = community)
  carbonmsg=ccname + ' ' + qval[0] + ' %d\n' % int(time.time())
  print "Sending message: %s \n" % carbonmsg
  sock.sendall(carbonmsg)

def SimpleLoad(ccname,ccval):
  carbonmsg=ccname + ' ' + ccval + ' %d\n' % int(time.time())
  print "Sending message: %s \n" % carbonmsg
  sock.sendall(carbonmsg)

while True:
  # get network interface data
  for i in INTERFACE_ID:
    # define SNMP OIDs
    if_name="IF-MIB::ifName." + str(i)
    if_octets_in="IF-MIB::ifInOctets." + str(i)
    if_octets_out="IF-MIB::ifOutOctets." + str(i)
    if_hc_in="IF-MIB::ifHCInOctets." + str(i)
    if_hc_out="IF-MIB::ifHCOutOctets." + str(i)
    if_admin_status="IF-MIB::ifAdminStatus." + str(i)
    if_op_status="IF-MIB::ifOperStatus." + str(i)
        
    # get SNMP values
    if_name_val = netsnmp.snmpget(netsnmp.Varbind(if_name), Version = SNMP_VERSION, DestHost = HOST, Community=SNMP_COMMUNITY)
    QueryLoad('hp.if.'+if_name_val[0]+'.in', HOST, SNMP_COMMUNITY, SNMP_VERSION, if_hc_in)
    QueryLoad('hp.if.'+if_name_val[0]+'.out', HOST, SNMP_COMMUNITY, SNMP_VERSION, if_hc_out)
    QueryLoad('hp.if.'+if_name_val[0]+'.status.adm', HOST, SNMP_COMMUNITY, SNMP_VERSION, if_admin_status)
    QueryLoad('hp.if.'+if_name_val[0]+'.status.oper', HOST, SNMP_COMMUNITY, SNMP_VERSION, if_op_status)

  # get memory data
  i=0
  mem_cached="UCD-SNMP-MIB::memCached." + str(i)
  mem_shared="UCD-SNMP-MIB::memShared." + str(i)
  mem_buffer="UCD-SNMP-MIB::memBuffer." + str(i)
  mem_swap_total="UCD-SNMP-MIB::memTotalSwap." + str(i)
  mem_swap_avail="UCD-SNMP-MIB::memAvailSwap." + str(i)
  mem_totalreal="UCD-SNMP-MIB::memTotalReal." + str(i)
  mem_availreal="UCD-SNMP-MIB::memAvailReal." + str(i)
  mem_totalfree="UCD-SNMP-MIB::memTotalFree." + str(i)
  QueryLoad('hp.mem.cached',HOST, SNMP_COMMUNITY, SNMP_VERSION, mem_cached)
  QueryLoad('hp.mem.shared',HOST, SNMP_COMMUNITY, SNMP_VERSION, mem_shared)  
  QueryLoad('hp.mem.buffer',HOST, SNMP_COMMUNITY, SNMP_VERSION, mem_buffer)
  QueryLoad('hp.swap.total',HOST, SNMP_COMMUNITY, SNMP_VERSION, mem_swap_total)
  QueryLoad('hp.swap.avail',HOST, SNMP_COMMUNITY, SNMP_VERSION, mem_swap_avail)
  QueryLoad('hp.mem.total.real',HOST, SNMP_COMMUNITY, SNMP_VERSION, mem_totalreal)
  QueryLoad('hp.mem.total.avail',HOST, SNMP_COMMUNITY, SNMP_VERSION, mem_availreal)
  QueryLoad('hp.mem.total.free',HOST, SNMP_COMMUNITY, SNMP_VERSION, mem_totalfree)

  # get CPU counters
  i=0
  cpu_rawuser="UCD-SNMP-MIB::ssCpuRawUser." + str(i)
  cpu_rawnice="UCD-SNMP-MIB::ssCpuRawNice." + str(i)
  cpu_rawsystem="UCD-SNMP-MIB::ssCpuRawSystem." + str(i)
  cpu_rawidle="UCD-SNMP-MIB::ssCpuRawIdle." + str(i)
  cpu_rawwait="UCD-SNMP-MIB::ssCpuRawWait." + str(i)
  cpu_rawkernel="UCD-SNMP-MIB::ssCpuRawKernel." + str(i)
  cpu_rawinterrupt="UCD-SNMP-MIB::ssCpuRawInterrupt." + str(i)
  QueryLoad("hp.cpu.raw.user",HOST,SNMP_COMMUNITY, SNMP_VERSION, cpu_rawuser)
  QueryLoad("hp.cpu.raw.nice",HOST,SNMP_COMMUNITY, SNMP_VERSION, cpu_rawnice)  
  QueryLoad("hp.cpu.raw.system",HOST,SNMP_COMMUNITY, SNMP_VERSION, cpu_rawsystem)  
  QueryLoad("hp.cpu.raw.idle",HOST,SNMP_COMMUNITY, SNMP_VERSION, cpu_rawidle)  
  QueryLoad("hp.cpu.raw.wait",HOST,SNMP_COMMUNITY, SNMP_VERSION, cpu_rawwait)  
  QueryLoad("hp.cpu.raw.kernel",HOST,SNMP_COMMUNITY, SNMP_VERSION, cpu_rawkernel)
  QueryLoad("hp.cpu.raw.interrupt",HOST,SNMP_COMMUNITY, SNMP_VERSION, cpu_rawinterrupt)
  
  # get ILO temperatures
  if USE_IPMI==0:
    temp_inlet="enterprises.232.6.2.6.8.1.4.0.1"
    temp_cpu="enterprises.232.6.2.6.8.1.4.0.2"
    temp_dimm="enterprises.232.6.2.6.8.1.4.0.3"
    temp_chipset="enterprises.232.6.2.6.8.1.4.0.5"
    temp_chipsetzone="enterprises.232.6.2.6.8.1.4.0.6"
    temp_vrzone="enterprises.232.6.2.6.8.1.4.0.7"
    temp_ilozone="enterprises.232.6.2.6.8.1.4.0.9"
    temp_pci="enterprises.232.6.2.6.8.1.4.0.11"
    temp_pcizone="enterprises.232.6.2.6.8.1.4.0.12"
    QueryLoad('hp.ilo.temp.inlet',ILOHOST, SNMP_COMMUNITY, SNMP_VERSION, temp_inlet)
    QueryLoad('hp.ilo.temp.cpu',ILOHOST, SNMP_COMMUNITY, SNMP_VERSION, temp_cpu)
    QueryLoad('hp.ilo.temp.dimm',ILOHOST, SNMP_COMMUNITY, SNMP_VERSION, temp_dimm)
    QueryLoad('hp.ilo.temp.chipset',ILOHOST, SNMP_COMMUNITY, SNMP_VERSION, temp_chipset)
    QueryLoad('hp.ilo.temp.chipsetzone',ILOHOST, SNMP_COMMUNITY, SNMP_VERSION, temp_chipsetzone)
    QueryLoad('hp.ilo.temp.vrzone',ILOHOST, SNMP_COMMUNITY, SNMP_VERSION, temp_vrzone)
    QueryLoad('hp.ilo.temp.ilozone',ILOHOST, SNMP_COMMUNITY, SNMP_VERSION, temp_ilozone)
    QueryLoad('hp.ilo.temp.pci',ILOHOST, SNMP_COMMUNITY, SNMP_VERSION, temp_pci)
    QueryLoad('hp.ilo.temp.pcizone',ILOHOST, SNMP_COMMUNITY, SNMP_VERSION, temp_pcizone)
  else:  
    ipmi_sdr=subprocess.check_output(['ipmitool','sdr']).strip().split("\n")
    ipmi_values_dict = {}
    ipmi_status_dict = {}
    for sdr_row in ipmi_sdr:
      vals = sdr_row.split("|")
      vals = map(lambda s: s.strip(), vals)
      ipmi_values_dict[vals[0]]=vals[1]
      ipmi_status_dict[vals[0]]=vals[2]
    SimpleLoad('hp.ilo.temp.inlet',ipmi_values_dict["01-Inlet Ambient"].strip(" degrees C"))
    SimpleLoad('hp.ilo.temp.cpu',ipmi_values_dict["02-CPU"].strip(" degrees C"))
    SimpleLoad('hp.ilo.temp.dimm',ipmi_values_dict["03-P1 DIMM 1-2"].strip(" degrees C"))
    SimpleLoad('hp.ilo.temp.chipset',ipmi_values_dict["05-Chipset"].strip(" degrees C"))
    SimpleLoad('hp.ilo.temp.chipsetzone',ipmi_values_dict["06-Chipset Zone"].strip(" degrees C"))
    SimpleLoad('hp.ilo.temp.vrzone',ipmi_values_dict["07-VR P1 Zone"].strip(" degrees C"))
    SimpleLoad('hp.ilo.temp.ilozone',ipmi_values_dict["09-iLO Zone"].strip(" degrees C"))
    SimpleLoad('hp.ilo.temp.pci',ipmi_values_dict["10-PCI 1"].strip(" degrees C"))
    SimpleLoad('hp.ilo.temp.pcizone',ipmi_values_dict["11-PCI 1 Zone"].strip(" degrees C"))
    SimpleLoad('hp.ilo.temp.exhaust',ipmi_values_dict["12-Sys Exhaust"].strip(" degrees C"))
    SimpleLoad('hp.ilo.fan.rpm',ipmi_values_dict["Fan 1"].strip(" percent"))
#    print json.dumps(ipmi_values_dict, sort_keys=True, indent=4)
#    print json.dumps(ipmi_status_dict, sort_keys=True, indent=4)
        


  # sleep before a new batch of data
  time.sleep(60)

# close the socket  
sock.close()


#session = netsnmp.Session(DestHost='localhost', Version=2, Community='public')
#vars = netsnmp.VarList(netsnmp.Varbind('sysDescr', '0'))
#session.get(vars)










#write
#var = netsnmp.Varbind('enterprises', '318.1.1.4.4.2.1.3.5', '1', 'INTEGER')
#res = netsnmp.snmpset(var, Version = 1, DestHost='192.168.2.3', Community='writecommunity')
                