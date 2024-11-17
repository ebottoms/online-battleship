import os
import libclient
import json
import time
import traceback
import sys

class Program:
    def __init__(self):
        self.host = None
        self.port = None
        self.sessionID = None
        self.lobbyName = None
        self.clientSender = None
    
    def exit_program(self):
        print("Exiting the program...")
        sys.exit(0)
    
    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def server_connection_prompt(self):
        action = "ping"
        print("Enter Server IPv4 Address:")
        host = input()
        print()
        print("Enter Port Number:")
        port = int(input())
        print()
        return host, port, action
    
    def login_prompt(self):
        action = "login"
        print("Enter Your Username:")
        username = input()
        print()
        print("Enter Your Password:")
        password = input()
        print()
        return action, username, password
    
    def register_prompt(self):
        action = "register"
        print("Enter New Username:")
        username = input()
        print()
        print("Enter New Password:")
        password = input()
        print()
        return action, username, password
    
    def login_or_register_prompt(self):
        print("Enter \"R\" to register or \"L\" to login.")
        success = False
        while not success:
            option = input()
            if option == 'R' or option == 'r':
                option = 'R'
                success = True
            elif option == 'L' or option == 'l':
                option = 'L'
                success = True
            else:
                self.clear_terminal()
                print("Try again. Enter \"R\" to register or \"L\" to login.")
        return option
        
    def server_join_screen(self):
        # FIND SERVER
        serverFound = False
        while not serverFound:
            self.clientSender = libclient.Client()
            self.host, self.port, action = self.server_connection_prompt()
            try:
                servReply = self.clientSender.send(self.host, self.port, action)
                time.sleep(0.5)
                serverFound = json.loads(servReply.get("reply")).get("pinged")
            except Exception as e:
                self.clear_terminal()
                print("Could not find server. Either the server is down or\nyou have entered an invalid IP address and/or port number.\nPlease try again.\n")
        self.clear_terminal()
        print("Server Found!\n")
        
        # REGISTRATION / LOGIN
        choice = self.login_or_register_prompt()
        self.clear_terminal()
        if choice == 'R':
            registered = False
            while not registered:
                action, username, password = self.register_prompt()
                try:
                    servReply = self.clientSender.send(self.host, self.port, action, [username, password])
                    registered = json.loads(servReply.get("reply")).get("registered")
                except Exception as e:
                    print(traceback.format_exc())
                if not registered:
                    self.clear_terminal()
                    print("Not registered. Please try again.\n")
                else:
                    self.clear_terminal()
                    print("Registered! Now please login.\n")
    
        loggedIn = False
        while not loggedIn:
            action, username, password = self.login_prompt()
            try:
                servReply = self.clientSender.send(self.host, self.port, action, [username, password])
                loggedIn = json.loads(servReply.get("reply")).get("loggedIn")
            except Exception as e:
                print(traceback.format_exc())
            if not loggedIn:
                self.clear_terminal()
                print("Bad login. Please try again.\n")
            else:
                self.sessionID = json.loads(servReply.get("reply")).get("sessionID")
    
    def create_or_join_prompt(self):
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
                self.clear_terminal()
                print("Try again. Enter \"C\" to create a new game lobby or \"J\" to join an existing game lobby.")
        return option
    
    def create_lobby_prompt(self):
        lobbyCreated = False
        while not lobbyCreated:
            print("Enter new lobby name:")
            lobbyName = input()
            try:
                servReply = self.clientSender.send(self.host, self.port, "create_lobby", [self.sessionID, lobbyName])
                time.sleep(0.5)
                lobbyCreated = json.loads(servReply.get("reply")).get("lobbyCreated")
                self.lobbyName = lobbyName
            except Exception as e:
                print(traceback.format_exc())
            if not lobbyCreated:
                self.clear_terminal()
                print("Could not create lobby.")
                if "lobbyAlreadyExists" in json.loads(servReply.get("reply")):
                    print("Reason: Lobby with name \"" + lobbyName + "\" already exists.")
                else:
                    print("Reason: Invalid SessionID. Please restart your program.")
                    self.exit_program()
                print("Please try again.")
            
    def join_lobby_prompt(self):
        pass
    
    def display_lobby(self):
        gameStarted = False
        while not gameStarted:
            self.clear_terminal()
            lobby = None
            try:
                servReply = self.clientSender.send(self.host, self.port, "get_lobby_status", [self.sessionID, self.lobbyName])
                lobby = json.loads(servReply.get("reply")).get("lobby")
            except Exception as e:
                self.clear_terminal()
                print("Lost connection to server. Please restart this application.")
                self.exit_program()
            print("LOBBY: " + self.lobbyName)
            print("STATUS: Waiting for Player 2 to join to start game.")
            gameStarted = lobby.get("gameStarted")
            time.sleep(1)
    
    def lobby_screen(self):
        choice = self.create_or_join_prompt()
        if choice == 'C':
            self.clear_terminal()
            self.create_lobby_prompt()
            self.clear_terminal()
            self.display_lobby()
        else:
            self.clear_terminal()
            self.join_lobby_prompt()
    
    def open(self):
        self.clear_terminal()
        self.server_join_screen()
        self.clear_terminal()
        print("Logged in!")
        self.lobby_screen()
        
        
        