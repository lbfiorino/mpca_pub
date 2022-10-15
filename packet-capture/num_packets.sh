#!/bin/bash

# Reset Color
NC='\033[0m'              # Text Reset
# Regular Colors
RED='\033[0;31m'          # Red
GREEN='\033[0;32m'        # Green
YELLOW='\033[0;33m'       # Yellow
BLUE='\033[0;34m'         # Blue
PURPLE='\033[0;35m'       # Purple
CYAN='\033[0;36m'         # Cyan
WHITE='\033[0;37m'        # White

PCAP=$1

TOTAL=$(tcpdump -r $PCAP | wc -l)
SYN=$(tcpdump -r $PCAP "tcp[tcpflags] == tcp-syn" | wc -l)
SYN_ACK=$(tcpdump -r $PCAP "tcp[tcpflags] == tcp-syn|tcp-ack" | wc -l)
RST=$(tcpdump -r $PCAP "tcp[tcpflags] == tcp-rst" | wc -l)

printf "\nPCAP: ${PCAP}\n"
printf "      Total packets: ${TOTAL}\n"
printf "        SYN packets: ${SYN}\n"
printf "    SYN/ACK packets: ${SYN_ACK}\n"
printf "        RST packets: ${RST}\n"
