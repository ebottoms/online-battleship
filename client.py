#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import struct

import libclient

sel = selectors.DefaultSelector()

text_json_commands = ["search", "register", "recognize"]

def create_request(action, values):
    if (action == "register"):
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, username=values[0], password=values[1]),
        )
    elif (action == "login"):
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, username=values[0], password=values[1]),
        )
    elif (action == "logout"):
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, sessionID=values[0]),
        )
    elif (action == "join"):
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, gameID=values[0], password=values[1]),
        )
    elif (action == "chat"):
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action, sessionID=values[0], message=values[1]),
        )
    elif (action == "quit"):
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action),
        )
    elif (action == "stillAlive"):
        return dict(
            type="text/json",
            encoding="utf-8",
            content=dict(action=action),
        )
    elif (action == "double") or (action == "negate"):
        return dict(
            type="binary/custom-client-binary-type",
            encoding="binary",
            content=struct.pack(">6si", action.encode(encoding="utf-8"), int(values[0])),
        )
    else:
        return dict(
            type="binary/custom-client-binary-type",
            encoding="binary",
            content=bytes(action + values[0], encoding="utf-8"),
        )


def start_connection(host, port, request):
    addr = (host, port)
    print("starting connection to", addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)


if len(sys.argv) <= 5:
    print("usage:", sys.argv[0], "<host> <port> <action> <value1> <value2> ... <valueN>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
action, values = sys.argv[3], sys.argv[4:]
print(action)
request = create_request(action, values)
start_connection(host, port, request)

try:
    while True:
        events = sel.select(timeout=1)
        for key, mask in events:
            message = key.data
            try:
                message.process_events(mask)
            except Exception:
                print(
                    "main: error: exception for",
                    f"{message.addr}:\n{traceback.format_exc()}",
                )
                message.close()
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
