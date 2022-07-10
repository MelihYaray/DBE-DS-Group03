# From this Script the MultiClient can be instanciated

import socket
import threading
import os

from time import sleep
import hosts
import send_multicast

# create Port for server
server_port = 10001

# standardized for creating and starting Threads


def thread(target, args):
    thread = threading.Thread(target=target, args=args)
    thread.daemon = True
    thread.start()


# function for sending messages to the Server
def send_msg():
    global soc

    while True:
        message = input("")

        try:
            send_message = message.encode(hosts.unicode)
            soc.send(send_message)

        except Exception as e:
            print(e)
            break


# function for receiving messages from the Server
def receive_msg():
    global soc

    while True:

        try:
            data = soc.recv(hosts.buf_size)
            print(data.decode(hosts.unicode))

            # if connection to server is lost (in case of server crash)
            if not data:
                print("\nSorry, the Chat server is currently not available."
                      "Please wait for reconnection with new server leader.")
                soc.close()
                sleep(3)

                # Start reconnecting to new server leader
                connect()

        except Exception as e:
            print(e)
            break


# function for creating Client socket and establishing connection to Server Leader
def connect():
    global soc

    # creating TCP Socket for Client
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # send a join request to Multicast Address for receiving the current Server Leader address
    # if there is no response from the Server Leader, value False will be returned
    server_exist = send_multicast.send_join_request()

    if server_exist:
        # assign Server Leader address
        leader_address = (hosts.leader, server_port)
        print(f'This is the server leader: {leader_address}')

        # connect to Server Leader
        soc.connect(leader_address)
        soc.send('JOIN'.encode(hosts.unicode))
        print("You´ve entered the Chat Room.\nYou can start chatting now.")

    # if there is no Server available, exit the script
    else:
        print("Please try to enter later again.")
        os._exit(0)


# main Thread
if __name__ == '__main__':
    try:
        print("You try to enter the chat room.")

        # Connect to Server Leader
        connect()

        # Start Threads for sending and receiving messages from other chat participants
        thread(send_msg, ())
        thread(receive_msg, ())

        while True:
            pass

    except KeyboardInterrupt:
        print("\nYou left the chat room")
