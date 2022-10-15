#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys, os, subprocess
import ipaddress


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

#This script must be run as root!
if not os.geteuid()==0:
    sys.exit('This script must be run as root!')


# Get working directory
current_dir = os.getcwd()

	
# Parser command-line options
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--interface", dest='iface', help="Network interface.", required=True)
parser.add_argument("-n", "--namespace-name", dest='namespace', help="Namespace Name (default=mpca).", default="mpca")
parser.add_argument("-s", "--start-addr", dest='start_addr', help="Start IP Address.", required=True)
parser.add_argument("-e", "--end-addr", dest='end_addr', help="End IP Address.", required=True)
parser.add_argument("-m", "--netmask-prefix", dest='netmask', help="Network Mask.", required=True)
parser.add_argument("-r", "--route", dest='target_net', help="CIDR Network to add route (Ex.: 10.50.1.0/24).", required=True)
#parser.add_argument("-g", "--gateway", dest='gateway', help="Network Gateway.", required=True)
if len(sys.argv)==1:
     parser.print_help(sys.stderr)
     print("\n")
     exit(1)
args = parser.parse_args()

START_IP =  ipaddress.IPv4Address(args.start_addr)
END_IP = ipaddress.IPv4Address(args.end_addr)


print(f"{bcolors.HEADER}Creating MACVLAN namespaces...{bcolors.ENDC}")
for k, ip_int in enumerate(range(int(START_IP), int(END_IP)+1)):
	# print(ipaddress.IPv4Address(ip_int))
	IP = ipaddress.IPv4Address(ip_int)
	NS = f"{args.namespace}{str(k).zfill(3)}"
	# NS = IP
	CMD1 = f"ip netns add {NS}"
	CMD2 = f"ip link add macv0 link {args.iface} type macvlan mode bridge"
	CMD3 = f"ip link set macv0 promisc on"
	CMD4 = f"ip link set macv0 netns {NS}"
	CMD5 = f"ip netns exec {NS} ip addr add {IP}/{args.netmask} brd + dev macv0"
	CMD6 = f"ip netns exec {NS} ip link set macv0 up"
	CMD7 = f"ip netns exec {NS} ip link set lo up"
	CMD8 = f"ip netns exec {NS} route add -net {args.target_net} dev macv0"
	# print(CMD1)
	# print(CMD2)
	# print(CMD3)
	# print(CMD4)
	# print(CMD5)
	# print(CMD6)
	# print(CMD7)
	# print(CMD8)
	
	os.system(CMD1)
	os.system(CMD2)
	os.system(CMD3)
	os.system(CMD4)
	os.system(CMD5)
	os.system(CMD6)
	os.system(CMD7)
	os.system(CMD8)
	print(f"{'Namespace:':>10}{bcolors.OKCYAN} {NS} {bcolors.ENDC}")
	print(f"{'Interface:':>10}{bcolors.OKCYAN} macv0 {bcolors.ENDC}")
	print(f"{'IP:':>10}{bcolors.OKCYAN} {IP} {bcolors.ENDC}")
	print("\n")

    
