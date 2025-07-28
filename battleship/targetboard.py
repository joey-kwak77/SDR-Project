from board import Board
RED_PEG = 1
WHITE_PEG = 2


#=============================================================================
# Battleship Target Board - this is the vertical board in the Battleship
# game that tracks hits and misses. In the game, when the player guesses and
# hits, a red peg is placed at the coordinate. If it misses, a white peg
# is placed at the coordinate.
#
# Methods
#    markHit(r, c) - place a "red peg" at (r, c)
#    markMiss(r, c) - place a "white peg" at (r, c)
#    isHit(r, c) - is there a a "red peg" at (r, c)?
#    isEmpty(r, c) - is there any peg at (r, c)?
#=============================================================================
class TargetBoard(Board):

    def __init__(self, rsize: int, csize: int):
        super().__init__(rsize,csize)

    # place a "red peg" at (r, c)
    def markHit(self, r: int, c: int) -> None:
        self.putPiece(RED_PEG, r, c)

    # place a "white peg" at (r, c)
    def markMiss(self, r: int, c: int) -> None:
        self.putPiece(WHITE_PEG, r, c)

    # is there a "red peg" (a hit) at (r, c)?
    def isHit(self, r: int, c: int) -> bool:
        return self.getPiece(r,c) == RED_PEG

    # is there a any peg at (r, c)?
    def isEmpty(self, r: int, c: int) -> bool:
        return self.getPiece(r,c) == None
