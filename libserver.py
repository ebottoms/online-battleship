
import sys
import selectors
import json
import io
import struct
import socket
import traceback

import datetime
import random

class Server:
    def __init__(self, host, port):
        self.sel = selectors.DefaultSelector()
        self.host = host
        self.port = port
        self.clients = {}
        self.sessionIDs = {}
    
    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print("accepted connection from", addr)
        conn.setblocking(False)
        message = Message(self.sel, conn, addr, self)
        self.sel.register(conn, selectors.EVENT_READ, data=message)
        
    def run(self):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        lsock.bind((self.host, self.port))
        lsock.listen()
        print("listening on", (self.host, self.port))
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)

        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
                        except Exception:
                            print(
                                "main: error: exception for",
                                f"{message.addr}:\n{traceback.format_exc()}",
                            )
                            message.close()
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()
            
    def register_client(self, username, password):
        default_bio = "There was an age undreamed-of... and unto this," + username.upper() + "... "
        sessionID = random.randrange(1000000)
        self.clients[username] = dict(
                                        username=username,
                                        password=password,
                                        sessionID=None,
                                        bio=default_bio,
                                        registrationDate=datetime.date.today().strftime("%B %d, %Y")
                                      )
        
    def verify_client(self, username, password):
        if username in self.clients:
            if self.clients[username]["password"] == password:
                return True
        return False
    
    def user_connected(self, sessionID):
        if sessionID in self.sessionIDs:
            return True
        return False
    
    def connect_user(self, username):
        sessionID = random.randrange(1000000)
        while sessionID in self.sessionIDs:
            sessionID = random.randrange(1000000)
        self.clients[username]["sessionID"] = sessionID
        self.sessionIDs[str(sessionID)] = sessionID
        
        return sessionID
    
    def get_server_reply(self, request):
        reply = dict(request=request, reply=None)
        try:
            action = request.get("action")

            if action == "register":
                try:
                    username = request.get("username")
                    password = request.get("password")
                except Exception as e:
                    answer = dict(badRequest=True)
                    reply["reply"] = answer
                    return reply
                try:
                    if username in self.clients:
                        answer = dict(registered=True)
                        reply["reply"] = answer
                    else:
                        self.register_client(username, password)
                        answer = dict(registered=True)
                        reply["reply"] = answer
                except Exception as e:
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer

            elif action == "login":
                try:
                    username = request.get("username")
                    password = request.get("password")
                except Exception as e:
                    answer = dict(badRequest=True)
                    reply["reply"] = answer
                    return reply
                try:
                    if self.verify_client(username, password):
                        if self.clients[username]["sessionID"] == None:
                            sessionID = self.connect_user(username)
                            answer = dict(loggedIn=True, badLogin=False, sessionID=sessionID)
                            reply["reply"] = answer
                        else:
                            answer = dict(loggedIn=True, badLogin=False, sessionID=None)
                            reply["reply"] = answer
                    else:
                        answer = dict(loggedIn=False, badLogin=True, sessionID=None)
                        reply["reply"] = answer
                except Exception as e:
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer
                
            elif action == "logout":
                try:
                    username = request.get("username")
                    sessionID = request.get("sessionID")
                except Exception as e:
                    answer = dict(badRequest=True)
                    reply["reply"] = answer
                    return reply
                try:
                    if str(sessionID) in self.sessionIDs:
                        self.clients[username]["sessionID"] = None
                        del self.sessionIDs[sessionID]
                        answer = dict(loggedOut=True, unknownSessionID=False)
                        reply["reply"] = answer
                    else:
                        answer = dict(loggedOut=False, unknownSessionID=True)
                        reply["reply"] = answer
                except Exception as e:
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer
                
            elif action == "chat":
                try:
                    sessionID = request.get("sessionID")
                    message = request.get("message")
                except Exception as e:
                    answer = dict(badRequest=True)
                    reply["reply"] = answer
                    return reply
                try:
                    if self.user_connected(sessionID):
                        answer = dict(messageSent=True, unknownSessionID=False)
                        reply["reply"] = answer
                    else:
                        answer = dict(messageSent=False, unknownSessionID=True)
                        reply["reply"] = answer
                except Exception as e:
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer

            else:
                answer = dict(badRequest=True)
                reply["reply"] = answer
                
        except Exception as e:
            answer = dict(badRequest=True)
            reply["reply"] = answer
        
        return reply

class Message:
    def __init__(self, selector, sock, addr, server_handle):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False
        self.server_handle = server_handle

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            print("sending", repr(self._send_buffer), "to", self.addr)
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
                if sent and not self._send_buffer:
                    self.close()

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(
        self, *, content_bytes, content_type, content_encoding
    ):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def _create_response_json_content(self):
        content = self.server_handle.get_server_reply(self.request)
        content_encoding = "utf-8"
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        
        return response

    def _create_response_binary_content(self):
        response = None
        action = self.request[:6]
        if (action == b"double") or (action == b"negate"):
            value = struct.unpack(">i", self.request[6:])[0]
            if action == b"double":
                value = int(value) * 2
                result = struct.pack(">6si", b"result", value)
                response = {
                    "content_bytes": result,
                    "content_type": "binary/custom-server-binary-type",
                    "content_encoding": "binary",
                }
            else:
                value = int(value) * -1
                result = struct.pack(">6si", b"result", value)
                response = {
                    "content_bytes": result,
                    "content_type": "binary/custom-server-binary-type",
                    "content_encoding": "binary",
                }
        else:
            response = {
                "content_bytes": b"First 10 bytes of request: "
                + self.request[:10],
                "content_type": "binary/custom-server-binary-type",
                "content_encoding": "binary",
            }
        return response

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.request is None:
                self.process_request()

    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()

        self._write()

    def close(self):
        print("closing connection to", self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                f"error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )

        try:
            self.sock.close()
        except OSError as e:
            print(
                f"error: socket.close() exception for",
                f"{self.addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def process_request(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = self._json_decode(data, encoding)
            print("received request", repr(self.request), "from", self.addr)
        else:
            # Binary or unknown content-type
            self.request = data
            print(
                f'received {self.jsonheader["content-type"]} request from',
                self.addr,
            )
        # Set selector to listen for write events, we're done reading.
        self._set_selector_events_mask("w")

    def create_response(self):
        if self.jsonheader["content-type"] == "text/json":
            response = self._create_response_json_content()
        else:
            # Binary or unknown content-type
            response = self._create_response_binary_content()
        message = self._create_message(**response)
        self.response_created = True
        self._send_buffer += message
