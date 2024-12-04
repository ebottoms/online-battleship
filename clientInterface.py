import os
import sys
import time
import traceback
import json
import libclient
import battleshipClient

# GENERAL FUNCTIONS
def exit_program():
    print("Exiting the program...")
    sys.exit(0)
    
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')
    
def serverNotFoundMessage():
    clear_terminal()
    print("ERROR: Server could not be found!")
    print("Returning to FIND SERVER screen...")
    time.sleep(4)
    return

# USER INTERFACE CLASS
class UI:
    def __init__(self):
        self.serverFound = False
        self.connectedToServer = False
        self.inGame = False
        self.backend = libclient.Client()
        self.clientInfo = {
            'username': None,
            'sessionID': None
        }
        self.serverInfo = {
            'host': None,
            'port': None
        }
    
    # COMMUNICATION WITH BACKEND (libclient)
    def findServer(self, host, port):
        try:
            servReply = self.backend.send(host, port, action='ping')
            self.serverFound = json.loads(servReply.get('reply')).get('pinged')
            self.serverInfo['host'] = host
            self.serverInfo['port'] = port
        except:
            self.serverFound = False
            
    def login(self, username, password):
        host = self.serverInfo.get('host')
        port = self.serverInfo.get('port')
        try:
            servReply = self.backend.send(host, port, action='login', values=[username, password])
            sessionID = json.loads(servReply.get('reply')).get('sessionID')
        except Exception as e:
            raise ValueError("Server not found.")
        if sessionID is None:
            self.connectedToServer = False
        else:
            self.clientInfo['username'] = username
            self.clientInfo['sessionID'] = sessionID
            self.connectedToServer = True
            
    def endLobby(self):
        host = self.serverInfo.get('host')
        port = self.serverInfo.get('port')
        # Stop gameplay if in-game
        sessionID = self.clientInfo.get('sessionID')
        servReply = self.backend.send(host, port, 'lobby_end', [sessionID])
        lobbyExited = json.loads(servReply.get('reply')).get('notInLobby')
        self.inGame = False
        
    # PROMPTS AND DISPLAYS
    def findServerPrompt(self):
        clear_terminal()
        while not self.serverFound:
            host = None
            port = None
            inputValid = False
            while not inputValid:
                print("Enter Server IPv4 Address:")
                host = input()
                print()
                print("Enter Port Number:")
                try:
                    port = int(input())
                    inputValid = True
                except:
                    clear_terminal()
                    print("Port number has to be a number. Try again.")
            print()
            self.findServer(host, port)
            if not self.serverFound:
                clear_terminal()
                print("Could not find a server with IP address " + host + " and port " + str(port) + ".")
                print("Please try again.")
                
    def loginPrompt(self):
        clear_terminal()
        while not self.connectedToServer:
            print("Enter Your Username:")
            username = input()
            print()
            print("Enter Your Password:")
            password = input()
            print()
            self.login(username, password)
            if not self.connectedToServer:
                clear_terminal()
                print("Could not login with username " + username + " and password " + password + ".")
                print("Please try again.")
    
    def lobbyPrompt(self):
        clear_terminal()
        print("Enter \"C\" to create a new game lobby or \"J\" to join an existing game lobby.")
        success = False
        while not success:
            option = input()
            if option == 'C' or option == 'c':
                option = 'C'
                success = True
            elif option == 'J' or option == 'j':
                option = 'J'
                success = True
            else:
                clear_terminal()
                print("Try again. Enter \"C\" to create a new game lobby or \"J\" to join an existing game lobby.")
        clear_terminal()
        return option
    
    def createLobby(self):
        host = self.serverInfo.get('host')
        port = self.serverInfo.get('port')
        lobbyCreated = False
        while not lobbyCreated:
            print("Enter new lobby name:")
            lobbyName = input()
            try:
                servReply = self.backend.send(host, port, "create_lobby", [self.clientInfo.get('sessionID'), lobbyName])
                lobbyCreated = json.loads(servReply.get("reply")).get("lobbyCreated")
                self.lobbyName = lobbyName
            except Exception as e:
                print(traceback.format_exc())
            if not lobbyCreated:
                clear_terminal()
                print("Could not create lobby.")
                if "lobbyAlreadyExists" in json.loads(servReply.get("reply")):
                    print("Reason: Lobby with name \"" + lobbyName + "\" already exists.")
                else:
                    print("Reason: Invalid SessionID. Please restart your program.")
                    exit_program()
                print("Please try again.")
    
    def joinLobby(self):
        host = self.serverInfo.get('host')
        port = self.serverInfo.get('port')
        lobbyJoined = False
        while not lobbyJoined:
            print("Enter the name of the lobby you'd like to join:")
            lobbyName = input()
            try:
                servReply = self.backend.send(host, port, "join_lobby", [self.clientInfo.get('sessionID'), lobbyName])
                lobbyJoined = json.loads(servReply.get("reply")).get("lobbyJoined")
                self.lobbyName = lobbyName
            except Exception as e:
                print(traceback.format_exc())
            if not lobbyJoined:
                clear_terminal()
                print("Could not join lobby.")
                if json.loads(servReply.get("reply")).get("lobbyExists") is False:
                    print("Reason: Lobby with name \"" + lobbyName + "\" does not exist.")
                elif json.loads(servReply.get("reply")).get("lobbyFull") is True:
                    print("Reason: Lobby \"" + lobbyName + "\" is full.")
                else:
                    print("Reason: Unkonwn")
                print("Please try again.")
    
    def displayLobby(self):
        host = self.serverInfo.get('host')
        port = self.serverInfo.get('port')
        servReply1 = self.backend.send(host, port, "get_client_status", [self.clientInfo.get('sessionID')])
        lobbyName = json.loads(servReply1.get('reply')).get('clientStatus').get('lobbyName')
        if lobbyName is None:
            option = self.lobbyPrompt()
            if option == 'C':
                self.createLobby()
                return
            else:
                self.joinLobby()
                return
        clear_terminal()
        print("LOBBY: " + lobbyName)
        servReply1 = self.backend.send(host, port, "get_lobby_status", [lobbyName])
        lobby = json.loads(servReply1.get('reply')).get('lobby')
        if not lobby['player2'] is None and not lobby['player1'] is None:
            print("STATUS: Starting match...")
            print("PLAYERS: " + lobby['player1'] + "  VS  " + lobby['player2'])
            gameStarted = False
            while not gameStarted:
                servReply2 = self.backend.send(host, port, "game_start", [self.clientInfo.get('sessionID')])
                gameStarted = json.loads(servReply2.get('reply')).get('gameStarted')
                time.sleep(2)
            self.inGame = True
        else:
            print("STATUS: Waiting for Player 2 to join...")
            print("PLAYERS: " + self.clientInfo.get('username') + "  VS  " + "(Not Joined Yet)")
        time.sleep(3)
        
    def displayGame(self):
        host = self.serverInfo.get('host')
        port = self.serverInfo.get('port')
        
        # Initialize client game, send server list of boat positions
        game = battleshipClient.Game()
        game.initialize()
        
        win = False
        gameOver = False
        while not gameOver:
            time.sleep(2)
            # Ask server if game is still going
            servReply = self.backend.send(host, port, "game_over", [self.clientInfo.get('sessionID')])
            gameOver = json.loads(servReply.get('reply')).get('gameOver')
            if gameOver:
                winner = json.loads(servReply.get('reply')).get('winner')
                if winner == self.clientInfo.get('username'):
                    win = True
                continue
            # Ask server if it's my turn
            servReply = self.backend.send(host, port, "turn", [self.clientInfo.get('sessionID')])
            turn = json.loads(servReply.get('reply')).get('turn')
            # If it's my turn:
            if turn == self.clientInfo.get('username'):
                # Ask server for new incoming strike location
                servReply = self.backend.send(host, port, "incoming_strike", [self.clientInfo.get('sessionID')])
                incomingStrikeLocation = json.loads(servReply.get('reply')).get('location')
                # Ask for result of my previous outgoing strike (?) -> (x) or (!)
                servReply = self.backend.send(host, port, "result_outgoing_strike", [self.clientInfo.get('sessionID')])
                resultOutgoingStrike = json.loads(servReply.get('reply')).get('result')
                enemyShipStats = json.loads(servReply.get('reply')).get('shipStats')
                # Process result of my previous outgoing strike
                enemyHitMe, outgoingStrike, shipStats = game.takeMyTurn(incomingStrikeLocation, resultOutgoingStrike, enemyShipStats)
                # Tell server if I was hit, where I choose to strike next, and end my turn
                result = None
                if enemyHitMe:
                    result = '!'
                else:
                    result = 'x'
                servReply = self.backend.send(host, port, "end_turn", [self.clientInfo.get('sessionID'), result, outgoingStrike, shipStats])
                
        if win:
            clear_terminal()
            print('VICTORY!')
            time.sleep(1)
            print('Congratulations... ', end='')
            time.sleep(2)
            print('you live to fight another day, ' + self.clientInfo.get('username') + '.')
            servReply = self.backend.send(host, port, "get_client_status", [self.clientInfo.get('sessionID')])
            lobbyName = json.loads(servReply.get('reply')).get('clientStatus').get('lobbyName')
            servReply = self.backend.send(host, port, "get_lobby_status", [lobbyName])
            lobby = json.loads(servReply.get('reply')).get('lobby')
            time.sleep(2)
            if lobby['player1'] == self.clientInfo.get('username'):
                print('But your foe, ' + lobby['player2'] + ', sinks to a wat\'ry grave...')
            else:
                print('But your foe, ' + lobby['player1'] + ', sinks to a wat\'ry grave...')
            time.sleep(6)
            self.endLobby()
            time.sleep(2)
        else:
            clear_terminal()
            print('DEFEAT!')
            time.sleep(1)
            print('Poor, ' + self.clientInfo.get('username') + '... ', end='')
            time.sleep(2)
            print('you have found a final resting place beneath the waves.')
            servReply = self.backend.send(host, port, "get_client_status", [self.clientInfo.get('sessionID')])
            lobbyName = json.loads(servReply.get('reply')).get('clientStatus').get('lobbyName')
            servReply = self.backend.send(host, port, "get_lobby_status", [lobbyName])
            lobby = json.loads(servReply.get('reply')).get('lobby')
            time.sleep(2)
            if lobby['player1'] == self.clientInfo.get('username'):
                print('Meanwhile your foe, ' + lobby['player2'] + ', lives on in glory...')
            else:
                print('Meanwhile your foe, ' + lobby['player1'] + ', lives on in glory...')
            time.sleep(6)
            self.endLobby()
            time.sleep(2)
        
    # "ENSURE" METHODS (to prevent state errors)
    def ensureNoServerState(self):
        host = self.serverInfo.get('host')
        port = self.serverInfo.get('port')
        try:
            sessionID = self.clientInfo.get('sessionID')
            servReply = self.backend.send(host, port, 'logout', [sessionID])
            loggedOut = json.loads(servReply.get('reply')).get('loggedOut')
        except:
            pass
        self.connectedToServer = False
        self.serverFound = False
        self.inGame = False
        self.clientInfo = {
            'username': None,
            'sessionID': None
        }
        self.serverInfo = {
            'host': None,
            'port': None
        }
        
    def ensureLoginState(self):
        host = self.serverInfo.get('host')
        port = self.serverInfo.get('port')
        # Ensure still server exists. If not, crash.
        servReply = self.backend.send(host, port, action='ping')
        self.serverFound = json.loads(servReply.get('reply')).get('pinged')
        # Ensure logged out
        try:
            sessionID = self.clientInfo.get('sessionID')
            servReply = self.backend.send(host, port, 'logout', [sessionID])
            loggedOut = json.loads(servReply.get('reply')).get('loggedOut')
        except:
            pass
        # Set to not in game and reset client information
        self.inGame = False
        self.clientInfo = {
            'username': None,
            'sessionID': None
        }
        
    def ensureLobbyState(self):
        host = self.serverInfo.get('host')
        port = self.serverInfo.get('port')
        # Ensure still server exists. If not, crash.
        servReply = self.backend.send(host, port, action='ping')
        self.serverFound = json.loads(servReply.get('reply')).get('pinged')
        # Set to not in-game
        self.inGame = False
        
    def ensureInGameState(self):
        host = self.serverInfo.get('host')
        port = self.serverInfo.get('port')
        # Ensure still server exists. If not, crash.
        servReply = self.backend.send(host, port, action='ping')
        self.serverFound = json.loads(servReply.get('reply')).get('pinged')
        # Set to in-game
        self.inGame = True
    
    # UI HANDLING
    def updateDisplay(self):
        if not self.serverFound:
            self.ensureNoServerState()
            self.findServerPrompt()
            
        elif self.serverFound and not self.connectedToServer:
            try:
                self.ensureLoginState()
            except:
                # Server not found. Skip this loop and go back to find server prompt
                self.serverFound = False
                serverNotFoundMessage()
                return
            try:
                self.loginPrompt()
            except:
                # Server not found. Skip this loop and go back to find server prompt
                self.serverFound = False
                serverNotFoundMessage()
                return
            
        elif self.serverFound and self.connectedToServer and not self.inGame:
            try:
                self.ensureLobbyState()
            except:
                # Server not found. Skip this loop and go back to find server prompt
                self.serverFound = False
                serverNotFoundMessage()
                return
            try:
                self.displayLobby()
            except Exception as e:
                # Server not found. Skip this loop and go back to find server prompt
                #print("\n\n\n" + traceback.format_exc() + "\n\n\n")
                #time.sleep(10)
                self.serverFound = False
                serverNotFoundMessage()
                return
        
        elif self.serverFound and self.connectedToServer and self.inGame:
            try:
                self.ensureInGameState()
            except:
                # Server not found. Skip this loop and go back to find server prompt
                self.serverFound = False
                serverNotFoundMessage()
                return
            try:
                self.displayGame()
            except Exception as e:
                # Server not found. Skip this loop and go back to find server prompt
                #print("\n\n~~DEBUG INFO~~\n" + traceback.format_exc() + "\n~~~~~~~~~~~~~\n\n")
                #time.sleep(10)
                self.serverFound = False
                serverNotFoundMessage()
                return
            
        else:
            clear_terminal()
            print("ERROR: Client UI entered unkown state.")
            exit_program()
        
    # LAUNCHING POINT
    def start(self, host, port, action, values):
        try:
            if not action is None and not values is None:
                servReply = self.backend.send(host, port, action=action, values=values)
                print()
                print(json.loads(servReply.get('reply')))
                print()
            else:
                self.findServerPrompt()
                while(True):
                    self.updateDisplay()
                
        except KeyboardInterrupt:
            clear_terminal()
            print("Caught keyboard interrupt. Exiting...")
            host = self.serverInfo.get('host')
            port = self.serverInfo.get('port')
            sessionID = self.clientInfo.get('sessionID')
            if not host is None and not port is None and not sessionID is None:
                self.backend.send(host, port, 'logout', [sessionID])
            exit_program()