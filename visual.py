"""All visual functions, Button class and screen template function"""

from collections import namedtuple
from math import sqrt
import sys
import pygame as pg

import consts
from algs import inRect, point

def drawHex(surface, col_in: 'inside colour', col_out: 'bounds colour', pos, a):
    x, y = pos
    points = [(x-a/2, y-a*sqrt(3)/2),
              (x+a/2, y-a*sqrt(3)/2),
              (x+a, y),
              (x+a/2, y+a*sqrt(3)/2),
              (x-a/2, y+a*sqrt(3)/2),
              (x-a, y)]
    pg.draw.polygon(surface, col_in, points)
    pg.draw.polygon(surface, col_out, points, 4)

def textRect(txt, size):
    """Return the rectangle of the text"""
    font = pg.font.SysFont('Verdana', size)
    text = font.render(txt, False, consts.BLACK)
    return text.get_rect()

def textOut(surface, data, size, col, pos):
    txt = str(data)
    font = pg.font.SysFont('Verdana', size)
    text = font.render(txt, False, col)
    rect = text.get_rect(center=pos)
    surface.blit(text, rect)

def textOutMultiline(surface, txt, size, col, pos):
    font = pg.font.SysFont('Verdana', size)
    for y, line in enumerate(txt.split('\n')):
        text = font.render(line, False, col)
        rect = text.get_rect(center=(pos[0], pos[1]+(y+5)*size))
        surface.blit(text, rect)


class Button:
    """pos - center of the buttons
    size - scaled width
    instr - function executed when the button is pressed
    txt, img - text or the image of the button (text has higher priority)
    col - colour of the text
    """

    def __init__(self, game, pos, size, instr: 'function', txt='', img=None, col=consts.BLACK):
        self.game = game
        self.pos = pos
        self.col = col
        self.text = txt
        self.img = img
        self.instr = instr
        self.original_size = self.size = size
        if img:
            # create smaller and bigger copies of an image for highlighting
            img_w, img_h = self.img.get_rect().size
            scale = self.size/img_w
            self.smaller_img = pg.transform.scale(self.img, (int(img_w*scale),
                                                             int(img_h*scale)))
            scale = (self.size+5)/img_w
            self.bigger_img = pg.transform.scale(self.img, (int(img_w*scale),
                                                            int(img_h*scale)))

        self.rect = None
        if txt:
            self.rect = textRect(txt, size)
        elif img:
            self.rect = self.smaller_img.get_rect()

    def params_(self):
        """returns the top left corner point as well as width and height"""
        return (self.pos[0] + self.rect.left - self.rect.width/2,
               self.pos[1] + self.rect.top - self.rect.height/2,
               self.rect.width,
               self.rect.height)

    def highlighted(self):
        """Is called if the mouse is above the button.
        Changes the size of the button
        """
        x, y, w, h = self.params_()
        pos = pg.mouse.get_pos()
        if inRect(point(pos), x, y, w, h):
            self.size = self.original_size + 5
        else:
            self.size = self.original_size

    def triggered(self):
        """Checks if the button is pressed and runs self.instr() if it is"""
        x, y, w, h = self.params_()
        pos = pg.mouse.get_pos()
        if inRect(point(pos), x, y, w, h):
            if self.game.click_sound_channel and self.game.click_sound\
               and self.game.sound_state:
                self.game.click_sound_channel.play(self.game.click_sound)
            self.instr(self)

    def imgUpdate(self):
        if self.img:
            if self.size > self.original_size:
                self.img = self.bigger_img
            else:
                self.img = self.smaller_img

    def show(self):
        if self.text:
            textOut(self.game.screen, self.text, self.size, self.col, self.pos)
        elif self.img:
            self.imgUpdate()
            img_w, img_h = self.img.get_rect().size
            self.game.screen.blit(self.img, (self.pos[0]-img_w/2,
                                             self.pos[1]-img_h/2))
        #x, y, w, h = self.params_()
        #pg.draw.rect(surface, self.col, (x, y, w, h), 2)


def screen(game, buttons=[],
        text: [namedtuple('Text', 'instr size col pos')] = [],
        onMousePressed: 'function' = None,
        additional: 'function' = None,
        bg_image=None):
    """shows a screen, quits if the cross was pressed"""
    # initializing buttons
    while True:
        # sticking to fps
        pg.time.Clock().tick(consts.FPS)

        # --------------------EVENTS---------------------
        for event in pg.event.get():
            if event.type == pg.QUIT:
                # if exit button is pressed
                pg.quit()
                sys.exit(0)
            elif event.type == pg.MOUSEBUTTONDOWN:
                try:
                    onMousePressed(game)
                except TypeError:
                    pass
                # if mouse is pressed check button overlapping
                for button in buttons:
                    button.triggered()

        # highlight buttons
        for button in buttons:
            button.highlighted()

        # --------------------STUFF-----------------------
        # display background
        if bg_image:
            game.screen.blit(bg_image, (0, 0))
        try:
            additional(game)
        except TypeError:
            pass

        # display all the text
        for txt in text:
            textOut(game.screen, txt.instr(game), txt.size, txt.col, txt.pos)

        # show buttons
        for button in buttons:
            button.show()

        # double processing
        pg.display.flip()
