#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import psutil
import argparse
from scapy.all import *
from datetime import datetime


# Parser dos parametros
parser = argparse.ArgumentParser()
parser.add_argument("-pcap", "--pcap-file", dest='pcapfile', help="Arquivo PCAP.")
parser.add_argument("-srcmac", "--source-mac", dest='srcmac', help="MAC Origen.")
parser.add_argument("-dstmac", "--dest-mac", dest='dstmac', help="MAC Destino.")
parser.add_argument("-srcip", "--source-ip", dest='srcip', help="IP Origen.")
parser.add_argument("-dstip", "--dest-ip", dest='dstip', help="IP Destino.")
args = parser.parse_args()
if len(sys.argv)<=10:
    parser.print_help(sys.stderr)
    print("\n")
    exit(1)


# SRC_MAC = "fa:16:3e:e5:15:92" # VM vm-replaypcap
# SRC_IP = "10.50.1.120" # VM vm-replaypcap
# DST_MAC = "fa:16:3e:ad:26:99" # Roteador da rede no OpenStack ou VM se estiver na mesma rede.
# DST_IP = "10.50.1.97" # Servidor vm-webserver01


print("\nAlterando pacotes para:\n")
print("{:>15} {}".format("SRC-Mac: ", args.srcmac))
print("{:>15} {}".format("SRC-IP: ", args.srcip))
print("{:>15} {}".format("DST-Mac: ", args.dstmac))
print("{:>15} {}".format("DST-IP: ", args.dstip))

# Carrega PCAP original
myreader = PcapReader(args.pcapfile)
# Arquivo PCAP modificado
pcap_mod_file = os.path.splitext(args.pcapfile)[0]+"_mac-ip_mod.pcap"
print("\nPCAP Modificado: "+pcap_mod_file)
print("\n")

count = 0
if os.path.exists(pcap_mod_file):
    os.remove(pcap_mod_file)
while True:
    try:
        packet = myreader.read_packet()

        if Ether in packet:
            packet['Ethernet'].src = args.srcmac
            packet['Ethernet'].dst = args.dstmac
        
        if IP in packet:
            packet['IP'].dst = args.dstip
            packet['IP'].src = args.srcip
            del packet['IP'].chksum
            packet['IP'].chksum = IP(packet['IP'].build()).chksum  ### AJUSTE DE CHECKSUM

        # Salva pacote modificado no novo arquivo PCAP
        wrpcap(pcap_mod_file, packet, append=True)
    except EOFError:
        break
    count += 1