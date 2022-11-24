# Scalable-P3

# RUNME.SH

  The runme.sh script will start 4 nodes, create 8 sensors for each of these nodes.
  The sensors will fire data at the nodes, per-node data will be stored under 'Data/'
  Logs for each node will be available under 'Logs/'
  The SDN Daemon will also be started in the background

  To begin, install pip dependencies
  'pip install -r requirements.txt'

  Get read/execute access: 
  'chmod u+x runme.sh'

  Execute runme.sh
  './runme.sh'

  View Data and Logs.
  When finished, see killme section below.

# SDN Commands

  Once you have executed the runme.sh script, you can access the SDN through commands:
  
  python3 SDN/Remotecontroller.py --username admin --password admin123 --command print_topology
  python3 SDN/Remotecontroller.py --username admin --password admin123 --command election
  python3 SDN/Remotecontroller.py --username admin --password admin123 --command print_sensor_data

  python3 SDN/Remotecontroller.py --username admin --password admin123 --command sleep:[ip]:[port] #example port = Node1:33000, Sensor1:33300
  python3 SDN/Remotecontroller.py --username admin --password admin123 --command wakeup:[ip]:[port] #IP depends on local subnet IP, workaround by running 'python3 tools/extractIP.py'

# KILLME.SH

  The killme.sh script kills all running nodes and sensors created from the runme.sh script, iff previously ran.
  The script will output errors if there are no procs to kill.

  'chmod u+x killme.sh'
  
  Execute killme.sh
  './killme.sh'






# Changelog: python Nodes/client.py

# v.1

1.)
-Client will begin by looking for a leader
-If leader unavailable, will try again
-After 4 unsuccessful attempts, elect itself as leader (unsure if this is right thing to do might change this later, but it works->self-organising)

2.)
-If client is leader it will listen for 'who is leader?' broadcasts (UDP)

-Regardless, all clients will 'do stuff' this will be things like collecting sensor data or any other execution.

# v.1.1

3.)
-If client is the leader it will also send recurring 'I am leader!' messages every X cylces (controlled by counter similar to 'leaderCounter').
-Client hears this message and compares to current leader
-if this is wrong then call for re-election
-if this haven't heard for Xcycles, assume leader is dead and call re-election (Currently just reverting to unknown leader, will ask again for leader...)
-election not yet implemented

-Had an issue with reading the wrong messages, so now directing certain messages to various ports, 3700 (general msg), 3701 (election msg)

# v.2.1

-Run 2 pis
cd Node
python clientv2.1.py --port 33000 --name pi1
python clientv2.1.py --port 33001 --name pi2

# v.2.0

-overhaul to structure and code flow

# v.2.1

-added sensor listener functionality

# v2.3

-added logs instead of print()

# v2.4

-added ML and Security(SHA256)

# How to Run

- Install needed packages
  pip install sklearn
  pip install cryptography
  pip install jupyter-lab
- train the model
- start SDN. More details at SDN section.
- start sensors and nodes by shell scripts. More details at Shell Scripts

# Training the Model

- go to the Models directory and run jupyter-lab from terminal
- run the test_sc.ipynb notebook on the jupyter web interface and a model file will be generated in the same file by the name of 'sc_proj_3_model.pkl'
- copy this model file into the 'Nodes' directory

# SDN

-Run SDN on fixed port 33020
cd SDN
-Start the UDP receiver
python SDNDaemon.py
-Start the controller with commands
python Remotecontroller.py --username admin --password admin123 --command print_topology
python Remotecontroller.py --username admin --password admin123 --command election
python Remotecontroller.py --username admin --password admin123 --command print_sensor_data

python Remotecontroller.py --username admin --password admin123 --command sleep:[ip]:[port]
python Remotecontroller.py --username admin --password admin123 --command wakeup:[ip]:[port]

# Shell Scripts

-before running any bash scripts run:
chmod u+x Demo.sh

-in main directory of project, run:
-nodes: ./Demo/nodes.sh [Base_Port/33000]
-sensors: ./Demo/sensors.sh [Base_Port] [IP]
Example: ./Demo/sensors.sh 33000 192.168.0.60, where 192.168.0.60 is my local or pi ip address. Don't use 127.0.0.1.

-to kill nodes run:
./Demo/killDemo.sh [Base_Port]

# Note: kills nodes on the system and sensors. Sensors from 33300 to 33332

## Pi's in macneill.scss.tcd.ie

rasp-017.berry.scss.tcd.ie
rasp-018.berry.scss.tcd.ie

# Note

The prof says

Hi all,

Just an FYI:  the Pi subnet 10.35.70.0/24 is configured to allow inter-pi communications on non-privileged ports only -- specifically through 33000-34000 on both TCP/UDP."

# Note: for running clients with an ML model

add another parameter for the link to the model file eg:
python .\Scalable-P3\Nodes\clientv2.4.py --name Node_1_new --model .\Scalable-P3\Models\sc_proj_3_model.pkl --leader y --port 33000
