#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import struct

import datetime

import libclient
import clientInterface

client = clientInterface.UI()

if len(sys.argv) == 1:
    host, port, action, values = None, None, None, None
elif len(sys.argv) <= 3:
    print("Usage: <host> <port> <action> <value1> <value2> ... <valueN>")
    sys.exit()
else:
    host, port, action, values = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4:]
    
client.start(host, port, action, values)