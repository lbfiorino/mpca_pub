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


display_usage() {
	echo -e "Script to extract only SYN packets from PCAP."
	echo -e "\nUsage:"
        echo -e "\t$(basename $0) <PCAP_DIR> <OUT_DIR>"
		echo -e "\nOptions:"
		echo -e "\tPCAP_DIR - Pcap files directory"
		echo -e "\t OUT_DIR - Output directory.\n"
	}

# If less than three arguments supplied, display usage.
	if [  $# -lt 2 ]
	then
		display_usage
		exit 1
	fi


PCAP_DIR=$(realpath $1)
OUT_DIR=$(realpath $2)
for file in $PCAP_DIR/*.pcap; do
    filebasename=$(basename $file)
    printf "::Processing PCAP: $file \n"
    OUTFILE=$OUT_DIR"/"$filebasename"_only-syn.pcap"
    #printf "OUTFILE = $OUTFILE\n\n"
    tcpdump -r $file "(tcp[tcpflags] == tcp-syn) and (tcp port 80)" -w $OUTFILE -U
done