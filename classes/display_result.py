# -*- coding: utf8 -*-
# display_result
# helper class for toprace
# Alfredo Martin 2021

import pygame
import random
import time

version = 'display_result.v.1.0.0'


class DisplayResult:
    """class intended to display the results of the qualification or the race"""

    def __init__(self):
        """initiallizes the class"""
        self.style = pygame.font.SysFont('comicsans', 80)
        self.race = self.style.render('the winner is:', False, (0, 0, 255))
        _, _, w, h = self.race.get_rect()
        self.r_race = (w, h)
        self.qualification = self.style.render('Pole position for:', False, (0, 0, 255))
        _, _, w, h = self.qualification.get_rect()
        self.r_qualification = (w, h)

    def run_results(self, mode, screen, track, cars, clock):
        """runs countdown or the corresponding mode. It orders the cars as well
        mode: str: tupe of countdown, could be qualification or race
        screen: instance of pygame canvas
        track: instance of Track class
        cars: list of Car instances
        returns screen"""
        _, _, w, h = screen.get_rect()
        screen.fill((255, 255, 255))
        screen.blit(track.image, (0, 0))
        tic = time.time()
        countdown_exit = False
        while not countdown_exit:
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                    countdown_exit = True
            screen.fill((255, 255, 255))
            screen.blit(track.image, (0, 0))
            for car in cars:
                screen = car.draw_car(screen)
            tac = time.time()
            if tac - tic > 5:
                countdown_exit = True
            if mode == 'qualification':
                screen.blit(self.qualification, (w / 2 - self.r_qualification[0] / 2, h / 2 - self.r_qualification[1] / 2 - 20))
            else:
                screen.blit(self.race, (w / 2 - self.r_race[0] / 2, h / 2 - self.r_race[1] / 2 - 20))
            winner = self.style.render(cars[0].driver, False, cars[0].color)
            screen.blit(winner, (w/2, h/2 + 20))
            pygame.display.update()
            clock.tick(20)
        return None





if __name__ == '__main__':
    print version
