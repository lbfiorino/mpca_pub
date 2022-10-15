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
	echo -e "Script to analyse PCAP files with tshark tool and save statistics in CSV file."
	echo -e "${YELLOW}Output files will be saved in PCAP_DIR.${NC}"
	echo -e "\nUsage:"
	echo -e "\t$0 PCAP_DIR"
	echo -e "\nOptions:"
	echo -e "\tPCAP_DIR - PCAPs directory."
}


# if less than two arguments supplied, display usage
if [  $# -lt 1 ]
then
	display_usage
	exit 1
fi


PCAP_DIR="$1"
FILES="$(realpath $PCAP_DIR)/*.pcap"
echo $FILES
#OUT_DIR=$3
OUT_DIR=$PCAP_DIR
for f in $FILES
do
    if [ -f "$f" ] && [ ! -L "$f" ]
    then
		echo ""
		filebasename=$(basename $f)
		echo "::Processing file : $filebasename"

        # Tshark -t a|ad|adoy|d|dd|e|r|u|ud|udoy
		# 	r: (Default) Relative. The relative time is the time elapsed between the first packet and the current packet.
        #     ad : absolute time with date
        #      u : UTC absolute time
        #     ud : UTC absolute time with date
        #      e : Epoch. The time in seconds since epoch (Jan 1, 1970 00:00:00)
		tshark -qnr $f -z http_req,tree > $f.stats_http_req
    fi
done
echo ""
