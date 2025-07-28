from targetboard import WHITE_PEG, RED_PEG
from battleshipplayer import BattleshipPlayer
from letter import Letter
import subprocess

from ship import Ship

'''
Display - a class that handles the display of the Battleship game. It handles
all the printing and inputing for the game. It has some methods that help
move the cursor around for a more pleasant user game experience.
'''
class Display:

    #### DO NOT MODIFY LINES BELOW ####
    # move to 1, 1
    def home(self) -> None:
        print(u'\u001b[H', end='')

    # move cursor to line, col
    def moveTo(self, line, col) -> None:
        print(u'\u001b[' + f"{line};{col}H", end='')

    # move cursor to column col 
    def moveToColumn(self, col) -> None:
        print(u'\u001b[' + f"{col}G", end='')

    # clear to the end of line (keeping cursor at the current position)
    def clearToEndOfLine(self) -> None:
        print(u'\u001b[K', end='')

    # clear to the end of screen (keeping cursor at the current position)
    def clearToEndOfScreen(self) -> None:
        print(u'\u001b[J', end='')

    # clear screen and move to top left (1,1) of screen
    def clearScreen(self) -> None:
        self.home()
        self.clearToEndOfScreen()

    # return the proper column position for player X
    def playerColumn(self, playerNum: int) -> str:
        if playerNum== 2:
            column = 76
        else:
            column = 0
        return column

    # display message for player X
    def message(self, msg: str, playerNum = 1) -> None:
        self.moveToColumn(self.playerColumn(playerNum))
        print(msg)

    # ask for input from player X
    def ask(self, msg: str, playerNum = 1) -> str:
        self.moveToColumn(self.playerColumn(playerNum))
        return input(msg)

    def newLine(self):
        print()
    #### DO NOT MODIFY LINES ABOVE ####

    #### MODIFY BELOW ####
    # display the Ocean board of the player
    def displayOcean(self, player: BattleshipPlayer) -> None:
        o = player.getOcean()

        print("  1 2 3 4 5 6 7 8 9 10")
        for r in range(10):
            for c in range(11):
                if c == 0:
                    print(chr(int(ord('a'))+r) + ' ', end = "")
                else:
                    if o.getPiece(r, c-1) == None:
                        print(". ", end = "")
                    elif type(o.getPiece(r, c-1)) == Ship:
                        print(o.getPiece(r, c-1).type[0], end = " ")
            print('')

    # display both player 1 and player 2 ocean & target units
    def displayUnits(self, p1: BattleshipPlayer, p2: BattleshipPlayer) -> None:
        # get the boards of each player
        o1 = p1.getOcean()
        t1 = p1.getTarget()
        o2 = p2.getOcean()
        t2 = p2.getTarget()

        # print out boards
        print("{}'s Battleship Unit".format(p1.name) + " "*(52-len(p1.name)) + "{}'s Battleship Unit".format(p2.name))
        print("  Ocean                   Target                                        Ocean                   Target")
        print("  1 2 3 4 5 6 7 8 9 10    1 2 3 4 5 6 7 8 9 10                          1 2 3 4 5 6 7 8 9 10    1 2 3 4 5 6 7 8 9 10")
        for r in range(10):
            for c in range(47):
                # print out the column labels and empty spaces in between 
                if c == 0 or c == 12 or c == 24 or c == 36:
                    print(chr(ord('a')+r) + ' ', end = "")
                elif c == 23:
                    print("                        ", end = "")
                elif c == 11 or c == 35:
                    print("  ", end = "")

                # print out boards
                else:
                    if 1 <= c < 11: # print out player1's ocean board
                        if o1.getPiece(r, c-1) is None:
                            print(". ", end = "")
                        elif isinstance(o1.getPiece(r, c-1), Ship):
                            ship = o1.getPiece(r, c-1)
                            if ship.status[(r + c-1) - (ship.loc[0] + ship.loc[1])] == RED_PEG:
                                print(Letter(o1.getPiece(r, c-1).type[0], "red"), end = " ")
                            else:
                                print(o1.getPiece(r, c-1).type[0], end = " ")

                    elif 13 <= c < 23: # print out player1's target board
                        if t1.getPiece(r, c-13) is None:
                            print(". ", end = "")
                        elif t1.getPiece(r, c-13) == RED_PEG:
                            print(Letter("X", "red"), end = " ")
                        elif t1.getPiece(r, c-13) == WHITE_PEG:
                            print(Letter("o", "yellow"), end = " ")
                    
                    elif 25 <= c < 35: # print out player2's ocean board
                        if o2.getPiece(r, c-25) is None:
                            print(". ", end = "")
                        elif isinstance(o2.getPiece(r, c-25), Ship):
                            ship = o2.getPiece(r, c-25)
                            if ship.status[(r + c-25) -(ship.loc[0] + ship.loc[1])] == RED_PEG:
                                print(Letter(o2.getPiece(r, c-25).type[0], "red"), end = " ")
                            else:
                                print(o2.getPiece(r, c-25).type[0], end = " ")
                                
                    elif 37 <= c < 47: # print out player2's target board
                        if t2.getPiece(r, c-37) is None:
                            print(". ", end = "")
                        elif t2.getPiece(r, c-37) == RED_PEG:
                            print(Letter("X", "red"), end = " ")
                        elif t2.getPiece(r, c-37) == WHITE_PEG:
                            print(Letter("o", "yellow"), end = " ")

            print('')

