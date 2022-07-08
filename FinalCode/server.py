# From this Script the MultiServer can be instanciated

import socket
import sys
import threading
import queue

import hosts
import rcv_multicast
import send_multicast
import heartbeat

"""
create Port for server
creating TCP Socket for Server
get the own IP from hosts
and create a First in First out queue for messages
"""
server_port = 10001
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host_address = (hosts.userIPAddress, server_port)
fifoQueue = queue.Queue()

# This function is used to print some information on the terminal


def printer():
    print(
        f'\nList of Servers: {hosts.server_list} --> The Leader is: {hosts.leader}')
    print(f'\nList of Clients: {hosts.client_list}')
    print(f'\nServers Neighbour ==> {hosts.neighbour}\n')


# standardized for creating and starting Threads
def thread(target, args):
    thread = threading.Thread(target=target, args=args)
    thread.daemon = True
    thread.start()


# send all messages waiting in the Queue to all Clients
def send_clients():
    message = ''
    while not fifoQueue.empty():
        message += f'{fifoQueue.get()}'
        message += '\n' if not fifoQueue.empty() else ''

    if message:
        for member in hosts.client_list:
            member.send(message.encode(hosts.unicode))


# handle all received messages from connected Clients
def client_handler(client, address):
    while True:
        try:
            data = client.recv(hosts.buf_size)

            # if Client is disconnected or lost the connection
            if not data:
                print(f'{address} disconnected')
                fifoQueue.put(f'\n{address} disconnected\n')
                hosts.client_list.remove(client)
                client.close()
                break

            fifoQueue.put(f'{address} said: {data.decode(hosts.unicode)}')
            print(f'Message from {address} ==> {data.decode(hosts.unicode)}')

        except Exception as e:
            print(e)
            break


# bind the TCP Server Socket and listen for connections
def start_binding():
    soc.bind(host_address)
    soc.listen()
    print(f'\nStarting and listening on IP {hosts.userIPAddress} and on PORT {server_port}',
          file=sys.stderr)

    while True:
        try:
            client, address = soc.accept()
            data = client.recv(hosts.buf_size)

            # used just for Chat-Clients (filter out heartbeat)
            if data:
                print(f'{address} connected')
                fifoQueue.put(f'\n{address} connected\n')
                hosts.client_list.append(client)
                thread(client_handler, (client, address))

        except Exception as e:
            print(e)
            break


# main Thread
if __name__ == '__main__':

    # trigger Multicast Sender to check if a Multicast Receiver with given Multicast Address from hosts exists
    multicast_receiver_exist = send_multicast.send_req_to_multicast()

    # append the own IP to the Server List and assign the own IP as the Server Leader
    if not multicast_receiver_exist:
        hosts.server_list.append(hosts.userIPAddress)
        hosts.leader = hosts.userIPAddress

    # calling functions as Threads
    thread(rcv_multicast.start_multicast_rec, ())
    thread(start_binding, ())
    thread(heartbeat.start_hb, ())

    # loop main Thread
    while True:
        try:
            # send Multicast Message to all Multicast Receivers (Servers)
            # used from Server Leader or if a Server Replica recognizes another Server Replica crash
            if hosts.leader == hosts.userIPAddress and hosts.network_changed or hosts.replica_crashed:
                if hosts.leader_crashed:
                    hosts.client_list = []
                send_multicast.send_req_to_multicast()
                hosts.leader_crashed = False
                hosts.network_changed = False
                hosts.replica_crashed = ''
                printer()

            # used from Server Replica to set the variable to False
            if hosts.leader != hosts.userIPAddress and hosts.network_changed:
                hosts.network_changed = False
                printer()

            # function to send the fifoQueue Queue messages
            send_clients()

        except KeyboardInterrupt:
            soc.close()
            print(
                f'\nClosing Server on IP {hosts.userIPAddress} with PORT {server_port}', file=sys.stderr)
            break
