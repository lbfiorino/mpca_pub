#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, subprocess
import ipaddress

def create_namespace_macvlan(IP, IFACE, NAME, NETMASK_PREFIX, ROUTE, TARGET_SERVER=None):
    # print(ipaddress.IPv4Address(ip_int))
    NS = f"{NAME}_{IP}"
    # NS = IP
    CMD1 = f"ip netns add {NS}"
    CMD2 = f"ip link add macv0 link {IFACE} type macvlan mode bridge"
    CMD3 = f"ip link set macv0 promisc on"
    CMD4 = f"ip link set macv0 netns {NS}"
    CMD5 = f"ip netns exec {NS} ip addr add {IP}/{NETMASK_PREFIX} brd + dev macv0"
    CMD6 = f"ip netns exec {NS} ip link set macv0 up"
    CMD7 = f"ip netns exec {NS} ip link set lo up"
    CMD8 = f"ip netns exec {NS} route add -net {ROUTE} dev macv0"
    # print(CMD1)
    # print(CMD2)
    # print(CMD3)
    # print(CMD4)
    # print(CMD5)
    # print(CMD6)
    # print(CMD7)
    # print(CMD8)

    # os.system(CMD1)
    # os.system(CMD2)
    # os.system(CMD3)
    # os.system(CMD4)
    # os.system(CMD5)
    # os.system(CMD6)
    # os.system(CMD7)
    # os.system(CMD8)
    
    GET_MAC_CMD = ""
    ns_mac = ""
    target_server_mac = ""
    try:
        subprocess.run(CMD1, shell=True, check=True)
        subprocess.run(CMD2, shell=True, check=True)
        subprocess.run(CMD3, shell=True, check=True)
        subprocess.run(CMD4, shell=True, check=True)
        subprocess.run(CMD5, shell=True, check=True)
        subprocess.run(CMD6, shell=True, check=True)
        subprocess.run(CMD7, shell=True, check=True)
        subprocess.run(CMD8, shell=True, check=True)

        GET_NS_MAC_CMD = f"ip netns exec {NS} cat /sys/class/net/macv0/address"
        ns_mac = subprocess.getoutput(GET_NS_MAC_CMD)

        if TARGET_SERVER:
            PING_CMD = f"ip netns exec {NS} ping -c 2 -W 1 {TARGET_SERVER}"
            subprocess.run(PING_CMD, shell=True, check=True, stdout=subprocess.DEVNULL)

            GET_TARGET_MAC_CMD = f"ip netns exec {NS} arp -an {TARGET_SERVER} | cut -d ' ' -f4"
            target_server_mac = subprocess.getoutput(GET_TARGET_MAC_CMD)
            #print(TARGET_SERVER, target_server_mac)


        # print(f"{'Namespace:':>10}{bcolors.OKCYAN} {NS} {bcolors.ENDC}")
        # print(f"{'Interface:':>10}{bcolors.OKCYAN} macv0 {bcolors.ENDC}")
        # print(f"{'IP:':>10}{bcolors.OKCYAN} {IP} {bcolors.ENDC}")
        # print("\n")

    except Exception as e:
        print(e)

    if TARGET_SERVER:
        return NS, "macv0", ns_mac, target_server_mac
    else:
        return NS, "macv0"