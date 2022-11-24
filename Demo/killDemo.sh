#!/bin/bash

#author: Mark Hanrahan

BASE_PORT=$1

#nodes
for i in {0..3}
do
    port=$(($BASE_PORT + $i))
    echo $port
    kill $(sudo lsof -i:${port} | tail +2 | cut -d ' ' -f 3)> /dev/null 
done
echo "Killed all nodes"

#sensors
for j in {0..31}
do
    port=$(($BASE_PORT +300+ $j))
    echo $port
    kill $(sudo lsof -i:${port} | tail +2 | cut -d ' ' -f 3)> /dev/null
done
echo "Killed all sensors"