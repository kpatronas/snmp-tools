#!/usr/bin/env python
import sys
import netsnmp
import math
from prettytable import PrettyTable
from optparse import OptionParser

disk_mount_path  = ".1.3.6.1.4.1.2021.9.1.2"
disk_part_path   = ".1.3.6.1.4.1.2021.9.1.3"
total_size       = ".1.3.6.1.4.1.2021.9.1.6"
avail_size       = ".1.3.6.1.4.1.2021.9.1.7"
used_size        = ".1.3.6.1.4.1.2021.9.1.8"
used_size_perc   = ".1.3.6.1.4.1.2021.9.1.9"
used_inodes_perc = ".1.3.6.1.4.1.2021.9.1.10"

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
Description: Returns the disk statistics of a linux host.
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

        disk_mount_path  = ".1.3.6.1.4.1.2021.9.1.2"
        disk_part_path   = ".1.3.6.1.4.1.2021.9.1.3"
        total_size       = ".1.3.6.1.4.1.2021.9.1.6"
        avail_size       = ".1.3.6.1.4.1.2021.9.1.7"
        used_size        = ".1.3.6.1.4.1.2021.9.1.8"
        used_size_perc   = ".1.3.6.1.4.1.2021.9.1.9"
        used_inodes_perc = ".1.3.6.1.4.1.2021.9.1.10"

        # SNMP Get the CPU load OIDs
        disk_mount_path_vars = netsnmp.VarList(netsnmp.Varbind(disk_mount_path))
        disk_part_path_vars  = netsnmp.VarList(netsnmp.Varbind(disk_part_path))
        total_size_vars      = netsnmp.VarList(netsnmp.Varbind(total_size))
        avail_size_vars      = netsnmp.VarList(netsnmp.Varbind(avail_size))
        used_size_vars       = netsnmp.VarList(netsnmp.Varbind(used_size))
        used_size_perc_vars  = netsnmp.VarList(netsnmp.Varbind(used_size_perc))
        used_size_perc_vars  = netsnmp.VarList(netsnmp.Varbind(used_inodes_perc))

        disk_mount_path_res   = session.walk(disk_mount_path_vars)
        disk_part_path_res    = session.walk(disk_part_path_vars)
        total_size_res        = session.walk(total_size_vars)
        avail_size_res        = session.walk(avail_size_vars)
        used_size_res         = session.walk(used_size_vars)
        used_size_perc_res    = session.walk(used_size_perc_vars)
        used_size_perc_res    = session.walk(used_size_perc_vars)

        if (session.ErrorStr):
            print ('Error occurred during SNMP query: '+session.ErrorStr)
            sys.exit(2)
        i = 0
        x = PrettyTable(["Mount Point", "Partition", "Total Size", "Used Size"])
        x.border = False
        x.align["Mount Point"] = "l"
        for path in disk_mount_path_res:
            if "/" in str(disk_part_path_res[i]):
                x.add_row([path,str(disk_part_path_res[i]), convertSize((int(total_size_res[i]))),convertSize((int(used_size_res[i])))])
            i=i+1
        print(x)
    except Exception as exception_error:
        print ('Error occurred during executing script: '+str(exception_error))
        sys.exit(2)
        
if __name__ == "__main__":
    main()
