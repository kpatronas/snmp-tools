#!/usr/bin/env python
import sys
import netsnmp
from prettytable import PrettyTable
from optparse import OptionParser

# Check if port is in the range of 1-65535
def IsPortValid(option, opt_str, value, parser):
    if (value <= 0 or value >65535):
        parser.values.snmp_port = 161
        print("snmp port must be in range of 1-6535, defaulting to '161'")
    else:
        parser.values.snmp_port = value

help = """%prog [-d <destination>] [-p <port>] [-c <community>] [-s <snmp-version>]
Description: Returns the average cpu load of a linux host for 1, 5, 15 minutes.
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
        help    = "SNMP version, defaults to '1', possible values [1,2,2c]")
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
        # SNMP Get the CPU load OIDs
        cpu_load_vars = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.4.1.2021.10.1.3.1'), # 1  Min CPU Load
                                        netsnmp.Varbind('.1.3.6.1.4.1.2021.10.1.3.2'), # 5  Min CPU Load
                                        netsnmp.Varbind('.1.3.6.1.4.1.2021.10.1.3.3')) # 15 Min CPU Load
        cpu_load_res = session.get(cpu_load_vars)
        if (session.ErrorStr):
            print ('Error occurred during SNMP query: '+session.ErrorStr)
            sys.exit(2)
        x = PrettyTable(["1 Min", "5 Min", "15 Min"])
        x.border = False
        x.align["1 Min Avg CPU Load"] = "l"
        x.add_row([str(cpu_load_res[0]),str(cpu_load_res[1]),str(cpu_load_res[2])])
        print(x)
    except Exception as exception_error:
        print ('Error occurred during executing script: '+exception_error)
        sys.exit(2)
        
if __name__ == "__main__":
    main()
