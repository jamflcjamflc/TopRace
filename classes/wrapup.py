# -*- coding: utf8 -*-
# wrapup
# helper class for toprace
# Alfredo Martin 2021

import pygame

version = 'wrapup.v.1.0.0'


class Wrapup:
    """the instance of this class renders the wrap up menu used to exit the game or
    start a new game
    instance attributes:
    wrapup_image: pygame image: image to be shown in the front cover
    """

    def __init__(self, wrapup_image=None):
        """wrapup_image: filename for an image file
        screen_shape: tuple of two ints (shape of the screen)"""
        self.wrapup_image = pygame.image.load(wrapup_image)
        self.color = (0, 0, 0)

    def run_wrapup(self, screen, joystick, clock):
        """screen: pygame display instance
        joystick: pygame joystick instance
        clock: pygame clock instance"""

        _, _, sw, sh = screen.get_rect()
        _, _, w, h = self.wrapup_image.get_rect()
        width_factor = (0.9 * sw) / w
        height_factor = (0.9 * sh) / h
        sf = min(width_factor, height_factor)
        self.wrapup_image = pygame.transform.smoothscale(self.wrapup_image, (int(w * sf), int(h * sf)))
        keep_menu = True
        new_game = False
        exit_game = False
        while keep_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                    break
            exit_game = joystick.get_button(2)
            new_game = joystick.get_button(1)
            keep_menu = not exit_game and not new_game
            screen.fill((255, 255, 255))
            screen.blit(self.wrapup_image, ((sw // 2) - (w // 2), (sh - h) // 2))
            pygame.display.update()
            clock.tick(20)
        if new_game:
            return 'new_game'
        else:
            return 'exit_game'


if __name__ == '__main__':
    print(version)
