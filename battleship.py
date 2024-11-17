import numpy as np
import ships

class Game:    
    def __init__(self):        
        player1_board = self.create_board()
        player1_opponent_board = self.create_board()
        player1_ships = ships.ShipCreator().create_ships()
        
        player2_board = self.create_board()
        player2_opponent_board = self.create_board()
        player2_ships = ships.ShipCreator().create_ships()
        
    def create_board(self):
        board = np.zeros((10,10))
        board[board == 0] = {
            'hit': False,
            'segment': None
        }
        return board