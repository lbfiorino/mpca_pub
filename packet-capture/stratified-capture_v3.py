#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse, configparser
import shlex, subprocess
import sys, os, signal, psutil
import ipaddress


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# This script must be run as root!
if not os.geteuid()==0:
    sys.exit(bcolors.BOLD+"[WARNING] "+bcolors.ENDC+bcolors.WARNING+"This script must be run as root!"+bcolors.ENDC+"\n")


# Get working directory
current_dir = os.getcwd()
script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)

# Parser command-line options
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config-file", dest='config_file', help="Network interface (default: capture.ini).", default=script_dir+"/capture.ini")
parser.add_argument("-i", "--interface", dest='iface', help="Network interface.", required=True)
parser.add_argument("-t", "--traffic-type", dest='traffic_type', help="Traffic type [-t section_name | -t all].  Section name in capture.ini or all.", required=True)
parser.add_argument("-o", "--out-dir", dest='out_dir', help="Directory to save pcap files (defalt: current dir).", default=current_dir)
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    print("")
    print("Suggested directory structure for easier labeling:")
    print("  .")
    print("  └── pcaps/")
    print("      ├── test/")
    print("      │   ├── attack-getflood/")
    print("      │   ├── attack-synflood/")
    print("      │   └── normal-http/")
    print("      └── train/")
    print("          ├── attack-getflood/")
    print("          ├── attack-synflood/")
    print("          └── normal-http/")
    print("")
    exit(1)
args = parser.parse_args()

# Create new process group to kill all process in group
os.setpgrp()
# Processes
proc = []

# Load hosts and servers
captureConfig = configparser.ConfigParser()
captureConfig.read(args.config_file)

# Print config file path
print(f"{bcolors.BOLD} \n[INFO] {bcolors.ENDC}{bcolors.HEADER}Config file: {bcolors.ENDC}{bcolors.BOLD}{os.path.realpath(args.config_file)}{bcolors.ENDC}")
# Print output dir
print(f"{bcolors.BOLD} \n[INFO] {bcolors.ENDC}{bcolors.HEADER}Output dir: {bcolors.ENDC}{bcolors.BOLD}{os.path.realpath(args.out_dir)}{bcolors.ENDC}")

def start_capture(section):
    # Load targets
    targets = []
    for t in captureConfig['targets']:
        # if(t=='range'):
        #     START_IP =  ipaddress.IPv4Address(captureConfig['targets'][t].split('-')[0])
        #     END_IP = ipaddress.IPv4Address(captureConfig['targets'][t].split('-')[1])
        #     for ip_int in range(int(START_IP), int(END_IP)+1):
        #         tip = format(ipaddress.IPv4Address(ip_int))
        #         targets.append(tip)
        if ("range" in t):
            START_IP =  ipaddress.IPv4Address(captureConfig['targets'][t].split('-')[0])
            END_IP = ipaddress.IPv4Address(captureConfig['targets'][t].split('-')[1])
            for ip_int in range(int(START_IP), int(END_IP)+1):
                tip = format(ipaddress.IPv4Address(ip_int))
                targets.append(tip)
        else:
            targets.append(captureConfig['targets'][t])

    #print("Targets: ", targets)

    # Load Section (Attack or Normal)
    hosts = []
    for h in captureConfig[section]:
        # if(h=='range'):
        #     START_IP =  ipaddress.IPv4Address(captureConfig[section][h].split('-')[0])
        #     END_IP = ipaddress.IPv4Address(captureConfig[section][h].split('-')[1])
        #     for ip_int in range(int(START_IP), int(END_IP)+1):
        #         tip = format(ipaddress.IPv4Address(ip_int))
        #         hosts.append(tip)
        if("range" in h):
            START_IP =  ipaddress.IPv4Address(captureConfig[section][h].split('-')[0])
            END_IP = ipaddress.IPv4Address(captureConfig[section][h].split('-')[1])
            for ip_int in range(int(START_IP), int(END_IP)+1):
                tip = format(ipaddress.IPv4Address(ip_int))
                hosts.append(tip)
        else:
            hosts.append(captureConfig[section][h])
    # print("Hosts: ", hosts)

    # Tcpdump commands
    for t in targets:
        target_ip_port = t.split(':')
        if (len(target_ip_port) == 1 and captureConfig['capture']['port']):
            target_ip_port.append(captureConfig['capture']['port'])

        for host in hosts:
            CMD = "tcpdump -n -i "+args.iface+" 'host "+target_ip_port[0]+" and host "+host
            if (captureConfig['capture']['proto']):
                if (captureConfig['capture']['proto'].lower() == 'icmp'):
                    CMD += " and "+captureConfig['capture']['proto'].lower()
                    pcapfile = args.out_dir+'/'+host+"_to_"+target_ip_port[0]+"_"+captureConfig['capture']['proto']+"_"+section+".pcap"
                elif(captureConfig['capture']['proto'].lower() == 'tcp' or captureConfig['capture']['proto'].lower() == 'udp'):
                    CMD += " and "+captureConfig['capture']['proto'].lower()
                    portsep = ''
                    if (len(target_ip_port) == 2):
                        CMD += " port "+target_ip_port[1]
                        portsep = "_port"
                    #pcapfile = args.out_dir+'/'+host+"_to_"+portsep.join(target_ip_port)+"_"+captureConfig['capture']['proto']+"_"+section+".pcap"
                    pcapfile = os.path.join(args.out_dir, host+"_to_"+portsep.join(target_ip_port)+"_"+captureConfig['capture']['proto']+"_"+section+".pcap")


            CMD += "' -U -w "+pcapfile+" 2> /dev/null"
            print("")
            print(CMD)
            # Start tcpdump
            proc.append(subprocess.Popen(CMD, shell=True, executable='/bin/bash', preexec_fn=os.setsid))


# Check if network interface exist
if (args.iface not in psutil.net_if_addrs().keys()):
    print(bcolors.BOLD+"[FAIL] "+bcolors.ENDC+bcolors.FAIL+"Invalid Network Interface.\n"+bcolors.ENDC)
    exit(1)


# Check if output dir is writeable
if not os.access(args.out_dir, os.W_OK):
    print(bcolors.BOLD+"[FAIL] "+bcolors.ENDC+bcolors.FAIL+"Output dir is not writeable.\n"+bcolors.ENDC)
    exit(1)


# Disable NIC Send/Receive Offload
print(bcolors.BOLD+"\n[INFO] "+bcolors.ENDC+bcolors.OKCYAN + "Disabling NIC Send/Receive Offloading " + bcolors.ENDC)
os.system("ethtool -K "+args.iface+" tx off rx off gro off lro off tso off gso off ufo off")

try:
    if (args.traffic_type == "all"):
        for section in  captureConfig.sections():
            if section not in ['capture','targets']:
                start_capture(section)
    else:
        start_capture(args.traffic_type)

    print("\n"+bcolors.BOLD+"[INFO] "+bcolors.ENDC+bcolors.HEADER + "Capturing on "+args.iface+"." + bcolors.ENDC)
    print("\nPress CTRL+C to exit.\n")
    while(True):
        input()

except KeyboardInterrupt:
    print("\n"+bcolors.BOLD+"[WARNING] "+bcolors.ENDC+bcolors.WARNING + "Killing the processes..." + bcolors.ENDC)
  
    # Kill tcpdump processes
    for p in proc:
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)

    # Enable NIC Send/Receive Offload
    print("\n[INFO]"+bcolors.OKCYAN + " Enabling NIC Send/Receive Offloading " + bcolors.ENDC)
    os.system("ethtool -K "+args.iface+" tx on rx on gro on lro on tso on gso on ufo on")

    # Kill all processes in group, including python script
    os.killpg(0, signal.SIGKILL)  

