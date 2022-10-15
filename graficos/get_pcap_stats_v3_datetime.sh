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
	echo -e "${YELLOW}CSV files will be saved in PCAP_DIR.${NC}"
	echo -e "\nUsage:"
#	echo -e "\t$0 PCAP_DIR TIME_INTERVAL OUT_DIR"
	echo -e "\t$0 PCAP_DIR TIME_INTERVAL"
	echo -e "\nOptions:"
	echo -e "\tPCAP_DIR - PCAPs directory."
	echo -e "\tINTERVAL - Time in seconds [0.5, 1, 2,...].\n"
#	echo -e "\t OUT_DIR - Directory to save csv.\n"
}


# if less than two arguments supplied, display usage
if [  $# -lt 2 ]
then
	display_usage
	exit 1
fi


PCAP_DIR="$1"
INTERVAL="$2"
FILES="$(realpath $PCAP_DIR)/*.pcap"
#OUT_DIR=$3
OUT_DIR=$PCAP_DIR
for f in $FILES
do
    if [ -f "$f" ] && [ ! -L "$f" ]
    then
		echo ""
		filebasename=$(basename $f)
		csv_file=$OUT_DIR/"$filebasename"_stats_int_"$INTERVAL"_sec.stats.csv
		echo "::Processing file : $filebasename"

        # Tshark -t a|ad|adoy|d|dd|e|r|u|ud|udoy
		# 	r: (Default) Relative. The relative time is the time elapsed between the first packet and the current packet.
        #     ad : absolute time with date
        #      u : UTC absolute time
        #     ud : UTC absolute time with date
        #      e : Epoch. The time in seconds since epoch (Jan 1, 1970 00:00:00)
		tshark -q -nr $f -t ud -z io,stat,$INTERVAL > $f.stats
        grep -P "\d{4}-\d{2}-\d{2}|Date and time" $f.stats > $f.stats2
		cat $f.stats2 | sed 's/\s*|\s*/|/g; s/Date and time/Datetime/g' | tr "|" "," | sed 's/^.//;s/.$//' > $csv_file
		rm -f $f.stats $f.stats2
		echo "        Stats CSV : $csv_file"
    fi
done
echo ""
