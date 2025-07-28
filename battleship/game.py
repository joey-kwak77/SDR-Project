from battleshipplayer import BattleshipPlayer
from ship import Ship
from display import Display
from setting import Setting
from letter import Letter

'''
Places the 5 ships onto the Ocean board of 'player'
Creates 5 ships, asks player where it wants them placed, and puts them into
the Ocean board.
'''
def initPlayer(d: Display, player: BattleshipPlayer) -> None:
    for i in [["Carrier", 5], ["Battleship", 4], ["Destroyer", 3], ["Submarine", 3], ["Patrol Boat", 2]]:
        ship = Ship(i[0], i[1])
        d.clearScreen()
        d.message(player.name)
        d.displayOcean(player)
        loc = input("Where should the {} (size {}) be placed? ".format(i[0], i[1]))
        orientation = input("What orientation (h/v)? ")
        while not player.placeShip(ship, loc, orientation):
            print("illegal placement, please place again")
            loc = input("Where should the {} (size {}) be placed (ex. a1)? ".format(i[0], i[1]))
            orientation = input("What orientation (h/v)? ")


'''
playerNumber calls a shot and p1/p2 player units are updated appropriately
return - True if all ships are sunk after the player's shot
'''
def convertLoc(loc: str):
    try:
        c = int(loc[1:]) - 1
    except ValueError:
        return False
    else:
        if not 0 <= c <= 9:
            return False
    
    r = int(ord(loc[0]) - ord('a'))
    if not 0 <= r <= 9:
        return False
    return (r, c)


def turn(d: Display, p1: BattleshipPlayer, p2: BattleshipPlayer, playerNumber: int, message = "") -> bool:

    if playerNumber == 0:
        p = p1
        o = p2
    else:
        p = p2
        o = p1

    while True: # check for valid grid
        res = convertLoc(input("{}, which grid are you shooting? ".format(p.name)))
        if res:
            r, c = res # unpacking into row and column
            break
        else:
            d.message("invalid grid")
        
    # if already hit (don't get to hit again because you are dumb)
    if p.target.getPiece(r, c) != None:
        print("You already hit that...")

    # if miss
    elif o.ocean.getPiece(r, c) == None:
        p.target.markMiss(r, c)
        d.clearScreen()
        d.displayUnits(p1, p2)
        d.message("Miss!")

    # if hit
    else:
        ship = o.ocean.getPiece(r, c)
        ship.markHitAt(r, c)
        p.target.markHit(r, c)

        d.clearScreen()
        d.displayUnits(p1, p2)
        d.message("Hit!")

        if ship.isSunk():
            d.message("You sunk {}'s {}!".format(o.name, o.ocean.getPiece(r, c).getType()))
        
            # extra feature: can hit one more time
            hitagain = input("Hit! {}, you have a chance to hit again! Do you want to? (yes/no) ".format(p.name)).lower() 
            if hitagain == "yes":
                while True: 
                    res = convertLoc(input("{}, which grid are you shooting? ".format(p.name)))
                    if res:
                        r, c = res 
                        break
                    else:
                        d.message("invalid grid")
                if o.ocean.getPiece(r, c) == None:
                    p.target.markMiss(r, c)
                    d.clearScreen()
                    d.displayUnits(p1, p2)
                    print("Miss!")
                else:
                    ship = o.ocean.getPiece(r, c)
                    ship.markHitAt(r, c)
                    p.target.markHit(r, c)

                    d.clearScreen()
                    d.displayUnits(p1, p2)
                    if ship.isSunk():
                        d.message("You sunk {}'s {}!".format(o.name, o.ocean.getPiece(r, c).getType()))
                    else:
                        d.message("Hit!")

    return(p.allShipsSunk() or o.allShipsSunk())


def playBattleship(d: Display, settings: Setting) -> None:
    # h20
    name1 = input("Player 1, what is your name? ")
    p1 = BattleshipPlayer(name1, 10, 10)
    initPlayer(d, p1)

    d.clearScreen()
    name2 = input("Player 2, what is your name? ")
    p2 = BattleshipPlayer(name2, 10, 10)
    initPlayer(d, p2)

    d.clearScreen()
    d.displayUnits(p1, p2)

    # take turns between player 1 and 2 until one player sinks the other's ships
    turns = 0
    while not turn(d, p1, p2, turns%2):
        turns += 1

    d.clearScreen()

    # updating score
    if turns % 2 == 0:
        p1.updateScore(1)
        print("Congratulations {}! You won!".format(p1.name))
    else:
        p2.updateScore(1)
        print("Congratulations {}! You won!".format(p2.name))
    d.message("Score: {} - {}; {} - {}".format(p1.name, p1.score, p2.name, p2.score))

    # check if they want to play again
    playagain = input("Do you want to play again? (yes/no) ")
    while playagain == "yes":
        p1.resetUnit()
        p2.resetUnit()
        initPlayer(d, p1)
        initPlayer(d, p2)

        d.clearScreen()
        d.displayUnits(p1, p2)

        turns = 0
        while not turn(d, p1, p2, turns%2):
            turns += 1

        d.clearScreen()

        # updating score
        if turns % 2 == 0:
            p1.updateScore(1)
            print("Congratulations {}! You won!".format(p1.name))
        else:
            p2.updateScore(1)
            print("Congratulations {}! You won!".format(p2.name))
        d.message("Score: {} - {}; {} - {}".format(p1.name, p1.score, p2.name, p2.score))
        
        playagain = input("Do you want to play again? (yes/no) ")

    else:
        d.clearScreen()
        print("OK! Have a nice life :)!")

def main():
    d = Display()
    d.clearScreen()
    d.message("Let's play Battleship!")

    settings = Setting()
    settings.setSetting('mode', 'basic')
    settings.setSetting('numplayers', 2)

    playBattleship(d, settings)

if __name__ == "__main__":
    main()
