
import sys
import selectors
import json
import io
import traceback
import struct
import socket
import time

class Client:
    def __init__(self):
        self.sel = None

    text_json_commands = ["search", "register", "recognize"]

    def create_request(self, action, values):
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
        elif (action == "ping"):
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action),
            )
        elif (action == "create_lobby"):
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action, sessionID=values[0], lobbyName=values[1]),
            )
        elif (action == "join_lobby"):
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action, sessionID=values[0], lobbyName=values[1]),
            )
        elif (action == "lobby_end"):
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action, sessionID=values[0]),
            )
        elif (action == "get_lobby_status"):
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action, lobbyName=values[0]),
            )
        elif (action == "get_client_status"):
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action, sessionID=values[0]),
            )
        elif (action == "game_start"):
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action, sessionID=values[0]),
            )
        elif (action == "game_over"):
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action, sessionID=values[0]),
            )
        elif (action == "turn"):
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action, sessionID=values[0]),
            )
        elif (action == "incoming_strike"):
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action, sessionID=values[0]),
            )
        elif (action == "result_outgoing_strike"):
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action, sessionID=values[0]),
            )
        elif (action == "end_turn"):
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action, sessionID=values[0], result=values[1], outgoing=values[2], shipStats=values[3]),
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


    def start_connection(self, host, port, request):
        addr = (host, port)
        #print("starting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        message = Message(self.sel, sock, addr, request)
        self.sel.register(sock, events, data=message)
        

    def send(self, host, port, action, values=None):
        self.sel = selectors.DefaultSelector()
        request = self.create_request(action, values)
        self.start_connection(host, port, request)
        response = None
        try:
            while True:
                events = self.sel.select(timeout=1)
                for key, mask in events:
                    message = key.data
                    try:
                        message.process_events(mask)
                        if message.exportResponse == True:
                            response = message.response
                    except Exception:
                        #print(
                        #    "main: error: exception for",
                        #    f"{message.addr}:\n{traceback.format_exc()}",
                        #)
                        #time.sleep(10)
                        message.close()
                # Check for a socket being monitored to continue.
                if not self.sel.get_map():
                    break
                
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()

        return response


class Message:
    def __init__(self, selector, sock, addr, request):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.request = request
        self._recv_buffer = b""
        self._send_buffer = b""
        self._request_queued = False
        self._jsonheader_len = None
        self.jsonheader = None
        self.response = None
        self.exportResponse = False

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
            #print("sending", repr(self._send_buffer), "to", self.addr)
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]

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

    def _process_response_json_content(self):
        content = self.response
        #reply = content.get("reply")
        self.exportResponse = True

    def _process_response_binary_content(self):
        content = self.response
        #print(f"got response: {repr(content)}")
        if b"result" in content:
            value = struct.unpack(">i", content[6:])[0]
            #print('result:', int(value))

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
            if self.response is None:
                self.process_response()

    def write(self):
        if not self._request_queued:
            self.queue_request()

        self._write()

        if self._request_queued:
            if not self._send_buffer:
                # Set selector to listen for read events, we're done writing.
                self._set_selector_events_mask("r")

    def close(self):
        #print("closing connection to", self.addr)
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

    def queue_request(self):
        content = self.request["content"]
        content_type = self.request["type"]
        content_encoding = self.request["encoding"]
        if content_type == "text/json":
            req = {
                "content_bytes": self._json_encode(content, content_encoding),
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        else:
            req = {
                "content_bytes": content,
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        message = self._create_message(**req)
        self._send_buffer += message
        self._request_queued = True

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

    def process_response(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.response = self._json_decode(data, encoding)
            #print("received response", repr(self.response), "from", self.addr)
            self._process_response_json_content()
        else:
            # Binary or unknown content-type
            self.response = data
            #print(
            #    f'received {self.jsonheader["content-type"]} response from',
            #    self.addr,
            #)
            self._process_response_binary_content()
        # Close when response has been processed
        self.close()
