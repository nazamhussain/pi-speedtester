#!/bin/bash

# $1 is the name of the LAN the speedtester is being run on - e.g. plusnet, bt, etc
# $2 is time value in  HH:MM:SS format - to run script at 15 mins past every hour, the argument should be 00:15:00

if [ $# -eq 0 ]; then
    echo "No arguments provided"
    exit 1
fi

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

while true
do
  currenttime=$(date +%M:%S)
  starttime=$(date -d "$2" +%M:%S)
  endtime=$(date -d "$2 1mins" +%M:%S)
  if [[ "$currenttime" > "$starttime" ]] && [[ "$currenttime" < "$endtime" ]]; then
    mapfile < <(speedtest --accept-license --accept-gdpr --server-id=24640 --progress=no | grep 'Latency\|Download\|Upload')
    LATENCY=$(echo ${MAPFILE[0]} | awk '{print $2}')
    DOWNLOAD=$(echo ${MAPFILE[1]} | awk '{print $3}')
    UPLOAD=$(echo ${MAPFILE[2]} | awk '{print $3}')
    if [[ "$LATENCY" =~ ^[0-9.]+$ ]] && [[ "$DOWNLOAD" =~ ^[0-9.]+$ ]] && [[ "$UPLOAD" =~ ^[0-9.]+$ ]]; then
      echo "$(date) - DOWNLOAD: $DOWNLOAD / UPLOAD: $UPLOAD / LATENCY: $LATENCY"
      mosquitto_pub -h monitoring.nazam.co.uk -p 8883 -u collectduser -P collectdpass -t "collectd/hydra/internet/$1/speedtest" -m "N:$LATENCY:$DOWNLOAD:$UPLOAD" --cafile $SCRIPT_DIR/ca.crt
    fi
    sleep 3540
  fi
done
