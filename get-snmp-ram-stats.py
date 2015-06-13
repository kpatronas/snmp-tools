#!/usr/bin/env python
import sys
import math
import netsnmp
from prettytable import PrettyTable
from optparse import OptionParser

# Memory statistics        
total_swap_size       = '.1.3.6.1.4.1.2021.4.3.0'
available_swap_space  = '.1.3.6.1.4.1.2021.4.4.0'
total_ram_in_machine  = '.1.3.6.1.4.1.2021.4.5.0'
total_ram_used        = '.1.3.6.1.4.1.2021.4.6.0'
total_ram_free        = '.1.3.6.1.4.1.2021.4.11.0'
total_ram_shared      = '.1.3.6.1.4.1.2021.4.13.0'
total_ram_buffered    = '.1.3.6.1.4.1.2021.4.14.0'
total_cached_memory   = '.1.3.6.1.4.1.2021.4.15.0'

def convertSize(size):
    size_name = ("KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
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
Description: Returns the memory statistics of a linux host.
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
        
        # SNMP Get the Memory vars
        memory_vars = netsnmp.VarList(netsnmp.Varbind(total_swap_size),
                                      netsnmp.Varbind(available_swap_space),
                                      netsnmp.Varbind(total_ram_in_machine),
                                      netsnmp.Varbind(total_ram_used),
                                      netsnmp.Varbind(total_ram_free),
                                      netsnmp.Varbind(total_ram_shared),
                                      netsnmp.Varbind(total_ram_buffered),
                                      netsnmp.Varbind(total_cached_memory))
        memory_res = session.get(memory_vars)
        if (session.ErrorStr):
            print ('Error occurred during SNMPget: '+session.ErrorStr)
            sys.exit(2)
        x = PrettyTable(["RAM Total", "RAM Free", "Swap Total", "Swap Free"])
        x.border = False
        x.align["Mount Point"] = "l"
        x.add_row([convertSize(int(memory_res[2])),
                   convertSize((int(memory_res[4])+int(memory_res[6])+int(memory_res[7]))-int(memory_res[0])),
                   convertSize(int(memory_res[0])),
                   convertSize(int(memory_res[1]))])
        print(x)
    except Exception as exception_error:
        print ('Error occurred: '+str(exception_error))
        sys.exit(2)
        
if __name__ == "__main__":
    main()
