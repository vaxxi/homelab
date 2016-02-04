#!/usr/bin/python

import netsnmp
import time
import socket

interface_id=(2,3)

CARBON_SERVER='deb3'
CARBON_PORT=2003

for i in interface_id:
  if_name="IF-MIB::ifName." + str(i)
  if_octets_in="IF-MIB::ifInOctets." + str(i)
  if_octets_out="IF-MIB::ifOutOctets." + str(i)
  if_hc_in="IF-MIB::ifHCInOctets." + str(i)
  if_hc_out="IF-MIB::ifHCOutOctets." + str(i)
  if_hc_in_val = netsnmp.snmpget(netsnmp.Varbind(if_hc_in), Version = 2, DestHost = '127.0.0.1', Community='public')
  if_hc_out_val = netsnmp.snmpget(netsnmp.Varbind(if_hc_out), Version = 2, DestHost = '127.0.0.1', Community='public')
  if_name_val = netsnmp.snmpget(netsnmp.Varbind(if_name), Version = 2, DestHost = '127.0.0.1', Community='public')
  message_hc_in = 'hp.if.' + if_name_val[0] + '.in ' + if_hc_in_val[0] + ' %d\n' % int(time.time())
  message_hc_out = 'hp.if.' + if_name_val[0] + '.out ' + if_hc_out_val[0] + ' %d\n' % int(time.time())  
  sock = socket.socket()
  sock.connect((CARBON_SERVER, CARBON_PORT))
  print 'sending message:\n%s' % message_hc_in
  sock.sendall(message_hc_in)
  print 'sending message:\n%s' % message_hc_out
  sock.sendall(message_hc_out)
  sock.close()


#session = netsnmp.Session(DestHost='localhost', Version=2, Community='public')
#vars = netsnmp.VarList(netsnmp.Varbind('sysDescr', '0'))
#session.get(vars)










#write
#var = netsnmp.Varbind('enterprises', '318.1.1.4.4.2.1.3.5', '1', 'INTEGER')
#res = netsnmp.snmpset(var, Version = 1, DestHost='192.168.2.3', Community='writecommunity')
                