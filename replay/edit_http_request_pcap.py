#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import psutil
import argparse
from scapy.all import *
from scapy.layers.http import *
from datetime import datetime
from urllib.parse import urlparse

# Parser dos parametros
parser = argparse.ArgumentParser()
parser.add_argument("-pcap", "--pcap-file", dest='pcapfile', help="Arquivo PCAP.")
parser.add_argument("-dhost", "--dst-host", dest='dsthost', help="Host de destino para as requisicoes HTTP.")
args = parser.parse_args()
if len(sys.argv)<=1:
    parser.print_help(sys.stderr)
    print("\n")
    exit(1)

# Carrega PCAP original
myreader = PcapReader(args.pcapfile)
# Arquivo PCAP modificado
pcap_mod_file = os.path.splitext(args.pcapfile)[0]+"_httphost_mod.pcap"
print("\nPCAP Modificado: "+pcap_mod_file)
print("\n")

count = 0
if os.path.exists(pcap_mod_file):
    os.remove(pcap_mod_file)
while True:
    try:
        packet = myreader.read_packet()

        if HTTPRequest in packet:
            # altera o host de destino das requisições http
            packet['HTTP Request'].Host = args.dsthost
            referer = ''
            if packet['HTTP Request'].Referer:
                referer = packet['HTTP Request'].Referer.decode("utf-8")
                parsed = urlparse(referer)
                parsed = parsed._replace(netloc=args.dsthost).geturl()
                packet['HTTP Request'].Referer = parsed

            print("{:>10}: {}".format("Host", packet['HTTP Request'].Host.decode("utf-8")))
            if packet['HTTP Request'].Referer:
                print("{:>10}: {}".format("Referer", packet['HTTP Request'].Referer.decode("utf-8")))
            print("{:>10}: {}".format("Method", packet['HTTP Request'].Method.decode("utf-8")))
            print("{:>10}: {}".format("Path", packet['HTTP Request'].Path.decode("utf-8")))            
            if packet['HTTP Request'].Method.decode("utf-8") == "POST":
               print("{:>10}: {}".format("POST Load", packet['HTTP Request'].load.decode("utf-8")))            
            print("\n")
        # Salva pacote modificado no novo arquivo PCAP
        wrpcap(pcap_mod_file, packet, append=True)
    except EOFError:
        break
    count += 1