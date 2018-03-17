"""Game stuf and logic"""

import sys
from os import path
from math import sqrt
from collections import namedtuple
import pygame as pg

import consts
from algs import DFS, point, inHex
from visual import drawHex, textOut, textOutMultiline, Button, screen

Text = namedtuple('Text', 'instr size col pos')

class Game:
    def __init__(self, size):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((consts.W, consts.H))
        self.size = size
        self.setTileSize()
        self.state = [[0 for _ in range(self.size)] for __ in range(self.size)]
        self.origin = point(consts.W/2 - (consts.H/2-50)/sqrt(3), 50)
        self.move = 1
        self.sound_state = True

    def loadData(self):
        """load all the data (images, files, etc)"""
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        doc_folder = path.join(game_folder, 'docs')
        #------------------IMAGES------------------
        # image for tiles (optional)
        #self.tile_img = pg.image.load(path.join(img_folder, TILE_IMG)).convert_alpha()
        #self.tile_img = pg.transform.scale(self.tile_img, (2*self.tile_size+1, int(self.tile_size*sqrt(3))+1))

        self.bg_img = pg.image.load(path.join(img_folder, consts.BG_IMG)).convert_alpha()
        self.pause_img = pg.image.load(path.join(img_folder, consts.PAUSE_IMG)).convert_alpha()
        self.back_img = pg.image.load(path.join(img_folder, consts.BACK_IMG)).convert_alpha()
        self.up_img = pg.image.load(path.join(img_folder, consts.UP_IMG)).convert_alpha()
        self.down_img = pg.image.load(path.join(img_folder, consts.DOWN_IMG)).convert_alpha()

        #------------------MUSIC--------------------
        self.bg_music = pg.mixer.Sound(path.join(doc_folder, consts.BACKGROUND_MUSIC))
        self.bg_music_channel = pg.mixer.Channel(1)
        self.bg_music_channel.play(self.bg_music, loops=-1)
        self.bg_music_channel.set_volume(0.5)
        self.click_sound = pg.mixer.Sound(path.join(doc_folder, consts.CLICK_SOUND))
        self.click_sound_channel = pg.mixer.Channel(2)

        #-----------------TEXT--------------------
        with open(path.join(doc_folder, consts.RULES), 'r') as f:
            self.rules_text = ''.join(f.readlines())

    def reset(self):
        self.setTileSize()
        self.state = [[0 for _ in range(self.size)] for __ in range(self.size)]
        self.origin = point(consts.W/2 - (consts.H/2-50)/sqrt(3), 50)
        self.move = 1

    def setTileSize(self):
        self.tile_size = 4*(consts.H/2-50)/3/sqrt(3)/(self.size-1)

    def coords(self, r, c):
        """translates grid coordinates to real coordinates"""
        x = self.origin.x + c*3/2*self.tile_size
        y = self.origin.y + (c+2*r)*self.tile_size*sqrt(3)/2
        return int(x), int(y)

    def tick(self):
        """is called if mouse pressed, changes the state of the game"""
        pos = pg.mouse.get_pos()
        for r in range(self.size):
            for c in range(self.size):
                x, y = self.coords(r, c)
                if inHex(pos, x, y, self.tile_size) and self.state[r][c] != 2\
                                                    and self.state[r][c] != 1:
                    #if self.sound_state:
                    #    self.click_sound_channel.play(self.click_sound)
                    self.state[r][c] = self.move
                    self.move = 3-self.move

    def highlight(self):
        """highlights the hexagon that is under the mouse"""
        pos = pg.mouse.get_pos()
        for r in range(self.size):
            for c in range(self.size):
                x, y = self.coords(r, c)
                if self.state[r][c] == 0 and inHex(pos, x, y, self.tile_size):
                    self.state[r][c] = self.move + 2
                elif self.state[r][c] > 2 and not inHex(pos, x, y, self.tile_size):
                    self.state[r][c] = 0

    def showBounds_(self):
        """draws coloured bounds for players to understand were to go"""
        A = (self.origin.x-self.tile_size, self.origin.y-self.tile_size*sqrt(3))
        B = (self.origin.x-self.tile_size/2*(1-3*self.size),
             self.origin.y+self.tile_size*sqrt(3)/2*(self.size-2)+self.tile_size*sqrt(3)/6)
        C = (self.origin.x-self.tile_size/2*(1-3*self.size), self.origin.y+self.tile_size*sqrt(3)/2*(2*self.size+self.size-1))
        D = (self.origin.x-self.tile_size, self.origin.y+self.tile_size*sqrt(3)*(self.size-1/2)-self.tile_size*sqrt(3)/6)
        M = ((A[0]+B[0])/2, (B[1]+C[1])/2)
        pg.draw.polygon(self.screen, consts.GREEN, [A, B, M])
        pg.draw.polygon(self.screen, consts.GREEN, [C, D, M])
        pg.draw.polygon(self.screen, consts.BLUE, [B, C, M])
        pg.draw.polygon(self.screen, consts.BLUE, [D, A, M])

    def showGrid(self):
        """shows hexagonal grid as well as players moves and destination sides"""
        self.showBounds_()
        for r in range(self.size):
            for c in range(self.size):
                x, y = self.coords(r, c)
                # draw a tile
                #self.screen.blit(self.tile_img, (x-self.tile_size, y-self.tile_size))
                # draw players
                if self.state[r][c] == 1:
                    drawHex(surface=self.screen,
                            col_in=consts.GREEN,
                            col_out=consts.LIGHTYELLOW,
                            pos=(x, y),
                            a=self.tile_size)
                elif self.state[r][c] == 2:
                    drawHex(surface=self.screen,
                            col_in=consts.BLUE,
                            col_out=consts.LIGHTYELLOW,
                            pos=(x, y),
                            a=self.tile_size)
                elif self.state[r][c] == 3:
                    drawHex(surface=self.screen,
                            col_in=consts.LIGHTGREEN,
                            col_out=consts.LIGHTYELLOW,
                            pos=(x, y),
                            a=self.tile_size)
                elif self.state[r][c] == 4:
                    drawHex(surface=self.screen,
                            col_in=consts.LIGHTBLUE,
                            col_out=consts.LIGHTYELLOW,
                            pos=(x, y),
                            a=self.tile_size)
                else:
                    drawHex(surface=self.screen,
                            col_in=consts.DARKRED,
                            col_out=consts.LIGHTYELLOW,
                            pos=(x, y),
                            a=self.tile_size)

    def checkWin(self):
        """checks if any of the players have won"""
        for y in range(self.size):
            if self.state[y][0] == 2:
                if DFS((y, 0), self.state, lambda v: (v.y == self.size-1), 2):
                    return 2

        for x in range(self.size):
            if self.state[0][x] == 1:
                if DFS((0, x), self.state, lambda v: (v.x == self.size-1), 1):
                    return 1
        return 0

    def shadow(self):
        shadow = pg.Surface((consts.W, consts.H))
        shadow.set_alpha(200)
        self.screen.blit(shadow, (0, 0))

    def startScreen(self):
        """shows start screen, returns True if the game has started"""
        def playInstr(button):
            button.game.reset()
            button.game.mainGameScreen()

        buttons = [Button(self, pos=(consts.W/2, 2*consts.H/3), size=80,
                          instr=playInstr, txt='Play'),
                   Button(self, pos=(150, consts.H-75), size=50,
                          instr=lambda button: self.settingsScreen(),
                          txt='Settings'),
                   Button(self, pos=(consts.W-100, consts.H-75), size=50,
                          instr=lambda button: self.rulesScreen(),
                          txt='Rules')
                  ]

        text = [Text(instr=lambda game: 'HEX', size=200,
                     col=consts.ORANGE, pos=(consts.W/2, consts.H/3))
               ]

        screen(self, buttons=buttons, text=text, bg_image=self.bg_img)

    def rulesScreen(self):
        """shows the rules of the game, returns True if the "back" button was hit"""
        buttons = [Button(self, pos=(30, 30), size=50,
                          instr=lambda button: button.game.startScreen(),
                          img=self.back_img)
                  ]


        text = [Text(instr=lambda game: 'Rules', size=100,col=consts.ORANGE,
                     pos=(consts.W/2, consts.H/3))
               ]

        screen(self, buttons=buttons, text=text,
               additional=lambda game: textOutMultiline(
                                      surface=game.screen,
                                      txt=game.rules_text,
                                      size=30,
                                      col=consts.BLACK,
                                      pos=(consts.W/2, consts.H/3)),
               bg_image=self.bg_img)

    def settingsScreen(self):
        """shows the rules of the game, returns True if the "back" button was hit"""
        music_state = 'On' if self.bg_music_channel.get_busy() else 'Off'
        sound_state = 'On' if self.sound_state else 'Off'

        def musicInstr(button):
            if button.text == 'On':
                button.game.bg_music_channel.stop()
                button.text = 'Off'
            else:
                button.game.bg_music_channel.play(button.game.bg_music, loops=-1)
                button.text = 'On'

        def soundInstr(button):
            button.game.sound_state = button.text != 'On'
            button.text = 'On' if button.text == 'Off' else 'Off'

        def upSize(button):
            button.game.size = min(consts.MAX_BOARD_SIZE, button.game.size+1)

        def dnSize(button):
            button.game.size = max(consts.MIN_BOARD_SIZE, button.game.size-1)

        buttons = [Button(self, pos=(30, 30), size=50,
                          instr=lambda button: button.game.startScreen(),
                          img=self.back_img),
                   Button(self, pos=(2*consts.W/3+60, consts.H/2-25),
                          size=50, instr=upSize, img=self.up_img),
                   Button(self, pos=(2*consts.W/3+60, consts.H/2+25),
                          size=50, instr=dnSize, img=self.down_img),
                   Button(self, pos=(2*consts.W/3-50, consts.H/2+60),
                          size=50, instr=musicInstr, txt=music_state,
                          col=consts.DARKRED),
                   Button(self, pos=(2*consts.W/3-50, consts.H/2+120),
                          size=50, instr=soundInstr, txt=sound_state,
                          col=consts.DARKRED)
                  ]

        text = [Text(instr=lambda game: 'Settings', size=100,
                     col=consts.ORANGE, pos=(consts.W/2, consts.H/4)),
                Text(instr=lambda game: 'Board size:', size=50,
                     col=consts.BLACK, pos=(consts.W/3, consts.H/2)),
                Text(instr=lambda game: game.size, size=50,
                     col=consts.BLACK, pos=(2*consts.W/3, consts.H/2)),
                Text(instr=lambda game: 'Music:', size=50,
                     col=consts.BLACK, pos=(consts.W/3, consts.H/2+60)),
                Text(instr=lambda game: 'Sound:', size=50,
                     col=consts.BLACK, pos=(consts.W/3, consts.H/2+120))
               ]

        screen(self, buttons=buttons, text=text, bg_image=self.bg_img)

    def mainGameScreen(self):
        """shows the grid and player's position"""
        buttons = [Button(self, pos=(30, 30), size=50,
                          instr=lambda button: button.game.pauseScreen(),
                          img=self.pause_img)
                  ]

        def additional(game):
            game.highlight()
            game.showGrid()
            if game.checkWin():
                game.GOScreen(game.checkWin())

        screen(self, buttons=buttons, additional=additional,
               onMousePressed=lambda game: game.tick(),
               bg_image=self.bg_img)

    def pauseScreen(self):
        """shows pause screen, returns True if the game was resumed"""
        buttons = [Button(self, pos=(consts.W/2, consts.H/3), size=80,
                          txt='Resume',
                          instr=lambda button: button.game.mainGameScreen(),
                          col=consts.ORANGE),
                   Button(self, pos=(consts.W/2, consts.H/2), size=50,
                          txt='Home',
                          instr=lambda button: button.game.startScreen(),
                          col=consts.WHITE)
                  ]

        def additional(game):
            game.showGrid()
            game.shadow()

        screen(self, buttons=buttons, additional=additional, bg_image=self.bg_img)

    def GOScreen(self, winner):
        """shows game over screen, returns True if any key is hit"""
        buttons = [Button(self, pos=(consts.W/2, 2*consts.H/3), size=50, txt='Home',
                          instr=lambda button: button.game.startScreen(),
                          col=consts.WHITE)
                  ]

        win_text, col = ('Blue', consts.BLUE) if winner == 2 else ('Green', consts.GREEN)
        text = [Text(instr=lambda game: 'GAME OVER', size=80,
                     col=consts.ORANGE, pos=(consts.W/2, consts.H/3)),
                Text(instr=lambda game: win_text+' won', size=60,
                     col=col, pos=(consts.W/2, consts.H/2))
               ]

        def additional(game):
            game.showGrid()
            game.shadow()

        screen(self, buttons=buttons, text=text, additional=additional,
               bg_image=self.bg_img)
