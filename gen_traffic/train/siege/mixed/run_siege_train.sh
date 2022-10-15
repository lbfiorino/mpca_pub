#!/bin/bash
#siege --quiet -t10S -g www.joedog.org

ulimit -s 65536
ulimit -n 500000

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
	echo -e "Script to run siege."
  echo -e "${YELLOW}The urls must be placed in the urls.txt file.${NC}"

	echo -e "\nUsage:"
    #echo -e "$0 <NUM_USERS> <DELAY> <TIME>\n"
    echo -e "\t$0 <START_TIME> <START_USERS> <REQ_DELAY>\n"
		echo -e "\nOptions:"
    echo -e "\t         START_TIME - Time do start in 24h format (08:10:00, 14:20:00)."        
		echo -e "\t        START_USERS - Initial number of concurrent users."
		echo -e "\t          REQ_DELAY - Delay (in seconds) between each page request."
    # echo -e "\tRUNTIME_START_USERS - Amount of time each START_USERS should run (3600S, 60M, 1H)."
    # echo -e "\t  DELAY_SCALE_USERS - Time to wait for start new users (10s, 30m, 1h)."
    # echo -e "\t    NUM_USERS_SCALE - Number of concurrent users to scale."
    # echo -e "\t      RUNTIME_SCALE - Amount of time each START_USERS should run.\n"
	}

# If less than two arguments supplied, display usage.
if [  $# -lt 3 ]
then
    display_usage
    exit 1
fi

START_TIME=$1
#START_USERS=$2
START_USERS=30
REQ_DELAY=$3
# RUNTIME_START_USERS=$4
# DELAY_SCALE_USERS=$5
# NUM_USERS_SCALE=$6
# RUNTIME_SCALE=$7


# siege params:
#    --quiet    : This directive silences siege.
#    --log=FILE : This directive allows you to specify an alternative file for logging.)
#    -c         : Set the concurrent number of users.
#    -d         : Instructs siege how long to delay (in seconds) between each page request.
#    -i         : Internet mode. It makes requests from the urls.txt file in random order.
#    -f         : list of urls inside a text file.
#    -t         : Amount of time each user should run (-t3600S, -t60M, -t1H)

rm -f ./siege*.log

SIEGE_START_CMD="siege --quiet --log=./siege_30u_1H.log -c$START_USERS -d$REQ_DELAY -i -f urls.txt -t1H"
SIEGE_UPSCALE_CMD="siege --quiet --log=./siege_120u_20-40min.log -c120 -d$REQ_DELAY -i -f urls.txt -t20M"
SIEGE_DOWNSCALE_CMD="siege --quiet --log=./siege_60u_40-60min.log -c60 -d$REQ_DELAY -i -f urls.txt -t21M"

# SLEEP TO START_TIME
echo -e "\nWaiting to start at $(date -d $START_TIME +'%D %T %:z')."
sleep $(( $(date -d $START_TIME +%s) - $(date +%s) ))


# # START_USERS for TIME_START_USERS
echo -e "\n$(date +'%D %T %:z') --> Starting $START_USERS users" ; $SIEGE_START_CMD &
PID_SIEGE_START=$(pgrep -f "$SIEGE_START_CMD")
echo "PID SIEGE_START: $PID_SIEGE_START"

# SLEEP TO UPSCALE
echo -e "\nSleep 20min to scale users..." ; sleep 20m
echo -e "\n$(date +'%D %T %:z') --> Scaling 120 users, total 150 users" ; $SIEGE_UPSCALE_CMD &
PID_SIEGE_UPSCALE=$(pgrep -f "$SIEGE_UPSCALE_CMD")
echo "PID_SIEGE_UPSCALE: $PID_SIEGE_UPSCALE"

# SLEEP TO DOWNSCALE
echo -e "\nSleep 20min to downscale users..." ; sleep 20m
echo -e "\n$(date +'%D %T %:z') --> Downscaling 60 users, total 90 users" ; $SIEGE_DOWNSCALE_CMD &
PID_SIEGE_DOWNSCALE=$(pgrep -f "$SIEGE_DOWNSCALE_CMD")
echo "PID_SIEGE_DOWNSCALE: $PID_SIEGE_DOWNSCALE"


if wait $PID_SIEGE_UPSCALE; then
  echo -e "\nProcess $PID_SIEGE_UPSCALE SIEGE UPSCALE success. End at $(date +'%D %T %:z')"
else
  echo "Process $PID_SIEGE_UPSCALE fail"
fi


if wait $PID_SIEGE_START; then
  echo -e "\nProcess $PID_SIEGE_START SIEGE START success. End at $(date +'%D %T %:z')"
else
  echo "Process $PID_SIEGE_START fail"
fi


if wait $PID_SIEGE_DOWNSCALE; then
  echo -e "\nProcess $PID_SIEGE_DOWNSCALE SIEGE DOWNSCALE success. End at $(date +'%D %T %:z')"
else
  echo "Process $PID_SIEGE_DOWNSCALE fail"
fi


echo ""


# # SIEGE_START COMMAND
# SIEGE_START_CMD="siege --quiet --log=./siege_start.log -c$START_USERS -d$REQ_DELAY -i -f urls.txt -t$RUNTIME_START_USERS"
# # SIEGE_SCALE COMMAND
# SIEGE_SCALE_CMD="siege --quiet --log=./siege_scale.log -c$NUM_USERS_SCALE -d$REQ_DELAY -i -f urls.txt -t$RUNTIME_SCALE"

# # START_USERS for TIME_START_USERS
# echo -e "\n$(date +'%D %T %:z') --> Starting $START_USERS users" ; $SIEGE_START_CMD &
# PID_SIEGE_START=$(pgrep -f "$SIEGE_START_CMD")
# echo "PID SIEGE_START: $PID_SIEGE_START"

# #SLEEP TO SCALE
# echo -e "\nSleep $DELAY_SCALE_USERS to scale users..." ; sleep $DELAY_SCALE_USERS

# # SCALE USERS
# echo -e "\n$(date +'%D %T %:z') --> Scaling $NUM_USERS_SCALE users" ; $SIEGE_SCALE_CMD &
# PID_SIEGE_SCALE=$(pgrep -f "$SIEGE_SCALE_CMD")
# echo "PID SIEGE_START: $PID_SIEGE_SCALE"

# if wait $PID_SIEGE_SCALE; then
#   echo -e "\nProcess $PID_SIEGE_SCALE SIEGE SCALE success. End at $(date +'%D %T %:z')"
# else
#   echo "Process $PID_PID_SIEGE_SCALE fail"
# fi

# if wait $PID_SIEGE_START; then
#   echo -e "\nProcess $PID_SIEGE_START SIEGE START success. End at $(date +'%D %T %:z')"
# else
#   echo "Process $PID_SIEGE_START fail"
# fi

# if [ $? -eq 0 ] ; then
#   echo "Success "
# else
#   echo "Failure"
# fi
