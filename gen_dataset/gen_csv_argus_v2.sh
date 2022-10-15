#!/bin/bash

display_usage() {
	echo "Script to analyse PCAP files with Argus tool and generate CSV for each file."

	echo -e "\nUsage:"
        echo -e "\t$0 <PCAP_DIR> <OUT_DIR> <LABEL1> <LABEL2> \n"
		echo -e "\nOptions:"
		echo -e "\tPCAP_DIR - Pcap files directory."
		echo -e "\t OUT_DIR - Output directory."
        echo -e "\t  LABEL1 - Sample's first label."        
        echo -e "\t  LABEL2 - Sample's second label.\n" 
	}

# If less than two arguments supplied, display usage.
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


PCAP_DIR=$(realpath $1)
OUT_DIR=$(realpath $2)
LABEL1=$3
LABEL2=$4

# Remove old files (.argus, .argus.csv)
# rm -f $OUT_DIR/*.argus
# rm -f $OUT_DIR/*.argus.csv


for file in $PCAP_DIR/*.pcap; do
    filebasename=$(basename $file)

    printf "\n"
    printf "::Processing PCAP: $filebasename \n"

    ARGUS_FILE=$(realpath "$OUT_DIR/$filebasename.argus")
    CSV_FILE=$(realpath "$OUT_DIR/$filebasename.argus.csv")

    ## Process pcap file
    # Analyse with argus
    argus -r $file -w $ARGUS_FILE
    printf "       Argus file: $ARGUS_FILE\n"
    # Generate CSV 
    ra -c , -r $ARGUS_FILE -u -nn -s stime ltime dur proto saddr sport daddr dport state spkts dpkts pkts sbytes dbytes bytes > $CSV_FILE
    # Add labels
    sed -i "1s/\$/,Label1,Label2/; 2,\$s/\$/,$LABEL1,$LABEL2/" $CSV_FILE
    printf "         CSV file: $CSV_FILE\n"

done

rm -f $OUT_DIR/*.argus

echo
echo
echo "************************************************************************"
echo "PCAP_DIR: $PCAP_DIR"
echo " OUT_DIR: $OUT_DIR"
echo "  LABELS: $LABEL1, $LABEL2"
echo
printf "${YELLOW}NECESSÁRIO CONCATENAR OS CSV'S ROTULADOS COM PANDAS${NC}\n"
printf "${YELLOW}ORDERNAR PELA COLUNA \"StartTime\"${NC}\n"
echo "************************************************************************"
echo