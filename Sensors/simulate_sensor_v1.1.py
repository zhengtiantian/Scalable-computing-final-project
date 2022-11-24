#!/usr/bin/env python

"""Simulates sensor readings, sends to specified node"""

__author__      = "DAANISH MILLWALLA"


import random
import argparse
import socket
import time
import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Security.SymmetricEncryption import decrypted, encrypted

wakeupCall = 'wake up!'
sleepCall = 'sleep!'
SensorHeartBeatCall = 'SensorHeartBeat!'


def sendToAll(nodeSocket, msg, localport):

    # localport
    # nodeSocket.bind(localport)
    msg = msg.encode()
    msg = encrypted(msg)
    for port in range(33000, 33019):
        nodeSocket.sendto(msg, ('<broadcast>', port))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', help='name of this sensor', type=str)
    parser.add_argument('--host', help='hostname of the node to connect to', type=str)
    parser.add_argument('--port', help='port of the node', type=str)
    parser.add_argument('--min', help='minimum value of sensor reading', type=float)
    parser.add_argument('--max', help='maximum value of sensor reading', type=float)
    # localport
    parser.add_argument('--localport', help='port of the sensor', type=float)

    args = parser.parse_args()

    if args.name is None:
        print("please specify the name of this sensor")
        exit(1)

    # localport
    if args.localport is None:
        print("please specify the port of the node")
        exit(1)

    if args.host is None:
        print("please specify the hostname of the node")
        exit(1)

    if args.port is None:
        print("please specify the port of the node")
        exit(1)

    if args.min is None:
        print("please specify the minimum sensor reading")
        exit(1)

    if args.max is None:
        print("please specify the maximum sensor reading")
        exit(1)

    delimiter = ","
    nodeUp = True
    socket.SO_REUSEPORT = socket.SO_REUSEADDR
    nodeSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    nodeSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)  # not sure if still needed, using anyway
    # Enable broadcasting mode
    nodeSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    print(args.localport)
    nodeSocket.bind((args.host, int(args.localport)))
    UDP_sensor_socket = nodeSocket
    program_start = time.time()
    # close itself in 20 mins
    while time.time() - program_start <= 1200:
        try:
            UDP_sensor_socket.settimeout(0.1)
            data, addr = UDP_sensor_socket.recvfrom(1024)
            data = decrypted(data)
            UDP_sensor_socket.settimeout(None)
            text = data.decode().split(',')  # limiter
            msg = text[0]  # type of message
            print(text)
            print(msg)
            print(addr)
            if msg.strip() == wakeupCall:
                print('Waking up node {}...'.format(str(args.name)))
                nodeUp = True
                logging.info('REQUESTED TO WAKE')
            if msg.strip() == sleepCall:
                print('Sleep node {}...'.format(str(args.name)))
                nodeUp = False
                logging.info('REQUESTED TO SLEEP')
        except:
            pass

        if nodeUp:
            sensor_reading = random.uniform(args.min, args.max)

            message_str = "SENSOR DATA PACKET " + delimiter + " Sensor: " + args.name + " " + delimiter + " Val: " + str(
                sensor_reading) + " " + delimiter + " Time: " + str(int(time.time()))
            message = str.encode(message_str)
            print(message_str + " to node " + args.host + ":" + args.port)
            message = encrypted(message)
            UDP_sensor_socket.sendto(message, (args.host, int(args.port)))
            sendToAll(nodeSocket, SensorHeartBeatCall + ',' + str(args.name), args.localport)

        time.sleep(10)

    return


if __name__ == '__main__':
    main()