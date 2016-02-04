#!/usr/bin/python

import netsnmp
import time
import socket

# monitored host settings
HOST='127.0.0.1'
SNMP_COMMUNITY='public'
SNMP_VERSION=2

# change this array to match your network interface index numbers
INTERFACE_ID=(2,3)

# change to your Carbon server hostname and port
CARBON_SERVER='deb3'
CARBON_PORT=2003

# open Carbon socket and keep it open while pushing data
sock = socket.socket()
sock.connect((CARBON_SERVER, CARBON_PORT))

while True:
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
    if_hc_in_val = netsnmp.snmpget(netsnmp.Varbind(if_hc_in), Version = SNMP_VERSION, DestHost = HOST, Community=SNMP_COMMUNITY)
    if_hc_out_val = netsnmp.snmpget(netsnmp.Varbind(if_hc_out), Version = SNMP_VERSION, DestHost = HOST, Community=SNMP_COMMUNITY)
    if_name_val = netsnmp.snmpget(netsnmp.Varbind(if_name), Version = SNMP_VERSION, DestHost = HOST, Community=SNMP_COMMUNITY)
    if_adm_status_val = netsnmp.snmpget(netsnmp.Varbind(if_admin_status), Version = SNMP_VERSION, DestHost = HOST, Community=SNMP_COMMUNITY)
    if_op_status_val = netsnmp.snmpget(netsnmp.Varbind(if_op_status), Version = SNMP_VERSION, DestHost = HOST, Community=SNMP_COMMUNITY)
    
    # start building messages
    message_hc_in = 'hp.if.' + if_name_val[0] + '.in ' + if_hc_in_val[0] + ' %d\n' % int(time.time())
    message_hc_out = 'hp.if.' + if_name_val[0] + '.out ' + if_hc_out_val[0] + ' %d\n' % int(time.time())
    message_adm_stat = 'hp.if.' + if_name_val[0] + '.status.adm ' + if_adm_status_val[0] + ' %d\n' % int(time.time())
    message_op_stat = 'hp.if.' + if_name_val[0] + '.status.oper ' + if_op_status_val[0] + ' %d\n' % int(time.time())  
    print 'sending message:\n%s' % message_hc_in
    sock.sendall(message_hc_in)
    print 'sending message:\n%s' % message_hc_out
    sock.sendall(message_hc_out)
    print 'sending message:\n%s' % message_adm_stat
    sock.sendall(message_adm_stat)
    print 'sending message:\n%s' % message_op_stat
    sock.sendall(message_op_stat)

  # sleep before a new batch of data
  time.sleep(10)

# close the socket  
sock.close()


#session = netsnmp.Session(DestHost='localhost', Version=2, Community='public')
#vars = netsnmp.VarList(netsnmp.Varbind('sysDescr', '0'))
#session.get(vars)










#write
#var = netsnmp.Varbind('enterprises', '318.1.1.4.4.2.1.3.5', '1', 'INTEGER')
#res = netsnmp.snmpset(var, Version = 1, DestHost='192.168.2.3', Community='writecommunity')
                