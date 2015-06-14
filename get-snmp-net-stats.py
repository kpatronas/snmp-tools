#!/usr/bin/env python
import sys
import netsnmp
import time
import math
from prettytable import PrettyTable
from optparse import OptionParser

def PortStatus(status):
    status = int(status)
    if status == 1:
        return "up"
    if status == 2:
        return "down"
    if status == 3:
        return "testing"
    if status == 4:
        return "unknow"
    if status == 5:
        return "dormant"
    if status == 6:
        return "notPresent"
    if status == 7:
        return "lowerLayerDown"

def convertSize(size):
    size_name = ("B","KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size,1024)))
    p = math.pow(1024,i)
    s = round(size/p,2)
    if (s > 0):
        return '%s %s' % (s,size_name[i])
    else:
        return '0B'

# Check if port is in the range of 1-65535
def IsPortValid(option, opt_str, value, parser):
    if (value <= 0 or value >65535):
        parser.values.snmp_port = 161
        print("snmp port must be in range of 1-6535, defaulting to '161'")
    else:
        parser.values.snmp_port = value

help = """%prog [-d <destination>] [-p <port>] [-c <community>] [-s <snmp-version>]
Description: Returns the network statistics of a linux host.
Copyright 2015, Konstantinos Patronas, Email: kpatronas@gmail.com"""

def main():
    # Parse the command line options
    parser = OptionParser(usage = help,version = "%prog 1.0")
    parser.add_option("-d", "--destination",
        action  = "store",
        type    = "string",
        dest    = "snmp_destination",
        default = "127.0.0.1",
        help    = "destination to query, defaults to 127.0.0.1")
    parser.add_option("-p", "--port",
        action  = "callback",
        type    = "int",
        dest    = "snmp_port",
        callback = IsPortValid,
        default = 161,
        help    = "SNMP port, defaults to '161'")
    parser.add_option("-c", "--community",
        action  = "store",
        type    = "string",
        dest    = "snmp_community",
        default = "public",
        help    = "community string, default to 'public'")
    parser.add_option("-s", "--snmp-version",
        action  = "store",
        type    = "choice",
        choices = ("1","2"),
        dest    = "snmp_version",
        default = "1",
        help    = "SNMP version, defaults to '1', possible values [1,2]")
    (options, args) = parser.parse_args()
    try:
        snmp_hostname   = options.snmp_destination  # string
        snmp_port       = int(options.snmp_port)    # integer
        snmp_community  = options.snmp_community    # string
        snmp_version    = int(options.snmp_version) # string
        # Create the session object
        session = netsnmp.Session(DestHost   = snmp_hostname,
                                  Version    = snmp_version,
                                  Community  = snmp_community,
                                  RemotePort = snmp_port)

        ifDescr             = ".1.3.6.1.2.1.2.2.1.2"                # Description of the IP interface
        ifType              = ".1.3.6.1.2.1.2.2.1.3"                # Type of the interface
        ifInOctets          = ".1.3.6.1.2.1.2.2.1.10"               # The total number of octets received on the interface,including framing characters.
        ifOutOctets         = ".1.3.6.1.2.1.2.2.1.16"               # The total number of octets transmitted out of the interface, including framing characters.
        ifPhysAddress       = ".1.3.6.1.2.1.2.2.1.6"                # Get the MAC address
        ifAdminStatus       = ".1.3.6.1.2.1.2.2.1.7"                # The desired state of the interface 1: Up 2: Down 3: Test
        ifOperStatus        = ".1.3.6.1.2.1.2.2.1.8"                # The current operational state of the interface. 1: Up 2: Down 3: Test

        # SNMP Get the CPU load OIDs
        ifDescr_vars            = netsnmp.VarList(netsnmp.Varbind(ifDescr))
        ifType_vars             = netsnmp.VarList(netsnmp.Varbind(ifType))
        ifInOctets_vars         = netsnmp.VarList(netsnmp.Varbind(ifInOctets))
        ifOutOctets_vars        = netsnmp.VarList(netsnmp.Varbind(ifOutOctets))
        ifPhysAddress_vars      = netsnmp.VarList(netsnmp.Varbind(ifPhysAddress))
        ifAdminStatus_vars      = netsnmp.VarList(netsnmp.Varbind(ifAdminStatus))
        ifOperStatus_vars       = netsnmp.VarList(netsnmp.Varbind(ifOperStatus))

        ifDescr_res             = session.walk(ifDescr_vars)
        ifType_res              = session.walk(ifType_vars)
        ifInOctets_res          = session.walk(ifInOctets_vars)
        ifOutOctets_res         = session.walk(ifOutOctets_vars)
        ifPhysAddress_res       = session.walk(ifPhysAddress_vars)
        ifAdminStatus_res       = session.walk(ifAdminStatus_vars)
        ifOperStatus_res        = session.walk(ifOperStatus_vars)

        if (session.ErrorStr):
            print ('Error occurred during SNMP query: '+session.ErrorStr)
            sys.exit(2)
        i = 0
        x = PrettyTable(["Interface Description","Total-In","Total-Out","Admin Status","Operational Status"])
        x.border = False
        x.align["Interface Description"] = "l"
        for ifDescr_str in ifDescr_res:
            if (int(ifInOctets_res[i]) != 0 and int(ifOutOctets_res[i]) != 0):
                x.add_row([ifDescr_str,convertSize(int(ifInOctets_res[i])),convertSize(int(ifOutOctets_res[i])),PortStatus(ifAdminStatus_res[i]),PortStatus(ifOperStatus_res[i])])
            i=i+1
        print(x)
    except Exception as exception_error:
        print ('Error occurred during executing script: '+str(exception_error))
        sys.exit(2)
        
if __name__ == "__main__":
    main()
