# this is a Multicast Receiver

import socket
import sys
import struct
import pickle

import hosts

# create Port for multicast
multicast = 10000

# get the Multicast IP
multicast_ip = hosts.multicast_address
server_address = ('', multicast)

# create the UDP Socket for Multicast
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# used from Servers
def start_multicast_rec():

    # bind the Server address
    sock.bind(server_address)

    # tell the operating system to add the socket to the multicast group on all interfaces
    group = socket.inet_aton(multicast_ip)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f'\n[MULTICAST RECEIVER {hosts.userIPAddress}] Starting UDP Socket and listening on Port {multicast}',
          file=sys.stderr)

    # receive/respond loop
    while True:
        try:
            data, address = sock.recvfrom(hosts.buf_size)
            print(f'\n[MULTICAST RECEIVER {hosts.userIPAddress}] Received data from {address}\n',
                  file=sys.stderr)

            # used from Server Leader if a join message was sent from a Chat Client
            if hosts.leader == hosts.userIPAddress and pickle.loads(data)[0] == 'JOIN':

                # answer Chat Client with Server Leader address
                message = pickle.dumps([hosts.leader, ''])
                sock.sendto(message, address)
                print(f'[MULTICAST RECEIVER {hosts.userIPAddress}] Client {address} wants to join the Chat Room\n',
                      file=sys.stderr)

            # used from Server Leader if a Server Replica joined
            if len(pickle.loads(data)[0]) == 0:
                hosts.server_list.append(
                    address[0]) if address[0] not in hosts.server_list else hosts.server_list
                sock.sendto('ack'.encode(hosts.unicode), address)
                hosts.network_changed = True

            # used from Server Replicas to update the own variables or if a Server Replica crashed
            elif pickle.loads(data)[1] and hosts.leader != hosts.userIPAddress or pickle.loads(data)[3]:
                hosts.server_list = pickle.loads(data)[0]
                hosts.leader = pickle.loads(data)[1]
                hosts.client_list = pickle.loads(data)[4]
                print(f'[MULTICAST RECEIVER {hosts.userIPAddress}] All Data have been updated',
                      file=sys.stderr)

                sock.sendto('ack'.encode(hosts.unicode), address)
                hosts.network_changed = True

        except KeyboardInterrupt:
            print(f'[MULTICAST RECEIVER {hosts.userIPAddress}] Closing UDP Socket',
                  file=sys.stderr)
