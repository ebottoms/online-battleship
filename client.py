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
client.start()