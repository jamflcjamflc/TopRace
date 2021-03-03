# -*- coding: utf8 -*-
# announcement
# helper class for toprace
# Alfredo Martin 2021

import pygame

version = 'announcement.v.1.0.0'


class Announcement:

    def __init__(self, screen=None, text='', time=5, color=(255, 0, 0)):
        """initiallizes the Announcement instance
        screen: pygame canvas instance
        text: str
        time: int (number of frames during which the announcement will be active
        color: color of the text"""
        _, _, sw, sh = screen.get_rect()
        self.t = 0
        self.color = color
        self.time = time
        self.active = True
        style = pygame.font.SysFont('comicsans', 70)
        self.text = style.render(text, False, self.color)
        _, _, w, h = self.text.get_rect()
        text_x = (sw / 2) - (w / 2)
        text_y = (sh / 2) - (h / 2)
        self.pos = (text_x, text_y)

    def update(self, screen):
        """updates the announcements (whether they are active or not) and blits
        announcements in the screen
        screen: pygame canvas instance
        returns: screen after being updated"""
        self.t += 1
        self.active = self.t <= self.time
        screen.blit(self.text, self.pos)
        return screen


if __name__ == '__main__':
    print(version)
