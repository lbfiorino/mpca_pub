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
	echo -e "GoReplay script to extract HTTP requests from PCAP."
	echo -e "${YELLOW}GOR files will be saved in PCAP_DIR.${NC}"
	echo -e "It will be generate one .gor file for each PCAP file."
	echo -e "Make sure to add GoReplay bin in PATH:"
	echo -e "   GoReplay 1.2.0 -->  ~/.local/bin/gor1.2.0"
	echo -e "   GoReplay 1.3.3 -->  ~/.local/bin/gor1.3.3"
	echo -e "   $ export PATH=\$PATH:~/.local/bin/"

	echo -e "\nUsage:"
    echo -e "\t$0 GOR_VERSION PCAP_DIR OUT_DIR"
	echo -e "\nOptions:"
	echo -e "\tGOR_VERSION - GoReplay version [1.2.0 | 1.3.3]."
	echo -e "\t   PCAP_DIR - Pcaps directory."	
	echo -e "\t    OUT_DIR - Directory to save .gor files.\n"	
	#echo -e "\t  PCAP_FILE - Pcap file."
	#echo -e "\tGOR_OUTFILE - Goreplay file with HTTP requests. ${YELLOW}Caution! Can generate multiple files See output file limits in documentation.${NC}\n"
}

# If less than two arguments supplied, display usage.
if [  $# -lt 3 ]
then
    display_usage
    exit 1
fi

#INPUTPCAP=
GOR_VERSION=$1
PCAP_DIR=$(realpath $2)
OUT_DIR=$(realpath $3)
GOR_BIN="gor$GOR_VERSION"

printf "\n"
printf "${WHITE}GoReplay${NC} = $GOR_BIN\n"
printf "${WHITE}PCAP_DIR${NC} = $PCAP_DIR\n"
printf " ${WHITE}OUT_DIR${NC} = $OUT_DIR\n"
printf "\n"


printf "\n${YELLOW}[ALERT] GoReplay not exit at EOF. Press CRTL+C at pcap EOF to processs next file.${NC}\n"
read -p "Press Enter to continue..." cont

OUT_FILES=""
for PCAP_FILE in $PCAP_DIR/*.pcap; do
	filebasename=$(basename $PCAP_FILE)
    printf "\n"
    printf "::Extracting requests from PCAP: $filebasename \n"
	GOR_OUTFILE=$OUT_DIR/$filebasename\_$GOR_BIN.gor
	OUT_FILES="$OUT_FILES\n$GOR_OUTFILE"
	$GOR_BIN --verbose 10 --input-raw $PCAP_FILE:80 --input-raw-engine pcap_file --output-file-size-limit 1TB --output-file-queue-limit 0 --output-file $GOR_OUTFILE
done


printf "\n\n ${GREEN}Done!${NC}\n"
printf "${WHITE}GoReplay${NC} = $GOR_BIN"
printf "${WHITE}Gor files:${NC}\n"
printf "$OUT_FILES"
printf "\n"
exit 0
