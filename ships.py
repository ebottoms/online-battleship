class ShipCreator:
    def __init__(self):
        pass
    
    def create_ships(self):
        ships = {
            'carrier': self.create_carrier(),
            'battleship': self.create_battleship(),
            'cruiser': self.create_cruiser(),
            'submarine': self.create_submarine(),
            'destroyer': self.create_destroyer()
        }
        
    def create_carrier(self):
        carrier = {
            'sunk': False,
            'segments': {
                '1': {
                    'location': None,
                    'destroyed': False
                },
                
                '2': {
                    'location': None,
                    'destroyed': False
                },
                
                '3': {
                    'location': None,
                    'destroyed': False
                },
                
                '4': {
                    'location': None,
                    'destroyed': False
                },
                
                '5': {
                    'location': None,
                    'destroyed': False
                }
            }
        }
        return carrier
    
    def create_battleship(self):
        battleship = {
            'sunk': False,
            'segments': {
                '1': {
                    'location': None,
                    'destroyed': False
                },
                
                '2': {
                    'location': None,
                    'destroyed': False
                },
                
                '3': {
                    'location': None,
                    'destroyed': False
                },
                
                '4': {
                    'location': None,
                    'destroyed': False
                }
            }
        }
        return battleship
    
    def create_cruiser(self):
        cruiser = {
            'sunk': False,
            'segments': {
                '1': {
                    'location': None,
                    'destroyed': False
                },
                
                '2': {
                    'location': None,
                    'destroyed': False
                },
                
                '3': {
                    'location': None,
                    'destroyed': False
                }
            }
        }
        return cruiser
    
    def create_submarine(self):
        submarine = {
            'sunk': False,
            'segments': {
                '1': {
                    'location': None,
                    'destroyed': False
                },
                
                '2': {
                    'location': None,
                    'destroyed': False
                },
                
                '3': {
                    'location': None,
                    'destroyed': False
                }
            }
        }
        return submarine
    
    def create_destroyer(self):
        destroyer = {
            'sunk': False,
            'segments': {
                '1': {
                    'location': None,
                    'destroyed': False
                },
                
                '2': {
                    'location': None,
                    'destroyed': False
                }
            }
        }
        return destroyer