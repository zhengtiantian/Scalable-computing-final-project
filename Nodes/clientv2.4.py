#!/usr/bin/env python

"""This is the code that runs on each Node"""

__author__      = "Mark Hanrahan, DAANISH MILLWALLA"

import socket
import time
import argparse
import os
import logging
import pickle
import sklearn
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Security.SymmetricEncryption import encrypted, decrypted

LEADER_RECCURING = 10
CLIENT_RECCURRING = LEADER_RECCURING/2
WORRY = 2*LEADER_RECCURING

data_req_call = "REQ DATA"
incorrect_leader_call = "INCORRECT LEADER"
data_sync_call = "SYNC DATA"
sensor_data_packet = "SENSOR DATA PACKET"
clientCall = 'WhoisLeader?'
leaderCall = 'IamLeader!'
electionCall = 'Election!'
electionResult = 'ElectionResult!'
Leader = 'Unknown' #Unknown, Me, {LeaderIP:Port}
leaderReccuring = 0
clientReccuring = 0 #start at zero, ask for leader straight away
localAddr = None #default value
worryCounter = WORRY
nodeUp = True
wakeupCall='wake up!'
sleepCall='sleep!'
model = None
model_path = None
sensor_corruption = {}

def setUpLogs(name):
    path = os.getcwd()
    directory = 'Logs'
    path = os.path.join(path,directory)
    try:
        #mkdir if doesn't exist
        os.mkdir(path)
    except:
        pass
    path = os.path.join(path, str(localAddr)+ name+".log")

    logging.basicConfig(filename=path, filemode='w', format='%(process)d - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logging.warning('This will get logged to a file')
    logging.warning(path)

def append_to_file(content, filename):
    logging.info('writing to file')
    path = os.getcwd()
    directory = 'Data'
    path = os.path.join(path,directory)
    try:
        #mkdir if doesn't exist
        os.mkdir(path)
    except:
        pass
    path = os.path.join(path, filename+".txt")
    with open(path, "a+") as file_ref:
        file_ref.write(content)
        file_ref.write("\n")

def get_file_contents(filename):
    logging.info('reading file')
    path = os.getcwd()
    directory = 'Data'
    path = os.path.join(path,directory)
    path = os.path.join(path, filename+".txt")
    try:
        with open(path, "r") as file_ref:
            lines = file_ref.readlines()
            last_lines = lines[-10:]
            return "".join(last_lines)
    except:
        return ''

def send_sensor_data_slice_to_addr(nodeSocket, args, addr):
    msg = get_file_contents(args.name)
    if msg=='':
        logging.warning("No data to send")
    else:
        msg = data_sync_call + ","+ "NODE:" + args.name + ","  \
            + "\n" + msg \
            # + "\nEND SYNC\n"
        send_data_to_addr(msg, addr, nodeSocket)

def send_data_to_addr(msg, addr, nodeSocket):
    logging.info('Sending to: {}'.format(addr))
    msg = msg.encode()
    msg = encrypted(msg)
    nodeSocket.sendto(msg, addr)

def check_if_leader_and_get_data(nodeSocket, args, addr):
    if Leader == localAddr:
        send_sensor_data_slice_to_addr(nodeSocket, args, addr)
    else:
        msg = incorrect_leader_call + "," + ':'.join(map(str,Leader))
        send_data_to_addr(msg, nodeSocket, addr)


def setLeader(addr):
    global Leader
    Leader = addr
    # print('Leader Set:',Leader)
    log = 'Leader Set: {}'.format(Leader)
    logging.info(log)

def sendToAll(nodeSocket,msg):
    msg = (msg+','+ name).encode()
    msg = encrypted(msg)
    for port in range(33000,33021):
            nodeSocket.sendto(msg, ('<broadcast>', port))

def getMsg(nodeSocket, args):
    global worryCounter
    global sensor_corruption
    #get msg
    try:  
        data, addr = nodeSocket.recvfrom(1024)
        data = decrypted(data)
        #clientCall -> 'WhoisLeader?'
        #leaderCall -> 'IamLeader!'
        #electionCall -> 'Election!'

        text = data.decode().split(',') #limiter
        msg = text[0] #type of message
        # print(text)
        # print(msg)
        # print(addr)
        
        if addr != localAddr:
            log = 'Received:{} from {}'.format(msg,addr)
            logging.info(log)

        if msg.strip() == sensor_data_packet:
            try:
                if model is not None:
                    sensor_frag = text[1].split(':')
                    sensor_name = sensor_frag[1].strip()
                    val = float(text[2].split(':')[1].strip())
                    prediction = int(model.predict([[val]]))
                    if prediction == 0:
                        if sensor_name not in sensor_corruption:
                            sensor_corruption[sensor_name] = 1

                        if sensor_corruption[sensor_name] > 3:
                            logging.warning('Sensor: ' + sensor_name + ' malfunction. Ignoring reading: ' + data.decode())
                            return
                        
                        else:
                            sensor_corruption[sensor_name] = sensor_corruption[sensor_name] + 1
                    else:
                        if sensor_name in sensor_corruption:
                            sensor_corruption[sensor_name] = 0
                else:
                    logging.info('No model')
            except Exception:
                logging.warning(Exception)
                pass

            
            append_to_file(data.decode(), args.name)

        if msg.strip() == data_sync_call:
            append_to_file(data.decode(), args.name)

        if msg.strip() == data_req_call:
            check_if_leader_and_get_data(nodeSocket, args, addr)
        if msg.strip() == sleepCall:
            sleepNode()
        if msg.strip() == wakeupCall:
            wakeupNode()
        if msg == clientCall:
            #only leaders care about this
            if Leader == localAddr:
                #send Leader Reply
                logging.info('Responding as Leader...')
                return leaderCall
        if msg == leaderCall:
            #everyone cares about this
            if Leader == 'Unknown':
                #set as Leader
                setLeader(addr)
            
            else:
                if addr != Leader:
                    logging.info('Comparing Leaders: {} {}'.format(addr,Leader))
                if addr<Leader:
                    logging.info('new addr is lower')
                    setLeader(addr)
            if Leader == addr:
                #reset worryCounter
                worryCounter = 0
        else:
            pass
        if msg == electionCall:
            if Leader in ['Unknown',localAddr]:
                #perform algorithm, return result. Leaders cannot perform this step as they don't have access to their local subnet ip
                pass
            #everyone cares about this
            #perform election protocol
            pass

        
        
    except:
        #nothing in port
        #increment worryCounter
        if Leader != localAddr:
            if worryCounter >=WORRY:
                #elect itself as leader
                setLeader(localAddr)
                worryCounter = 0
            else:
                worryCounter +=1
                log = 'Missing Leader...{}/{}'.format(worryCounter,WORRY)
                logging.info(log)


def sendMsg(nodeSocket, reply):
    # msg = clientCall.encode()
    # nodeSocket.sendto(msg, ('<broadcast>', nodeSocket.getsockname()[1]))
    
    #Cases for sending a msg:
    # -if node has a specific response (from get msg), send it
    # -if leader, sending reccuring msg (x cycles: LEADER_RECCURING)
    # -if node doesn't have a leader, ask for one every (y cycles: CLIENT_RECURRING)

    
    if reply:
        sendToAll(nodeSocket,reply)

    if Leader == localAddr:
        global leaderReccuring
        if leaderReccuring <=0:
            logging.info('sending leader call')
            sendToAll(nodeSocket, leaderCall)
            leaderReccuring = LEADER_RECCURING
        else:
            leaderReccuring -=1

    if Leader == 'Unknown':
        global clientReccuring
        if clientReccuring <=0:
            logging.info('sending client call')
            sendToAll(nodeSocket,clientCall)
            clientReccuring = CLIENT_RECCURRING
        else:
            clientReccuring-=1


def wakeupNode():
    print('Waking up node...')
    global nodeUp
    nodeUp = True
    logging.info('WAKEUP MODE NOW!')


def sleepNode():
    print('Sleep node...')
    logging.info('Sleeping node.Only receiving messages...')
    global nodeUp
    nodeUp = False



def nodeLoop(nodeSocket, args):
    global model
    global model_path
    try:
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
    except:
        pass

    upload_start = time.time()
    missing_start = time.time()
    program_start = time.time()
    # close itself in 20 mins
    while time.time() - program_start <= 1200:
        reply = getMsg(nodeSocket, args)
        # nodeUp is a global variable that can be controlled by SDN. When it is False, no messages are sent.
        if nodeUp:
            sendMsg(nodeSocket, reply)
        
            if time.time() - upload_start >= 5:
                logging.info('20 sec interval')
                upload_start = time.time()
                if (Leader != "Unknown") and (Leader != localAddr) :
                    send_sensor_data_slice_to_addr(nodeSocket, args, Leader)



        #dostuff



        #sleep for now (testing), remove later
        time.sleep(0.5)
                   
def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:       
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP



def setUp(args):
    global localAddr
    localAddr = (extract_ip(), args.port)
    global name
    global model_path
    model_path = os.path.dirname(os.path.realpath(__file__))
    model_path = os.path.join(model_path, "sc_proj_3_model.pkl")
    name = str(args.name)
    if args.model is not None:
        model_path = args.model
    setUpLogs(name)
    setLeader(localAddr)

    socket.SO_REUSEPORT = socket.SO_REUSEADDR

    nodeSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
    nodeSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) #not sure if still needed, using anyway
    # Enable broadcasting mode
    nodeSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    nodeSocket.bind(("", args.port))
    nodeSocket.settimeout(0.1) #tune this later

    return nodeSocket

def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='port of this node', type=int)
    parser.add_argument('--leader', help='is this node a leader? (y/n)', type=str)
    parser.add_argument('--name', help='name of this node', type=str)
    parser.add_argument('--model', help='Path to model', type=str)
    args = parser.parse_args()

    if args.name is None:
        print("please specify the name of the node")
        exit(1)
    
    if args.port is None:
        print("please specify the port of the node")
        exit(1)
    
    if args.port < 33000 or args.port > 34000:
        print("please specify ports between 33000-34000")
        exit(1)
    else:
        log = "Starting on Port:".format(args.port)
        print(log)
    
    if args.leader == 'y':
        log = 'Starting as Leader!'
        print(log)

    else:
        log = 'Starting node as follower!'
        print(log)
    return args
    

def main():
    args = getArgs()
    nodeSocket = setUp(args)
    nodeLoop(nodeSocket, args)

if __name__ == '__main__':
    main()