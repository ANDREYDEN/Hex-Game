"""main file"""

from game import Game
import consts

game = Game(consts.SIZE)
game.loadData()
game.startScreen()
