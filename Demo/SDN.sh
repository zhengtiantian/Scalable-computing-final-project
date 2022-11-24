#!/bin/bash

#author: Mark Hanrahan
python3 SDNDaemon.py &

python Remotecontroller.py --username admin --password admin123 --command print_sensor_data
