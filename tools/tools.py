#!/usr/bin/env python

"""Leader Election Algorithm"""

__author__      = "XIANGYU ZHENG"
import sys

class election:

    # ip_list = []
    # def recieve_ip(self,ip):

    #IPs ['199.255.1.1','192.168.0.255','192.168.1.5']
    def select_leader(self,IPs):
        if IPs is None or len(IPs) == 0:
            return ''

        IP_map = {}
        smallest = sys.maxsize
        for IP in IPs:
            IP_split = IP.split('.')
            if len(IP_split) !=4:
                continue
            for block in IP_split:
                if not block.isdigit() or len(block)>3:
                    break
            else:
                ip = int(IP_split[0]+ IP_split[1]+IP_split[2]+IP_split[3])
                IP_map[ip] = IP
                if smallest> ip :
                    smallest = ip

        return IP_map[smallest]

