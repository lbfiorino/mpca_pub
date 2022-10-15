#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import subprocess
import resource
from datetime import datetime, timezone
import sys, os, signal, fnmatch
import ipaddress, netifaces
from createnamespace import create_namespace_macvlan


# Set open files (ulimit -n 50000)
resource.setrlimit(resource.RLIMIT_NOFILE, (50000, 50000))
# Set stack size (ulimit -s 65536)
resource.setrlimit(resource.RLIMIT_STACK, (67108864, 67108864))


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ERR = '\033[31m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ITALIC = '\x1B[3m'
    PASS = OKGREEN + BOLD
    OKMSG = BOLD + OKGREEN + u'\u2705' + "  "
    ERRMSG = BOLD + FAIL + u"\u274C" + "  "
    WAITMSG = BOLD + HEADER + u'\u231b' + "  "


# In command line
# GOR_BIN = "gor1.2.0"
# GOR_BIN = "gor1.3.3"

# Get current dir
current_dir = os.getcwd()
absolute_path = os.path.abspath(__file__)
script_name = os.path.basename(__file__)
script_dir = absolute_path[0:-(len(script_name))]


#This script must be run as root!
if not os.geteuid()==0:
    sys.exit(bcolors.BOLD+"[WARNING] "+bcolors.ENDC+bcolors.WARNING+"This script must be run as root!"+bcolors.ENDC+"\n")


# Parser command-line options
parser = argparse.ArgumentParser()
parser.add_argument("-g", "--gor-bin", dest='gor_bin', help="GoReplay version [gor1.2.0 | gor1.3.3].", required=True)
parser.add_argument("-s", "--start-time", dest='start_time', help="Time do start in 24h format (08:10:00, 14:20:00...).", required=True)
parser.add_argument("-t", "--target-server", dest='target_server', help="IP Target Web Server.", required=True)
parser.add_argument("-d", "--gor-files-dir", dest='gor_files_dir', help="Directory with .gor files to replay.", required=True)
parser.add_argument("-i", "--interface", dest='iface', help="Physical Network interface.", required=True)
parser.add_argument("-n", "--namespace-name", dest='namespace_name', help="Namespace Name (default=mpca).", default="mpca")
parser.add_argument("-a", "--initial-ip", dest='initial_ip', help="Initial Replay IP Addresss. Will be create one namespace for each gor file with ips in sequence.", default="10.50.10.11", required=True)
parser.add_argument("-m", "--netmask-prefix", dest='netmask', help="Replay Network Mask Prefix.", required=True)
parser.add_argument("-r", "--route", dest='cloud_net', help="CIDR Cloud Network to add route (Ex.: 10.50.1.0/24).", default="10.50.1.0/24", required=True)
if len(sys.argv)==1:
     parser.print_help(sys.stderr)
     print("\n")
     exit(1)
args = parser.parse_args()


# Check if network interface exist
interfaces = netifaces.interfaces()
if (not args.iface in interfaces):
    sys.exit(bcolors.BOLD+"[FAIL]"+bcolors.ENDC+bcolors.FAIL+" Invalid network interface!"+bcolors.ENDC+"\n")

# UP Network Interface
subprocess.run(f"ip link set dev {args.iface} up", shell=True)

GOR_FILES_DIR=os.path.realpath(args.gor_files_dir)
GOR_BIN = args.gor_bin

# Create new process group to kill all process in group
os.setpgrp()
# Processes
proc = []

ns_list = []
replay_ip=ipaddress.ip_address(args.initial_ip)

# Log, create log dir if not exists
logfile = os.path.join(script_dir, "logs/goreplay", script_name+".log")
if not os.path.exists(os.path.dirname(logfile)):
    os.makedirs(os.path.dirname(logfile))

# Delete old logs if exists
subprocess.run(f"rm -f {os.path.dirname(logfile)}/*.log", shell=True)

f = open(logfile, "w")
utc_dt = datetime.now(timezone.utc) # UTC time
dt = utc_dt.astimezone() # local time
f.write("------------------------------------------------------------------------------------------------\n")
f.write(f"REPLAY NORMAL HTTP (GOREPLAY {GOR_BIN})\n")
f.write(f"       UTC: {utc_dt}\n")
f.write(f"Local Time: {dt}\n")
f.write("------------------------------------------------------------------------------------------------\n\n")
try:
    for file in os.listdir(GOR_FILES_DIR):
        if file.endswith(".gor"):
            # Create Namespaces
            ns_name, ns_iface = create_namespace_macvlan(IP=str(replay_ip), IFACE=args.iface, NAME=args.namespace_name, NETMASK_PREFIX=args.netmask, ROUTE=args.cloud_net)
            ns_list.append(ns_name)

            # Ping Target Server
            PING_CMD = f"ip netns exec {ns_name} ping -c 2 -W 1 {args.target_server}"
            subprocess.run(PING_CMD, shell=True, check=True, stdout=subprocess.DEVNULL)

            CMD_GOREPLAY = f"sleep $(( $(date -d {args.start_time} +%s) - $(date +%s) )) ; ip netns exec {ns_name} {GOR_BIN} --verbose 1 --stats --input-file {os.path.join(GOR_FILES_DIR, file)} --output-http \"http://{args.target_server}\""
            proc.append(subprocess.Popen(CMD_GOREPLAY, shell=True, executable='/bin/bash', preexec_fn=os.setsid))
            
            print("\n")
            print(bcolors.BOLD+"     Namespace:"+bcolors.ENDC+f" {ns_name}")
            print(bcolors.BOLD+"Replay Command:"+bcolors.ENDC+f" {CMD_GOREPLAY}")

            f.write(f"GoReplay file {file}\n")
            f.write(f"\t     Namespace: {ns_name}\n")
            f.write(f"\tReplay Command: {CMD_GOREPLAY}\n\n")

        replay_ip+=1

    f.close()
    print("\n--------------------------------------------------------")
    print(f"GoReplay version: {GOR_BIN}")
    print(f"LOG Files: {os.path.dirname(logfile)}")
    print(bcolors.BOLD+"[WARNING] "+bcolors.ENDC+bcolors.WARNING+"Copy GoReplay processes outputs!"+bcolors.ENDC)
    print("--------------------------------------------------------")    
    print("\nPress CTRL+C to exit...")
    while(True):
        input()

except KeyboardInterrupt:

    # Kill all GoReplay processes
    for p in proc:
        p.kill()    
    subprocess.run(f"pkill {GOR_BIN}", shell=True)

    # Del namespaces
    print("")
    for ns in ns_list:
        print(f"{bcolors.FAIL}Removing namespace:{bcolors.ENDC} {ns}...")
        subprocess.run(f"ip netns del {ns}", shell=True)
    
    print("\n"+bcolors.WARNING + "Killing the processes..." + bcolors.ENDC)
    # Kill all processes in group
    os.killpg(0, signal.SIGKILL)