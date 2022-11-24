#!/bin/bash

#author: Mark Hanrahan

#$1 = BASEPORT 33000
#$2 = IP of node to connect to
COUNTER=0
for i in {0..3}
do
    port=$(($1+$i))
    for name in S1 S2 S3 S4 S5 S6 S7 S8
    do

    localport=$(($1+300+COUNTER))
    let COUNTER=COUNTER+1
    echo "COUNTER $COUNTER"
    echo "port $port"
    echo "localport $localport"
    python Sensors/simulate_sensor_v1.1.py --host=$2 --port=$port --name=$name --min=1 --max=10 --localport=$localport&

    done
done


