
import sys
import selectors
import json
import io
import struct
import socket
import traceback

import datetime
import time
import random
import os

import libclient
import battleshipServer

class Server:
    def __init__(self, host, port):
        self.sel = selectors.DefaultSelector()
        self.host = host
        self.port = port
        self.sessionIDs = {}
        self.clientSIDs = {}
        self.clients = {}
        self.lobbies = {}
        self.games = {}
        
    def start_connection(self, host, port, message):
        addr = (host, port)
        print("starting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        message = libclient.Message(self.sel, sock, addr, message)
        self.sel.register(sock, events, data=message)
    
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
                events = self.sel.select(timeout=0.1)
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
    
    def save_client_info(self, clientInfo):
        jsonName = "server_data/client_info/" + clientInfo["username"] + ".json"
        if os.path.exists(jsonName):
            os.remove(jsonName)
        f = open(jsonName, "a")
        f.write(json.dumps(clientInfo))
        f.close()
        
    def read_client_info(self, username):
        jsonName = "server_data/client_info/" + username + ".json"
        try:
            with open(jsonName, 'r') as file:
                data = json.load(file)
            return data
        except Exception as e:
            return None
    
    def register_client(self, username, password):
        defaultBio = "There was an age undreamed-of... and unto this," + username.upper() + "!"
        clientInfo = dict(
                             username=username,
                             password=password,
                             sessionID=None,
                             bio=defaultBio,
                             registrationDate=datetime.date.today().strftime("%B %d, %Y")
                           )
        try:
            self.save_client_info(clientInfo)
            self.read_client_info(clientInfo["username"])
        except Exception as e:
            print("\n\n" + e + "\n\n")
            
    def client_registered(self, username):
        jsonName = "server_data/client_info/" + username + ".json"
        if os.path.exists(jsonName):
            return True
        else:
            return False
        
    def verify_client(self, username, password):
        if self.client_registered(username):
            clientInfo = self.read_client_info(username)
            if clientInfo["password"] == password:
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
        self.sessionIDs[str(sessionID)] = username
        self.clientSIDs[username] = sessionID
        self.clients[str(sessionID)] = {
            'username': username,
            'lobbyName': None,
            'inGame': False
        }
    
    def logged_in(self, username):
        if username in self.clientSIDs:
            return True
        else:
            return False
    
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
                    if self.client_registered(username):
                        answer = dict(registered=True)
                        reply["reply"] = answer
                    else:
                        self.register_client(username, password)
                        answer = dict(registered=True)
                        reply["reply"] = answer
                except Exception as e:
                    print("\n" + print(traceback.format_exc()) +"\n")
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
                        if not self.logged_in(username):
                            self.connect_user(username)
                        answer = dict(loggedIn=True, badLogin=False, sessionID=self.clientSIDs[username])
                        reply["reply"] = answer
                    else:
                        answer = dict(loggedIn=False, badLogin=True, sessionID=None)
                        reply["reply"] = answer
                except Exception as e:
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer
                
            elif action == "logout":
                try:
                    sessionID = request.get("sessionID")
                except Exception as e:
                    answer = dict(badRequest=True)
                    reply["reply"] = answer
                    return reply
                try:
                    if str(sessionID) in self.sessionIDs:
                        del self.clientSIDs[self.sessionIDs[str(sessionID)]]
                        del self.sessionIDs[str(sessionID)]
                        lobbyName = self.clients.get(str(sessionID)).get('lobbyName')
                        try:
                            del self.lobbies[lobbyName]
                        except:
                            pass
                        del self.clients[str(sessionID)]
                        answer = dict(loggedOut=True, unknownSessionID=False)
                        reply["reply"] = answer
                    else:
                        answer = dict(loggedOut=False, unknownSessionID=True)
                        reply["reply"] = answer
                except Exception as e:
                    print("\n" + print(traceback.format_exc()) +"\n")
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
                    print("\n" + print(traceback.format_exc()) +"\n")
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer

            elif action == "ping":
                try:
                    answer = dict(pinged=True)
                    reply["reply"] = answer
                except Exception as e:
                    print("\n" + print(traceback.format_exc()) +"\n")
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer
                    
            elif action == "create_lobby":
                try:
                    sessionID = request.get("sessionID")
                    lobbyName = request.get("lobbyName")
                except Exception as e:
                    answer = dict(badRequest=True)
                    reply["reply"] = answer
                    return reply
                try:
                    if str(sessionID) in self.sessionIDs:
                        if lobbyName not in self.lobbies:
                            self.clients.get(str(sessionID))['lobbyName'] = lobbyName
                            self.lobbies[lobbyName] = {
                                'gameStarted': False,
                                'player1': self.sessionIDs.get(str(sessionID)),
                                'player2': None,
                                'gameID': None,
                            }
                            answer = dict(lobbyCreated=True, invalidSessionID=False)
                        else:
                            answer = dict(lobbyCreated=False, invalidSessionID=False, lobbyAlreadyExists=True)
                    else:
                        answer = dict(lobbyCreated=False, invalidSessionID=True)
                    reply["reply"] = answer
                except Exception as e:
                    print("\n" + print(traceback.format_exc()) +"\n")
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer
                    
            elif action == "join_lobby":
                try:
                    sessionID = request.get("sessionID")
                    lobbyName = request.get("lobbyName")
                except Exception as e:
                    answer = dict(badRequest=True)
                    reply["reply"] = answer
                    return reply
                try:
                    if str(sessionID) in self.clients:
                        if lobbyName in self.lobbies:
                            lobby = self.lobbies.get(lobbyName)
                            if lobby['player1'] is None:
                                raise ValueError("Something went wrong on the server side. Please try again.")
                            if lobby['player2'] is None:
                                lobby['player2'] = self.clients.get(str(sessionID)).get('username')
                                self.clients.get(str(sessionID))['lobbyName'] = lobbyName
                                answer = dict(invalidSessionID=False, lobbyExists=True, lobbyFull=False, lobbyJoined=True)
                            else:
                                answer = dict(invalidSessionID=False, lobbyExists=True, lobbyFull=True, lobbyJoined=False)
                        else:
                            answer = dict(invalidSessionID=False, lobbyExists=False)
                    else:
                        answer = dict(invalidSessionID=True)
                    reply["reply"] = answer
                except Exception as e:
                    print("\n" + print(traceback.format_exc()) +"\n")
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer
                    
            elif action == "lobby_end":
                try:
                    sessionID = request.get("sessionID")
                except Exception as e:
                    answer = dict(badRequest=True)
                    reply["reply"] = answer
                    return reply
                try:
                    if str(sessionID) in self.clients:
                        if not self.clients.get(str(sessionID)).get('lobbyName') is None:
                            lobbyName = self.clients.get(str(sessionID)).get('lobbyName')
                            if lobbyName in self.games:
                                del self.games[lobbyName]
                            if lobbyName in self.lobbies:
                                del self.lobbies[lobbyName]
                            self.clients.get(str(sessionID))['lobbyName'] = None
                        answer = dict(invalidSessionID=False, notInLobby=True)
                    else:
                        answer = dict(invalidSessionID=True)
                    reply["reply"] = answer
                except Exception as e:
                    print("\n" + print(traceback.format_exc()) +"\n")
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer
                    
            elif action == "get_lobby_status":
                try:
                    lobbyName = request.get("lobbyName")
                except Exception as e:
                    answer = dict(badRequest=True)
                    reply["reply"] = answer
                    return reply
                try:
                    if lobbyName in self.lobbies:
                        lobby = self.lobbies.get(lobbyName)
                        answer = dict(lobbyExists=True, lobby=lobby)
                    else:
                        answer = dict(lobbyExists=True, lobby=None)
                    reply["reply"] = answer
                except Exception as e:
                    print("\n" + print(traceback.format_exc()) +"\n")
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer
                    
            elif action == "get_client_status":
                try:
                    sessionID = request.get("sessionID")
                except Exception as e:
                    answer = dict(badRequest=True)
                    reply["reply"] = answer
                    return reply
                try:
                    if str(sessionID) in self.clients:
                        answer = dict(invalidSessionID=False, clientStatus=self.clients.get(str(sessionID)))
                    else:
                        answer = dict(invalidSessionID=True)
                    reply["reply"] = answer
                except Exception as e:
                    print("\n" + print(traceback.format_exc()) +"\n")
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer
                    
            elif action == "game_start":
                try:
                    sessionID = request.get("sessionID")
                except Exception as e:
                    answer = dict(badRequest=True)
                    reply["reply"] = answer
                    return reply
                try:
                    if str(sessionID) in self.clients:
                        if not self.clients.get(str(sessionID)).get('lobbyName') is None:
                            lobby = self.lobbies.get(self.clients.get(str(sessionID)).get('lobbyName'))
                            if not lobby.get('gameStarted'):
                                if not lobby.get('player2') is None and not lobby.get('player1') is None:
                                    lobbyName = self.clients.get(str(sessionID)).get('lobbyName')
                                    lobby['gameStarted'] = True
                                    self.games[lobbyName] = battleshipServer.Referee(P1_name=lobby.get('player1'), P2_name=lobby.get('player2'))
                                    answer = dict(invalidSessionID=False, notInLobby=False, alreadyStarted=False, gameStarted=True)
                                else:
                                    answer = dict(invalidSessionID=False, notInLobby=False, alreadyStarted=False, gameStarted=False)
                            else:
                                answer = dict(invalidSessionID=False, notInLobby=False, alreadyStarted=True, gameStarted=True)
                        else:
                            answer = dict(invalidSessionID=False, notInLobby=True)
                    else:
                        answer = dict(invalidSessionID=True)
                    reply["reply"] = answer
                except Exception as e:
                    print("\n" + print(traceback.format_exc()) +"\n")
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer
                    
            elif action == "game_over":
                try:
                    sessionID = request.get("sessionID")
                except Exception as e:
                    answer = dict(badRequest=True)
                    reply["reply"] = answer
                    return reply
                try:
                    if str(sessionID) in self.clients:
                        if not self.clients.get(str(sessionID)).get('lobbyName') is None:
                            lobby = self.lobbies.get(self.clients.get(str(sessionID)).get('lobbyName'))
                            if lobby.get('gameStarted'):
                                lobbyName = self.clients.get(str(sessionID)).get('lobbyName')
                                gameOver = self.games.get(lobbyName).game_over
                                if gameOver == True:
                                    lobbyName = self.clients.get(str(sessionID)).get('lobbyName')
                                    winner = self.games.get(lobbyName).winner
                                    answer = dict(invalidSessionID=False, notInLobby=False, gameStarted=True, gameOver=gameOver, winner=winner)
                                else:
                                    answer = dict(invalidSessionID=False, notInLobby=False, gameStarted=True, gameOver=False)
                            else:
                                answer = dict(invalidSessionID=False, notInLobby=False, gameStarted=False)
                        else:
                            answer = dict(invalidSessionID=False, notInLobby=True)
                    else:
                        answer = dict(invalidSessionID=True)
                    reply["reply"] = answer
                except Exception as e:
                    print("\n" + print(traceback.format_exc()) +"\n")
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer

            elif action == "turn":
                try:
                    sessionID = request.get("sessionID")
                except Exception as e:
                    answer = dict(badRequest=True)
                    reply["reply"] = answer
                    return reply
                try:
                    if str(sessionID) in self.clients:
                        if not self.clients.get(str(sessionID)).get('lobbyName') is None:
                            lobby = self.lobbies.get(self.clients.get(str(sessionID)).get('lobbyName'))
                            if lobby.get('gameStarted'):
                                lobbyName = self.clients.get(str(sessionID)).get('lobbyName')
                                turn = self.games.get(lobbyName).turn
                                answer = dict(invalidSessionID=False, notInLobby=False, gameStarted=True, turn=turn)
                            else:
                                answer = dict(invalidSessionID=False, notInLobby=False, gameStarted=False)
                        else:
                            answer = dict(invalidSessionID=False, notInLobby=True)
                    else:
                        answer = dict(invalidSessionID=True)
                    reply["reply"] = answer
                except Exception as e:
                    print("\n" + print(traceback.format_exc()) +"\n")
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer
                    
            elif action == "incoming_strike":
                try:
                    sessionID = request.get("sessionID")
                except Exception as e:
                    answer = dict(badRequest=True)
                    reply["reply"] = answer
                    return reply
                try:
                    if str(sessionID) in self.clients:
                        if not self.clients.get(str(sessionID)).get('lobbyName') is None:
                            lobby = self.lobbies.get(self.clients.get(str(sessionID)).get('lobbyName'))
                            username = self.clients.get(str(sessionID)).get('username')
                            print("\n\n\n" + username + "\n\n")
                            if lobby.get('gameStarted'):
                                lobbyName = self.clients.get(str(sessionID)).get('lobbyName')
                                location = self.games.get(lobbyName).getIncomingStrike(username)
                                answer = dict(invalidSessionID=False, notInLobby=False, gameStarted=True, location=location)
                            else:
                                answer = dict(invalidSessionID=False, notInLobby=False, gameStarted=False)
                        else:
                            answer = dict(invalidSessionID=False, notInLobby=True)
                    else:
                        answer = dict(invalidSessionID=True)
                    reply["reply"] = answer
                except Exception as e:
                    print("\n" + print(traceback.format_exc()) +"\n")
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer
                    
            elif action == "result_outgoing_strike":
                try:
                    sessionID = request.get("sessionID")
                except Exception as e:
                    answer = dict(badRequest=True)
                    reply["reply"] = answer
                    return reply
                try:
                    if str(sessionID) in self.clients:
                        if not self.clients.get(str(sessionID)).get('lobbyName') is None:
                            lobby = self.lobbies.get(self.clients.get(str(sessionID)).get('lobbyName'))
                            username = self.clients.get(str(sessionID)).get('username')
                            print("\n\n\n" + username + "\n\n")
                            if lobby.get('gameStarted'):
                                lobbyName = self.clients.get(str(sessionID)).get('lobbyName')
                                result, shipStats = self.games.get(lobbyName).getResultOfPreviousStrike(username)
                                answer = dict(invalidSessionID=False, notInLobby=False, gameStarted=True, result=result, shipStats=shipStats)
                            else:
                                answer = dict(invalidSessionID=False, notInLobby=False, gameStarted=False)
                        else:
                            answer = dict(invalidSessionID=False, notInLobby=True)
                    else:
                        answer = dict(invalidSessionID=True)
                    reply["reply"] = answer
                except Exception as e:
                    print("\n" + print(traceback.format_exc()) +"\n")
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer
                    
            elif action == "end_turn":
                try:
                    sessionID = request.get("sessionID")
                    result = request.get("result")
                    outgoing = request.get("outgoing")
                    shipStats = request.get("shipStats")
                except Exception as e:
                    answer = dict(badRequest=True)
                    reply["reply"] = answer
                    return reply
                try:
                    if str(sessionID) in self.clients:
                        if not self.clients.get(str(sessionID)).get('lobbyName') is None:
                            lobby = self.lobbies.get(self.clients.get(str(sessionID)).get('lobbyName'))
                            username = self.clients.get(str(sessionID)).get('username')
                            if lobby.get('gameStarted'):
                                lobbyName = self.clients.get(str(sessionID)).get('lobbyName')
                                self.games.get(lobbyName).setResultOfStrike(username, result, shipStats)
                                self.games.get(lobbyName).setOutgoingStrike(username, outgoing)
                                self.games.get(lobbyName).switchTurns()
                                answer = dict(invalidSessionID=False, notInLobby=False, gameStarted=True, turnEnded=True)
                            else:
                                answer = dict(invalidSessionID=False, notInLobby=False, gameStarted=False, turnEnded=False)
                        else:
                            answer = dict(invalidSessionID=False, notInLobby=True, turnEnded=False)
                    else:
                        answer = dict(invalidSessionID=True)
                    reply["reply"] = answer
                except Exception as e:
                    print("\n" + print(traceback.format_exc()) +"\n")
                    answer = dict(internalServerError=True)
                    reply["reply"] = answer

            else:
                answer = dict(badRequest=True)
                reply["reply"] = answer
                
        except Exception as e:
            print("\n" + str(e) + "\n")
            answer = dict(badRequest=True)
            reply["reply"] = answer
        
        reply["reply"] = json.dumps(reply["reply"])
        
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
