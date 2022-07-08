# In this script the hosts are stored

import socket

# get the IP-Adress of the machine
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
userIPAddress = sock.getsockname()[0]

"""
declaration of variables for encoding, decoding messages
for the address for multicasts
and for leader and neighbour
"""

buf_size = 1024
unicode = 'utf-8'
multicast_address = '224.0.0.0'
leader = ''
neighbour = ''
# definition of lists for clients and servers
server_list = []
client_list = []

# global state variables
client_running = False
network_changed = False
leader_crashed = ''
replica_crashed = ''
