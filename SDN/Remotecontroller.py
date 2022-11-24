#!/usr/bin/env python

"""
SDN controller code, interfaces with SDN daemon to execute commands
Design based on Reference - FLAUZAC, O. et al. An SDN approach to route massive data flows of sensor networks.
International Journal of Communication Systems, [s. l.], v. 33, n. 7, p. 1–14, 2020. DOI 10.1002/dac.4309.
Disponível em: https://search-ebscohost-com.elib.tcd.ie/login.aspx?direct=true&db=a9h&AN=142538419.
Acesso em: 27 nov. 2021.
"""

__author__ = "JIACHUAN WANG(IAN)"
__email__ = "wangj3@tcd.ie"

import socket
import argparse
import configparser
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Security.SymmetricEncryption import encrypted

wakeupCall='wake up!'
sleepCall='sleep!'
electionCall = 'Election!'
MSGLEN=20
UDP_sensor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class RemoteController:
    "This is a controller class. It supports " \
    " A.print topology B.Wakeup or sleep nodes C.Read sensor data from the leader of WSN. D Election"

    def __init__(self):
        pass


    def read(self):
        config = configparser.ConfigParser()
        config.read('config.properties')

        nodes = config.get('DEFAULT', 'nodes')
        leaderInfo = config.get('DEFAULT', 'leaderInfo')
        statusMap = config.get('DEFAULT', 'statusMap')
        return [nodes, leaderInfo, statusMap]

    def print_topology(self):
        nodes, leaderInfo, statusMap = self.read()
        print('Nodes: ' + nodes)
        print('statusMap: ' + statusMap)
        print('Leader: ' + leaderInfo)



    def wake_up_node(self, hostname, port):
        addr = (hostname,port)
        print('Sending a message to wake up a node {}:{}'.format(hostname, port))

        msg = wakeupCall.encode()
        msg= encrypted(msg)
        UDP_sensor_socket.sendto(msg, addr)



    def sleep_node(self, hostname, port):
        addr = (hostname,port)
        print('Sending a message to make a node sleep {}:{}'.format(hostname, port))

        msg = sleepCall.encode()
        msg= encrypted(msg)
        UDP_sensor_socket.sendto(msg, addr)

    def election(self, hostname, port):
        print('Sending a message to make a election')

        msg = electionCall.encode()

        self.sendToAll(msg)

    def sendToAll(self, msg):
        msg = msg.encode()
        UDP_sensor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
        UDP_sensor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) #not sure if still needed, using anyway
        # Enable broadcasting mode
        UDP_sensor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        for port in range(33000,33020):
            msg= encrypted(msg)
            UDP_sensor_socket.sendto(msg, ('<broadcast>', port))

    def get_file_contents(self, filename):
        print('reading file')
        path = os.getcwd()
        path = os.path.join(path, filename)
        try:
            with open(path, "r") as file_ref:
                lines = file_ref.readlines()
                last_lines = lines[-10:]
                return "".join(last_lines)
        except:
            return ''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', help='username of the node', type=str)
    parser.add_argument('--password', help='password of the node', type=str)
    parser.add_argument('--command', help='command for SDN:print_topology, sleep [ip]:[port], wakeup [ip]:[port], election, print_sensor_data', type=str)

    args = parser.parse_args()

    if args.username is None or args.password is None or str(args.username) != 'admin' or str(
            args.password) != 'admin123':
        print("The username or password is wrong.please specify the right username and password")
        exit(1)

    if args.command is None:
        print("please specify the command of this SDN remote controller")
        exit(1)

    # if args.tcpport is None:
    #     print("please specify the tcp port of the node")

    remote = RemoteController()

    if args.command == 'print_topology':
        remote.print_topology()

    if str(args.command).startswith('wakeup'):
        remote.wake_up_node(str(args.command).split(':')[1], int(str(args.command).split(':')[2]))

    if str(args.command).startswith('sleep'):
        remote.sleep_node(str(args.command).split(':')[1], int(str(args.command).split(':')[2]))
    if str(args.command).startswith('election'):
        print("Election!")
        remote.sendToAll(electionCall)
    if str(args.command).startswith('print_sensor_data'):
        print(remote.get_file_contents('SensorData'))



if __name__ == '__main__':
    main()
