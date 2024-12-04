#!/usr/bin/env python3

import numpy as np
import sys
import os
import time

def exit_program():
    print("Exiting the program...")
    sys.exit(0)
    
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

class Game:    
    def __init__(self):        
        self.board = self.createBoard()
        self.opponentBoard = self.createBoard()
        self.ships = None
        self.outgoingStrike = None
        
    def createBoard(self):
        board = np.zeros((10,10), dtype=object)
        board[board == 0] = '~'
        return board
    
    #def drawBoard(self):
    #    boardRepresentation =                       "    1   2   3   4   5   6   7   8   9   10 \n"
    #    boardRepresentation = boardRepresentation + "    —   —   —   —   —   —   —   —   —   —  \n"
    #    for j in range(10):
    #        boardRepresentation = boardRepresentation + chr(j + 65)
    #        for i in range(10):
    #            boardRepresentation = boardRepresentation + " | " + self.board[i][j]
    #        boardRepresentation = boardRepresentation + " | \n"
    #        boardRepresentation = boardRepresentation + "    —   —   —   —   —   —   —   —   —   —  \n"
    #    print(boardRepresentation)
    
    def drawBoard(self, board):
        boardRepresentation = "  1 2 3 4 5 6 7 8 9 10 \n"
        for j in range(10):
            boardRepresentation = boardRepresentation + chr(j + 65) + ""
            for i in range(10):
                boardRepresentation = boardRepresentation + " " + board[i][j]
            boardRepresentation = boardRepresentation + "\n"
        print(boardRepresentation)
        
    def placeShip(self, board, ship, direction, position=(0,0)):
        headPos = position
        if direction == 'N':
            if headPos[1] + len(ship) > len(board):
                return None
            else:
                index = 0
                for segment in ship:
                    if board[headPos[0]][headPos[1]+index] != '~':
                        time.sleep(3)
                        return None
                    board[headPos[0]][headPos[1]+index] = segment
                    index += 1
        elif direction == 'E':
            if headPos[0]+1 - len(ship) < 0:
                return None
            else:
                index = 0
                for segment in ship:
                    if board[headPos[0]-index][headPos[1]] != '~':
                        return None
                    board[headPos[0]-index][headPos[1]] = segment
                    index += 1
        elif direction == 'S':
            if headPos[1]+1 - len(ship) < 0:
                return None
            else:
                index = 0
                for segment in ship:
                    if board[headPos[0]][headPos[1]-index] != '~':
                        return None
                    board[headPos[0]][headPos[1]-index] = segment
                    index += 1
        elif direction == 'W':
            if headPos[1] + len(ship) > len(board):
                return None
            else:
                index = 0
                for segment in ship:
                    if board[headPos[0]+index][headPos[1]] != '~':
                        return None
                    board[headPos[0]+index][headPos[1]] = segment
                    index += 1
        else:
            return None
        return board
    
    def placeShips(self):
        carrier = ['C', 'C', 'C', 'C', 'C']
        battleship = ['B', 'B', 'B', 'B']
        cruiser = ['V', 'V', 'V']
        submarine = ['S', 'S', 'S']
        destroyer = ['D', 'D']
        ships = [carrier, battleship, cruiser, submarine, destroyer]
        shipNames = ['carrier', 'battleship', 'cruiser', 'submarine', 'destroyer']
        directions = ['N','E','S','W']
        for i in range(len(ships)):
            newBoard = self.board.copy()
            position = None
            clear_terminal()
            done = False
            while not done:
                self.drawBoard(self.board)
                print("Please input a starting tile to place your " + shipNames[i].upper() + " on. (Example: C6)")
                pos = input().upper()
                if len(pos) <= 0 or len(pos) > 3:
                    clear_terminal()
                    print("Please follow the Letter-Number format.")
                    continue
                elif ord(pos[0]) < 65 or ord(pos[0]) > 74:
                    clear_terminal()
                    print("Please follow the choose a letter between \'A\' and \'J\'.")
                    continue
                col = ord(pos[0]) - 65
                try:
                    row = int(pos[1:]) - 1
                    if row < 0 or row > 9:
                        clear_terminal()
                        print("Please follow the choose a number between 1 and 10.")
                        continue
                except:
                    clear_terminal()
                    print("Please follow the Letter-Number format.")
                    continue
                if self.board[row][col] != '~':
                    clear_terminal()
                    print("Please do not choose a tile on which another ship is already placed.")
                    continue
                cannotFit = False
                for l in range(4):
                    currentBoard = self.board.copy()
                    rotBoard = self.placeShip(board=currentBoard, ship=ships[i], direction=directions[l], position=(row, col))
                    if rotBoard is None:
                        if l == 3:
                            cannotFit = True
                    else:
                        newBoard = rotBoard
                        break
                if cannotFit:
                    clear_terminal()
                    print("You have chosen to place your ship on a tile in which it will not fit between the others. Please try again.")
                    continue
                position = (row, col)
                done = True

            clear_terminal()
            currentDirection = 0
            done = False
            while not done:
                currentBoard = self.board.copy()
                self.drawBoard(newBoard)
                print("Please rotate the ship in the orientation you would like. Enter one of the following options:\n\'Z\' for rotate clockwise\n\'X\' to rotate counter-clockwise\n\'D\' to confirm orientation.")
                rot = input().upper()
                if len(rot) != 1:
                    clear_terminal()
                    print('Try again.')
                elif rot == 'Z':
                    currentDirection += 1
                    tempBoard = self.placeShip(board=currentBoard, ship=ships[i], direction=directions[currentDirection], position=position)
                    if tempBoard is None:
                        currentDirection -= 1
                        clear_terminal()
                        print("Cannot rotate that way. Something is in the way.")
                    else:
                        clear_terminal()
                        newBoard = tempBoard
                elif rot == 'X':
                    currentDirection -= 1
                    tempBoard = self.placeShip(board=currentBoard, ship=ships[i], direction=directions[currentDirection], position=position)
                    if tempBoard is None:
                        currentDirection += 1
                        clear_terminal()
                        print("Cannot rotate that way. Something is in the way.")
                    else:
                        clear_terminal()
                        newBoard = tempBoard
                elif rot == 'D':
                    done = True
                else:
                    clear_terminal()
                    print('Try again.')
            self.board = newBoard
            
    def makeShips(self):
        carrierIndices = np.where(self.board == 'C')
        carrier = []
        for i in range(len(carrierIndices[0])):
            carrier.append(((carrierIndices[0][i]), (carrierIndices[1][i])))
            
        battleshipIndices = np.where(self.board == 'B')
        battleship = []
        for i in range(len(battleshipIndices[0])):
            battleship.append(((battleshipIndices[0][i]), (battleshipIndices[1][i])))
            
        cruiserIndices = np.where(self.board == 'V')
        cruiser = []
        for i in range(len(cruiserIndices[0])):
            cruiser.append(((cruiserIndices[0][i]), (cruiserIndices[1][i])))
            
        submarineIndices = np.where(self.board == 'S')
        submarine = []
        for i in range(len(submarineIndices[0])):
            submarine.append(((submarineIndices[0][i]), (submarineIndices[1][i])))
            
        destroyerIndices = np.where(self.board == 'D')
        destroyer = []
        for i in range(len(destroyerIndices[0])):
            destroyer.append(((destroyerIndices[0][i]), (destroyerIndices[1][i])))
            
        self.ships = dict(carrier=carrier, battleship=battleship, cruiser=cruiser, submarine=submarine, destroyer=destroyer)
            
    def tempUI(self):
        clear_terminal()
        print("RADAR")
        self.drawBoard(self.opponentBoard)
        print("YOUR BOARD")
        self.drawBoard(self.board)
        print('\n')
    
    def initialize(self):
        self.placeShips()
        self.makeShips()
      
    def takeMyTurn(self, incomingStrikeLocation, resultOfPreviousStrike):
        # Deal with result of outgoing strike
        if not self.outgoingStrike is None:
            self.opponentBoard[self.outgoingStrike[0]][self.outgoingStrike[1]] = resultOfPreviousStrike
            
        # Deal with incoming strike
        enemyHitMe = False
        if not incomingStrikeLocation is None:
            if self.board[incomingStrikeLocation[0]][incomingStrikeLocation[1]] != '~':
                enemyHitMe = True
                self.board[incomingStrikeLocation[0]][incomingStrikeLocation[1]] = '!'
            else:
                self.board[incomingStrikeLocation[0]][incomingStrikeLocation[1]] = 'x'
                
        # Select new outgoing stike location
        clear_terminal()
        self.tempUI()
        done = False
        while not done:
            print("Please enter location you'd like to strike next:")
            newOutgoingStrike = input().upper()
            if len(newOutgoingStrike) <= 0 or len(newOutgoingStrike) > 3:
                self.tempUI()
                print("Please follow the Letter-Number format.")
                continue
            elif ord(newOutgoingStrike[0]) < 65 or ord(newOutgoingStrike[0]) > 74:
                self.tempUI()
                print("Please follow the choose a letter between \'A\' and \'J\'.")
                continue
            col = ord(newOutgoingStrike[0]) - 65
            try:
                row = int(newOutgoingStrike[1:]) - 1
                if row < 0 or row > 9:
                    self.tempUI()
                    print("Please follow the choose a number between 1 and 10.")
                    continue
            except:
                self.tempUI()
                print("Please follow the Letter-Number format.")
                continue
            if self.opponentBoard[row][col] != '~':
                self.tempUI()
                print("You have already fired upon this location. Choose another.")
                continue
            self.outgoingStrike = (row, col)
            done = True
        
        return enemyHitMe, self.outgoingStrike