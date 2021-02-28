# -*- coding: utf8 -*-
# intro
# helper class for toprace
# Alfredo Martin 2021

import pygame
import time
import os

version = 'intro.v.1.0.0'


class Intro:
    """the instance of this class renders the front cover and the main menu used to select
    the track that we will use for the race
    instance attributes:
    intro_image: pygame image: image to be shown in the front cover
    menu_image: pygame image: image to be shown in the menu
    """

    def __init__(self, cover_image=None, menu_image=None):
        """cover_image: filename for an image file
        screen_shape: tuple of two ints (shape of the screen)"""
        self.intro_image = pygame.image.load(cover_image)
        self.menu_image = pygame.image.load(menu_image)
        self.color = (0, 0, 0)
        self.style = pygame.font.SysFont('comicsans', 70)
        self.text = self.style.render('Select Track', False, self.color)

    def run_intro(self, screen, clock):
        """screen: pygame display instance
        clock: pygame clock instance"""
        _, _, sw, sh = screen.get_rect()
        _, _, w, h = self.intro_image.get_rect()
        width_factor = (0.9 * sw) / w
        height_factor = (0.9 * sh) / h
        sf = min(width_factor, height_factor)
        self.intro_image = pygame.transform.smoothscale(self.intro_image, (int(w * sf), int(h * sf)))

        _, _, w, h = self.intro_image.get_rect()
        keep_menu = True
        tic = time.time()
        while keep_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    keep_menu = False
                    pygame.quit()
                    quit()
            if time.time() - tic > 2:
                keep_menu = False
            screen.fill((255, 255, 255))
            screen.blit(self.intro_image, ((sw - w) // 2, (sh - h) // 2))
            pygame.display.update()
            clock.tick(20)
        return

    def run_menu(self, screen, joystick, clock):
        """screen: pygame display instance
        joystick: pygame joystick instance
        clock: pygame clock instance"""

        _, _, sw, sh = screen.get_rect()
        _, _, w, h = self.menu_image.get_rect()
        _, _, tw, th = self.text.get_rect()
        self.text = pygame.transform.scale(self.text, ((sw // 4), (th * sw) // (tw * 4)))
        _, _, tw, th = self.text.get_rect()
        old_hat = (0, 0)
        width_factor = (0.4 * sw) / w
        height_factor = (0.9 * sh) / h
        sf = min(width_factor, height_factor)
        self.menu_image = pygame.transform.smoothscale(self.menu_image, (int(w * sf), int(h * sf)))
        files = os.listdir('tracks')
        track_names = [file[:-len('_miniature.png')] for file in files if file[-len('_miniature.png'):] == '_miniature.png']
        miniatures = [pygame.image.load(os.path.join('tracks', name + '_miniature.png')) for name in track_names]
        miniatures = [pygame.transform.smoothscale(item, ((sw // 4), ((item.get_rect()[3] * sw) // (item.get_rect()[2] * 4)))) for item in miniatures]
        rects = [item.get_rect() for item in miniatures]
        active_track = 0
        _, _, w, h = self.menu_image.get_rect()
        keep_menu = True
        while keep_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                    break
            keep_menu = not joystick.get_button(1)
            change_config = joystick.get_button(2)
            if change_config:
                with open(os.path.join('resources', 'os_mask.ini'), 'r') as f:
                    lines = f.readlines()
                    line = lines[0].rstrip('\r\n')
                    if line.upper() == 'TRUE':
                        line = 'false\n'
                    else:
                        line = 'true\n'
                with open(os.path.join('resources', 'os_mask.ini'), 'w') as f:
                    f.write(line)
                print('os_mask.ini changed to ' + line)
                keep_menu = False
                pygame.quit()
                quit()
                break
            #scroll through tracks
            new_hat = joystick.get_hat(0)
            if new_hat != old_hat and old_hat == (0, 0) and new_hat[1] == -1:
                if active_track < len(track_names) - 1:
                    active_track += 1
            elif new_hat != old_hat and old_hat == (0, 0) and new_hat[1] == 1:
                if active_track > 0:
                    active_track -= 1
            old_hat = new_hat
            track_text = self.style.render(track_names[active_track], False, self.color)
            _, _, ttw, tth = track_text.get_rect()
            #track_text = pygame.transform.scale(track_text, ((sw // 4), (tth * sw) // (ttw * 4)))
            #_, _, ttw, tth = track_text.get_rect()
            screen.fill((255, 255, 255))
            screen.blit(self.menu_image, ((sw // 4) - (w // 2), (sh - h) // 2))
            #todo buscar un metodo para centrar el track y hacer un blit con el nombre del track
            screen.blit(miniatures[active_track], ((sw * 3 // 4) - (rects[active_track][2] // 2), (sh // 2) - (rects[active_track][3] // 2)))
            screen.blit(self.text, ((sw * 3 // 4) - (tw // 2), (sh // 8)))
            screen.blit(track_text, ((sw * 3 // 4) - (ttw // 2), (sh * 6 // 8)))
            pygame.display.update()
            clock.tick(20)
        return track_names[active_track]


if __name__ == '__main__':
    print(version)
