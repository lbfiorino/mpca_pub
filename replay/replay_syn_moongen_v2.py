#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys, os, signal
import subprocess
from datetime import datetime, timezone
from glob import glob
import ipaddress, netifaces
from scapy.all import *
from createnamespace import create_namespace_macvlan


MOONGEN_DIR="/home/lucianobf/MoonGen"
DPDKDEVBIND="/home/lucianobf/dpdk-stable-19.11.9/usertools/dpdk-devbind.py"
IFACE_LINUX_DRIVER="bnxt_en"


# Get current dir
current_dir = os.getcwd()
absolute_path = os.path.abspath(__file__)
script_name = os.path.basename(__file__)
script_dir = absolute_path[0:-(len(script_name))]


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
    sys.exit(bcolors.BOLD+"[WARNING] "+bcolors.ENDC+bcolors.WARNING+"This script must be run as root!"+bcolors.ENDC+"\n")


# Get working directory
current_dir = os.getcwd()

# Parser command-line options
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--start-time", dest='start_time', help="Time do start in 24h format (08:10:00, 14:20:00...).", required=True)
parser.add_argument("-t", "--target-server", dest='target_server', help="Target Web Server.", required=True)
parser.add_argument("-p", "--pcaps-dir", dest='pcaps_dir', help="Directory with PCAP files to replay.", required=True)
parser.add_argument("-i", "--interface", dest='iface', help="Network interface.", required=True)
parser.add_argument("-n", "--namespace-name", dest='namespace_name', help="Namespace Name (default=mpca).", default="mpca")
parser.add_argument("-a", "--initial-ip", dest='initial_ip', help="Initial Replay IP Addresss. Will be create one namespace for each pcap file.", default="10.50.10.123", required=True)
parser.add_argument("-m", "--netmask-prefix", dest='netmask', help="Network Replay Mask Prefix.", required=True)
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


PCAP_DIR = os.path.realpath(args.pcaps_dir)
# Enter pcap dir
os.chdir(PCAP_DIR)
cwd = os.getcwd()

ns_list = []
pcap_filter="*.pcap"

# Create new process group to kill all process in group
os.setpgrp()
# Processes
proc = []

replay_ip=ipaddress.ip_address(args.initial_ip)
replay_files = []

# Log, create log dir if not exists
logfile = os.path.join(script_dir, "logs/moongen", script_name+".log")
if not os.path.exists(os.path.dirname(logfile)):
    os.makedirs(os.path.dirname(logfile))

# Delete old logs if exists
subprocess.run(f"rm -f {os.path.dirname(logfile)}/*.log", shell=True)

f = open(logfile, "w")
utc_dt = datetime.now(timezone.utc) # UTC time
dt = utc_dt.astimezone() # local time
f.write("------------------------------------------------------------------------------------------------\n")
f.write("REPLAY SYN-FLOOD ATTACK (MOONGEN)\n")
f.write(f"       UTC: {utc_dt}\n")
f.write(f"Local Time: {dt}\n")
f.write("------------------------------------------------------------------------------------------------\n\n")
try:
    for pcap in glob(pcap_filter):
        
        # Create namespace for client
        ns_name, ns_iface, ns_mac, target_server_mac = create_namespace_macvlan(IP=str(replay_ip), IFACE=args.iface, NAME=args.namespace_name, NETMASK_PREFIX=args.netmask, ROUTE=args.cloud_net, TARGET_SERVER=args.target_server)
        ns_list.append(ns_name)
        #print(ns_name, ns_iface, ns_mac)

        # Edit PCAP IP/MAC
        replay_pcap = f"{PCAP_DIR}/{replay_ip}.pcap"
        replay_files.append(replay_pcap)
        CMD_TCPREWRITE = f"tcprewrite --fixcsum --dstipmap=0.0.0.0/0:{args.target_server} --srcipmap=0.0.0.0/0:{replay_ip} --enet-dmac={target_server_mac} --enet-smac={ns_mac} --infile={PCAP_DIR}/{pcap} --outfile={replay_pcap}"
        #print(CMD_TCPREWRITE)
        subprocess.run(CMD_TCPREWRITE, shell=True, check=True)

        replay_ip+=1

        print("\n")
        print(bcolors.BOLD+"PCAP Original:"+bcolors.ENDC+f" {pcap}")
        print(bcolors.BOLD+"  PCAP Replay:"+bcolors.ENDC+f" {replay_pcap}")
        print(bcolors.BOLD+"    Namespace:"+bcolors.ENDC+f" {ns_name}")   

        f.write(f"PCAP Original: {pcap}\n")
        f.write(f"\t    Namespace: {ns_name}\n")
        f.write(f"\tPCAP modified: {replay_pcap}\n\n")


    # Del namespaces
    print("")
    for ns in ns_list:
        #print(f"{bcolors.FAIL}Removing namespace:{bcolors.ENDC} {ns}...")
        subprocess.run(f"ip netns del {ns}", shell=True)

    # Merge pcaps to replay
    replay_pcap_merged = f"{PCAP_DIR}/moongen_replay.pcap"
    CMD_MERGE_PCAPS = f"mergecap -F pcap -w {replay_pcap_merged} {' '.join(replay_files)}"
    print(f"\n{bcolors.BOLD}Merge pcaps:{bcolors.ENDC} {CMD_MERGE_PCAPS}")
    subprocess.run(CMD_MERGE_PCAPS, shell=True, check=True)
    replay_files.append(replay_pcap_merged)

    f.write(f"\n\nPCAP Replay (Merged): {replay_pcap_merged}\n")

    # LOAD VFIO-PCI KERNEL DRIVER
    print(f"\n{bcolors.OKCYAN}Loading vfio-pci kernel driver (no-IOMMU mode)...{bcolors.ENDC}")
    subprocess.run("modprobe vfio-pci", shell=True, check=True)
    # VFIO no-IOMMU mode
    subprocess.run("echo 1 > /sys/module/vfio/parameters/enable_unsafe_noiommu_mode", shell=True, check=True)

    # DPDK DEV BIND
    # Get PCI BUS from iface name --> basename $(realpath /sys/class/net/<IFACE>/device)
    iface_pci_bus = subprocess.getoutput(f"basename $(realpath /sys/class/net/{args.iface}/device)")
    print(f"{bcolors.OKCYAN}Binding NIC to vfio-pci driver...{bcolors.ENDC}")
    subprocess.run(f"python3 {DPDKDEVBIND} -b vfio-pci {iface_pci_bus}", shell=True, check=True)

    CMD_MOONGEN = f"sleep $(( $(date -d {args.start_time} +%s) - $(date +%s) )) ; {MOONGEN_DIR}/build/MoonGen {MOONGEN_DIR}/examples/pcap/replay-pcap.lua -s 30 -r 1 0 {replay_pcap_merged}"
    #print(f"\n{CMD_MOONGEN}")
    moongen_proc = subprocess.Popen(CMD_MOONGEN, shell=True, executable='/bin/bash', preexec_fn=os.setsid)
 
    f.close()
    print("\n--------------------------------------------------------")   
    print(f"                 {bcolors.BOLD}NIC:{bcolors.ENDC} {args.iface}")
    print(f"         {bcolors.BOLD}NIC PCI BUS:{bcolors.ENDC} {iface_pci_bus}")
    print(f"       {bcolors.BOLD}Kernel Driver:{bcolors.ENDC} vfio-pci (no-IOMMU)")
    print(f"{bcolors.BOLD}PCAP Replay (Merged):{bcolors.ENDC} {replay_pcap_merged}")
    print(f"      {bcolors.BOLD}Replay Command:{bcolors.ENDC} {CMD_MOONGEN}\n\n")
    print("--------------------------------------------------------")
    print("\nPress CTRL+C to exit...")
    while(True):
        input()

except KeyboardInterrupt:

    # Kill Moongen process
    moongen_proc.kill()

    # DPDK DEV UNBIND
    subprocess.run(f"python3 {DPDKDEVBIND} -u {iface_pci_bus}", shell=True, check=True)
    # DPDK DEV BIND LINUX DRIVER
    subprocess.run(f"python3 {DPDKDEVBIND} -b {IFACE_LINUX_DRIVER} {iface_pci_bus}", shell=True, check=True)
    # UP LINUX IFACE
    subprocess.run(f"ip link set dev {args.iface} up", shell=True, check=True)

    # Del replay files
    for f in replay_files:
        print(f"{bcolors.FAIL}Removing replay file:{bcolors.ENDC} {f}...")
        os.system(f"rm -f {f}")
        #print(f)
   
    print("\n"+bcolors.WARNING + "Killing the processes..." + bcolors.ENDC)
    # Kill all processes in group
    os.killpg(0, signal.SIGKILL)