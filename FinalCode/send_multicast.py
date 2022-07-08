# this is a Multicast Sender

import socket
import sys
import struct
import pickle

from time import sleep
import hosts

# create Port for multicast
multicast_port = 10000

# get the Multicast IP
multicast_address = (hosts.multicast_address, multicast_port)

# create the UDP Socket for Multicast
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# set the timeout to the Socket
sock.settimeout(1)

# set the time-to-live for messages to 1 so they do not go past the local network segment
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)


# used from Server
def send_req_to_multicast():
    sleep(1)

    # send own variables from the hosts to the Multicast Receivers(Servers)
    # pickle used for sending data as Lists
    message = pickle.dumps([hosts.server_list, hosts.leader, hosts.leader_crashed, hosts.replica_crashed,
                            str(hosts.client_list)])
    sock.sendto(message, multicast_address)
    print(f'\n[MULTICAST SENDER {hosts.userIPAddress}] Sending data to Multicast Receivers {multicast_address}',
          file=sys.stderr)

    # if Multicast Receiver exists then return True otherwise return False
    try:
        sock.recvfrom(hosts.buf_size)

        if hosts.leader == hosts.userIPAddress:
            print(f'[MULTICAST SENDER {hosts.userIPAddress}] All Servers have been updated\n',
                  file=sys.stderr)
        return True

    except socket.timeout:
        print(f'[MULTICAST SENDER {hosts.userIPAddress}] Multicast Receiver not detected',
              file=sys.stderr)
        return False


# used from Clients
def send_join_request():

    print(f'\n[MULTICAST SENDER {hosts.userIPAddress}] Sending join chat request to Multicast Address {multicast_address}',
          file=sys.stderr)
    message = pickle.dumps(['JOIN', '', '', ''])
    sock.sendto(message, multicast_address)

    # try to get Server Leader
    try:
        data, address = sock.recvfrom(hosts.buf_size)
        hosts.leader = pickle.loads(data)[0]
        return True

    except socket.timeout:
        print(f'[MULTICAST SENDER {hosts.userIPAddress}] Multicast Receiver not detected -> Chat Server is offline.',
              file=sys.stderr)
        return False
