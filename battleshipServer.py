class Referee:    
    def __init__(self, P1_name, P2_name):
        # Player 2
        self.P1_incoming_strike = None
        self.P1_outgoing_strike = None
        self.P1_result_of_previous_outgoing_strike = None
        self.P1_num_hits = 0
        self.P1_name = P1_name
        
        # Player 2
        self.P2_incoming_strike = None
        self.P2_outgoing_strike = None
        self.P2_result_of_previous_outgoing_strike = None
        self.P2_num_hits = 0
        self.P2_name = P2_name
        
        # Referee
        self.game_over = False
        self.winner = None
        self.turn = self.P1_name
        
    def checkWinState(self):
        if self.P1_num_hits >= 17:
            self.winner = self.P2_name
            self.game_over = True
        elif self.P2_num_hits >= 17:
            self.winner = self.P1_name
            self.game_over = True
            
    def switchTurns(self):
        if self.turn == self.P1_name:
            self.turn = self.P2_name
        else:
            self.turn = self.P1_name
            
    def setOutgoingStrike(self, player_name, strike_location):
        if player_name == self.turn:
            if self.turn == self.P1_name:
                self.P1_outgoing_strike = strike_location
                self.P2_incoming_strike = strike_location
            else:
                self.P2_outgoing_strike = strike_location
                self.P1_incoming_strike = strike_location
            return True
        else:
            return False
        
    def setResultOfStrike(self, player_name, strike_result):
        if player_name == self.turn:
            if self.turn == self.P1_name:
                self.P2_result_of_previous_outgoing_strike = strike_result
                if strike_result == '!':
                    self.P2_num_hits += 1
                    self.checkWinState()
            else:
                self.P1_result_of_previous_outgoing_strike = strike_result
                if strike_result == '!':
                    self.P1_num_hits += 1
                    self.checkWinState()
            return True
        else:
            return False
        
    def getIncomingStrike(self, player_name):
        if player_name == self.turn:
            if self.turn == self.P1_name:
                return self.P1_incoming_strike
            else:
                return self.P2_incoming_strike
        else:
            return None
        
    def getResultOfPreviousStrike(self, player_name):
        if player_name == self.turn:
            if self.turn == self.P1_name:
                return self.P1_result_of_previous_outgoing_strike
            else:
                return self.P2_result_of_previous_outgoing_strike
        else:
            print("\n\n\nwhat dey helllll\n\n\n")
            print("\n\n", player_name, self.turn, "\n\n")
            print(self.P1_name, self.P2_name)
            return None