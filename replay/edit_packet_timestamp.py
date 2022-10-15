#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import psutil
import argparse
from scapy.all import *
from datetime import datetime

# Parser dos parametros
parser = argparse.ArgumentParser()
parser.add_argument("-pcap", "--pcap-file", dest='pcapfile', help="PCAP file.")
parser.add_argument("-tp", "--time-precision", dest='timeprecision', help="Timestamp Precision, in decimal places (Default=3, milliseconds).", default=3)
args = parser.parse_args()
if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    print("\n")
    exit(1)

# Carrega PCAP original
pcap_ext = os.path.splitext(args.pcapfile)[-1]
if pcap_ext.lower()==".pcap":
    print("pcap")
    myreader = PcapReader(args.pcapfile)
elif pcap_ext.lower()==".pcapng":
    print("pcapng")
    myreader = PcapNgReader(args.pcapfile)
else:
    parser.print_help(sys.stderr)
    print("\nInvalid PCAP file extension.")
    exit(1)    

# Arquivo PCAP modificado
pcap_mod_file = os.path.splitext(args.pcapfile)[0]+"_timestamp_mod.pcap"
print("\nPCAP Modificado: "+pcap_mod_file)
print("\n")

count = 0
# Remove o pcap modificado se existir
if os.path.exists(pcap_mod_file):
    os.remove(pcap_mod_file)

while True:
    try:
        packet = myreader.read_packet()
        torig = packet.time
        # Problema da função round é o arredondamento. round(torig, 3)
        # Solucao: converter para string e cortar as considerar apenas as tres primeiras casas
        s = str(torig).split(".")
        tmillis = s[0]+"."+s[1][0:args.timeprecision]
        tmod = EDecimal(tmillis)
        
        print("{:>20}: {}, {}".format("Timestamp original", torig, type(torig)))
        print("{:>20}: {}, {}".format("Timestamp Modificado", tmod, type(tmod)))
        
        packet.time = tmod

        # Salva pacote modificado no novo arquivo PCAP
        wrpcap(pcap_mod_file, packet, append=True)
    except EOFError:
        break
    count += 1
