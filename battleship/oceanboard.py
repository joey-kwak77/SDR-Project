from board import Board
from ship import Ship

'''
The Ocean Board is the portion of the Battleship Unit that holds
ships that the player had placed and keeps track of hits upon each
ship that the opponent has guessed correctly.
'''
class OceanBoard(Board):

    def __init__(self, rsize: int, csize: int):
        super().__init__(rsize, csize)
        self.ships = []

    # return False if ship could not be placed at r, c
    #    either r, c are illegal
    #    or ship is too big to be placed there
    #    or another ship is already there
    # Modify 'ship' with the given (r, c) and orientation
    # Add 'ship' to the the OceanBoard's list of 'ships' if placed successfully

    def placeShip(self, ship: Ship, r: int, c: int, orientation: str) -> bool:
        """
        params:
            orientation: 'h' -- horizontal; 'v' -- vertical
        return: True   -- ship has been sucessfully placed
                False  -- cannot place the ship
        """
        # check if initial position is on board
        if not(0 <= r <= 9 and 0 <= c <= 9):
            return False
        # check if ship can be placed
        if orientation == 'v':
            if r < 0 or (r+ship.size) > 10:
                return False
            for i in range(r, r + ship.size):
                if self.board[i][c] != None:
                    return False

            # modify the ship
            ship.horizontal = False
            ship.loc = (r, c)

            # place ships on board
            for i in range(r, r + ship.size):
                self.board[i][c] = ship
            self.ships.append(ship)

        elif orientation == 'h':
            if c < 0 or (c+ship.size) > 10:
                return False
            for i in range(c, c + ship.size):
                if self.board[r][i] != None:
                    return False

            # change the ship
            ship.horizontal = True
            ship.loc = (r, c)

            # place ships on board
            for i in range(c, c + ship.size):
                self.board[r][i] = ship

            self.ships.append(ship)

        return True

    # are all 'ships' in the OceanBoard sunk?
    def allShipsSunk(self) -> bool:
        for ship in self.ships:
            if not ship.isSunk():
                return False
        return True

