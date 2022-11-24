#!/bin/bash

#author: Mark Hanrahan

BASE_PORT=$1

for i in {0..3}
do
    python3 Nodes/clientv2.4.py --port=$(($i+$BASE_PORT)) --name="node$i" &
done