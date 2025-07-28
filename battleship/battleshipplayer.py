from targetboard import TargetBoard
from oceanboard import OceanBoard
from letter import Letter
from ship import Ship

class BattleshipPlayer:

    '''
    Models the Battleship Player
     player = Battleship("Joe")    # default 10x10 board

    State Variables
     name (str) - the name of the player
     score (int) - the score of the player
     ocean (OceanBoard) - the board which contains all of the ships
     target (TargetBoard) - the board whih contains all the shots made
    '''
                            # optional parameters default is 10x10
    def __init__(self, name: str, rsize=10, csize=10):
        self.name = name
        self.score = 0


        self.ocean = OceanBoard(rsize, csize)
        self.target = TargetBoard(rsize, csize)

    def getName(self) -> str:
        return self.name

    def getOcean(self) -> OceanBoard:
        return self.ocean

    def getTarget(self) -> TargetBoard:
        return self.target

    def getScore(self) -> int:
        return self.score

    '''
    loc: grid location like 'a1' or 'j10'
    orientation: 'h' or 'v' for horizontal or vertical
    return: True if ship was successfully placed
    '''

    def placeShip(self, ship: Ship, loc: str, orientation: str) -> bool:
        try:
            c = int(loc[1:]) - 1
        except ValueError:
            return False
        r = int(ord(loc[0]) - ord("a"))
        coords = (r, c)
        if orientation not in ["h", "v"]:
            return False
        else:
            return (self.ocean.placeShip(ship, coords[0], coords[1], orientation))

    def shipAt(self, r, c):
        piece = self.ocean.getPiece(r, c)
        if piece is None:
            return None
        return piece.getType()

    '''
    Process the shot at (r, c) and return (hit, sunk, name)
     - Determine if there is a hit
     - Check if the ship is sunk
     - Get the name of the ship (if there is a hit)
     - Mark the ship as being hit
    '''
    def shotAt(self, r: int, c: int) -> bool:
        piece = self.ocean.getPiece(r, c)
        if piece is None:
            hit = False
            sunk = False
        elif isinstance(piece, Ship):
            piece.markHitAt(r, c)
            hit = True
            sunk = piece.isSunk()
            piece = piece.getType()
        return (hit, sunk, piece)

    def markTargetHit(self, r: int, c: int) -> None:
        self.target.markHit(r, c)

    def markTargetMiss(self, r: int, c: int) -> None:
        self.target.markMiss(r, c)

    def allShipsSunk(self):
        return self.ocean.allShipsSunk()

    '''
    Resets both the ocean and target board so that game could
    be restarted
    '''
    def resetUnit(self) -> None:
        self.ocean = OceanBoard(10, 10)
        self.target = TargetBoard(10, 10)

    '''
    Adds num to the score
    '''
    def updateScore(self, num: int) -> None:
        self.score += num

