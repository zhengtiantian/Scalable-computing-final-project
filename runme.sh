#!/bin/bash

#author: Mark Hanrahan

set -e
python3 -m pip install -r requirements.txt

#read/exec access for all bash
chmod u+x Demo/*

#NODES, GETIP, SENSORS
echo "Setting up nodes..."
./Demo/nodes.sh 33000
echo "Nodes set up"

echo "Obtaining subnet IP of nodes(this system)"
output=$(python3 tools/extractIP.py 2>&1)
echo "Setting sensors to point the IP:"$output
./Demo/sensors.sh 33000
echo "Sensors Created"

echo "Starting SDN Daemon..."
python3 SDN/SDNDaemon.py &
