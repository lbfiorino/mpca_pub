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
        echo "Script to merge PCAP files in chronological order based on each frame's timestamp."

        echo -e "\nUsage:"
        echo -e "\t$0 <PCAP_DIR> <OUTPUT_FILE> <FILTER>\n"
        echo -e "\nOptions:"
        echo -e "\tPCAP_DIR - Pcaps directory."
        echo -e "\t$0OUTPUT_FILE - Filename to merged pcap."
        echo -e "\t$0FILTER - Filter to find pcaps.\n"
        }


# If less than two arguments supplied, display usage.
if [  $# -le 1 ]
then
        display_usage
        exit 1
fi

PCAP_DIR=$1
OUTPUT_FILE=$2
FILTER=$3

PCAPS=($(find $1 -maxdepth 1 -name "*$FILTER*.pcap"))
for f in ${PCAPS[@]}
do
        printf "$(realpath $f)\n"
done

echo -e "\n${YELLOW}PCAPs to merge:${NC} ${PCAPS[@]}\n\n"
printf "${PURPLE}Out file:${NC} ${WHITE}$(realpath $OUTPUT_FILE)${NC}\n"
printf "\n"
read -p "Press enter to continue"

# mergecap params:
#    -v : Causes mergecap to print a number of messages while it's working.
#    -F : -F  <file format> == pcap (tcpdump)
#    -w : -w  <outfile>

mergecap -F pcap -w "$OUTPUT_FILE" ${PCAPS[@]}

echo
