#!/usr/bin/env python

"""SDN daemon code, listens to network and maintains information"""

__author__ = "JIACHUAN WANG(IAN)"
__email__ = "wangj3@tcd.ie"

import argparse
import os
import time
import socket
import configparser
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Security.SymmetricEncryption import encrypted, decrypted

SDN_PORT=33020
HEART_BEAT_GAP = 20
wakeupCall='wake up!'
sleepCall='sleep!'
leaderCall = 'IamLeader!'
data_req_call = "REQ DATA"
data_sync_call = "SYNC DATA"
SensorHeartBeatCall='SensorHeartBeat!'
class SDNDaemon:
    "This is a SDNDaemon class. It supports A.receive UDP heartbeats B. receive leader info and write to a file" \

    def __init__(self, port):
        # store last time we have see this node's heartbeat
        self.heartBeatTimeMap = {}
        self.statusMap = {}
        self.hostMap = {}
        self.leader = ''

        self.nodeSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
        self.nodeSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) #not sure if still needed, using anyway
        # Enable broadcasting mode
        self.nodeSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.nodeSocket.bind(("", port))
        self.nodeSocket.settimeout(5) #tune this later

    def reset(self):
        self.heartBeatTimeMap = {}
        self.statusMap = {}
        self.hostMap = {}

    def append_to_file(self, content, filename):
        print('writing to file')
        with open(filename, "a+") as file_ref:
            file_ref.write(content)
            file_ref.write("\n")

    def sendToAll(self, msg):
        msg = msg.encode()
        msg= encrypted(msg)
        for port in range(33000,33020):
            UDP_sensor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            UDP_sensor_socket.sendto(msg, ('<broadcast>', port))

    def receive_UDP(self):
        print('Start SDN Daemon')
        program_start = time.time()
        # close itself in 20 mins
        while time.time() - program_start <= 1200:
            try:
                data, addr = self.nodeSocket.recvfrom(65535)
                data = decrypted(data)
                packet_segments = data.decode().split(',',2)
                packet_type = packet_segments[0]
                if packet_type.strip() == leaderCall:
                    self.receive_leader(addr)
                    print('Leader: {} heartbeat is received'.format(addr))
                    self.receive_heart_beats(addr, packet_segments[-1])
                elif packet_type.strip() == SensorHeartBeatCall:
                    print('Sensor: {} heartbeat is received'.format(addr))
                    self.receive_heart_beats(addr, packet_segments[-1])

                elif packet_type.strip()==data_sync_call:
                    self.append_to_file(packet_segments[2], 'SensorData')
            except Exception as e:
                print(e)
            time.sleep(0.5)


    def receive_heart_beats(self, hostname, name):

        currentTime = time.time()
        self.hostMap[hostname] = name
        ip = str(hostname[0])
        port = str(hostname[1])
        self.statusMap[hostname] = 'Active'

        if len(self.heartBeatTimeMap) !=0:
            for n in self.heartBeatTimeMap.keys():
                gap = currentTime - self.heartBeatTimeMap[n]
                if gap > HEART_BEAT_GAP:
                    self.statusMap[n] = 'Inactive'
        self.heartBeatTimeMap[hostname] = currentTime
        self.write()

    def receive_leader(self, hostname):
        print('{} is the leader'.format(hostname))
        self.leader = hostname
        print('Get data from leader {}'.format(hostname))
        msg = data_req_call.encode()
        msg= encrypted(msg)
        self.nodeSocket.sendto(msg, hostname)



    def write(self):
        config = configparser.ConfigParser()

        config['DEFAULT'] = {'nodes': self.hostMap, 'leaderInfo': self.leader,
                             'statusMap': self.statusMap}
        with open('config.properties', 'w') as configfile:
            config.write(configfile)



# Output: A-B etc.
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='port of the base station(SDN) default port', type=str)
    args = parser.parse_args()
    if args.port is None:
        port = SDN_PORT
    else:
        port = int(args.port)
    remote = SDNDaemon(port)
    remote.receive_UDP()


if __name__ == '__main__':
    main()
