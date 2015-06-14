#!/usr/bin/env python
import sys
import datetime
import netsnmp
from optparse import OptionParser

uptime_oid  = ".1.3.6.1.2.1.1.3.0"

def to_hhmmss(s):
    return "%d:%02d:%02d.%03d" % \
        reduce(lambda a,b : divmod(a[0],b) + a[1:], [(s*1000,),1000,60,60])

# Check if port is in the range of 1-65535
def IsPortValid(option, opt_str, value, parser):
    if (value <= 0 or value >65535):
        parser.values.snmp_port = 161
        print("snmp port must be in range of 1-6535, defaulting to '161'")
    else:
        parser.values.snmp_port = value

help = """%prog [-d <destination>] [-p <port>] [-c <community>] [-s <snmp-version>]
Description: Returns the uptime of a linux host.
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
                                  UseNumeric = True,
                                  Community  = snmp_community,
                                  RemotePort = snmp_port)
        # SNMP Get the CPU load OIDs
        uptime_vars = netsnmp.VarList(netsnmp.Varbind(uptime_oid))
        uptime_res   = session.get(uptime_vars)

        if (session.ErrorStr):
            print ('Error occurred during SNMP query: '+session.ErrorStr)
            sys.exit(2)
        print("Uptime: "+str(datetime.timedelta(seconds=int(uptime_res[0])/100)))
    except Exception as exception_error:
        print ('Error occurred during executing script: '+str(exception_error))
        sys.exit(2)
        
if __name__ == "__main__":
    main()
