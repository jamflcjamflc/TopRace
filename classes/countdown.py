# -*- coding: utf8 -*-
# countdown
# helper class for toprace
# Alfredo Martin 2021

import pygame
import random
import time

version = 'countdown.v.1.0.0'


class Countdown:

    def __init__(self):
        style = pygame.font.SysFont('comicsans', 100)
        self.countlist = [style.render(str(5 - i), False, (0, 0, 255)) for i in range(5)]
        self.countlist += [style.render('GO', False, (0, 0, 255))]
        self.race = style.render('Ready for the race', False, (0, 0, 255))
        _, _, w, h = self.race.get_rect()
        self.r_race = (w, h)
        self.qualification = style.render('Ready for the qualification', False, (0, 0, 255))
        _, _, w, h = self.qualification.get_rect()
        self.r_qualification = (w, h)

    def run_countdown(self, mode, screen, track, cars, clock):
        """runs countdown or the corresponding mode. It orders the cars as well
        mode: str: tupe of countdown, could be qualification or race
        screen: instance of pygame canvas
        track: instance of Track class
        cars: list of Car instances
        returns screen"""
        random.seed(time.time())
        _, _, w, h = screen.get_rect()
        if mode == 'qualification':
            initial_order = list(range(len(cars)))
            random.shuffle(initial_order)
            for i, (rank, car) in enumerate(zip(initial_order, cars)):
                cars[i].goto_start(rank, track)
        else:
            for i, car in enumerate(cars):
                cars[i].goto_start(i, track)
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
            index = int(tac - tic)
            if index > 5:
                countdown_exit = True
            else:
                if mode == 'qualification':
                    screen.blit(self.qualification, (w / 2 - self.r_qualification[0] / 2, h / 2 - self.r_qualification[1] / 2 - 20))
                    screen.blit(self.countlist[index], (w / 2, h / 2 + 20))
                else:
                    screen.blit(self.race, (w / 2 - self.r_race[0] / 2, h / 2 - self.r_race[1] / 2 - 20))
                    screen.blit(self.countlist[index], (w/2, h/2 + 20))
            pygame.display.update()
            clock.tick(20)

        return cars





if __name__ == '__main__':
    print version
