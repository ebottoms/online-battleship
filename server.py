#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback

import libserver

clients = {}

if len(sys.argv) != 3:
    print("usage:", sys.argv[0], "<host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
server = libserver.Server(host, port)

server.run()