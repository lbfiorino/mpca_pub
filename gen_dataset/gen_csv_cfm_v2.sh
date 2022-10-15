#!/bin/bash

display_usage() {
	echo -e "Script to analyse PCAP files with CICFlowMeter tool and generate CSV for each file."
	echo -e "\nUsage:"
        echo -e "\t$(basename $0) <PCAP_DIR> <OUT_DIR> <LABEL1> <LABEL2>"
		echo -e "\nOptions:"
		echo -e "\tPCAP_DIR - Pcap files directory"
		echo -e "\t OUT_DIR - Output directory"
        echo -e "\t  LABEL1 - Sample's first label."        
        echo -e "\t  LABEL2 - Sample's second label.\n" 
	}

# If less than three arguments supplied, display usage.
	if [  $# -lt 3 ]
	then
		display_usage
		exit 1
	fi


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


# CICFlowMeter 
CFM_BIN=/home/lucianobf/CICFlowMeter-4.0_microsec/bin

PCAP_DIR=$(realpath $1)
OUT_DIR=$(realpath $2)
LABEL1=$3
LABEL2=$4

cd $CFM_BIN

# Remove old files (_Flow.csv, _cfm.csv)
# rm -f $OUT_DIR/*_Flow.csv
# rm -f $OUT_DIR/*_cfm.csv

for file in $PCAP_DIR/*.pcap; do

    filebasename=$(basename $file)
    
    CSV_FILE=$(realpath $OUT_DIR/$filebasename"_Flow.csv")
         
    printf "\n"
    printf "::Processing PCAP: $filebasename \n"

    ./cfm $file $OUT_DIR
    # Add Labels
    sed -i "s/,Label/,Label1/" $CSV_FILE
    sed -i "s/,NeedManualLabel/,$LABEL1/" $CSV_FILE
    sed -i "1s/\$/,Label2/; 2,\$s/\$/,$LABEL2/" $CSV_FILE
    # Rename file with label
    mv $CSV_FILE $CSV_FILE"_cfm.csv"
done

echo
echo "************************************************************************"
echo "PCAP_DIR: $PCAP_DIR"
echo "OUT_DIR: $OUT_DIR"
echo "LABELS: $LABEL1, $LABEL2"
echo
printf "${YELLOW}NECESSÁRIO CONCATENAR OS CSV'S ROTULADOS COM PANDAS${NC}\n"
printf "${YELLOW}ORDERNAR PELA COLUNA \"Flow Start Time\"${NC}\n"
echo "************************************************************************"
echo