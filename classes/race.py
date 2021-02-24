# -*- coding: utf8 -*-
# race
# helper class for toprace
# Alfredo Martin 2021

import pygame
import os

version = 'race.v.1.0.0'


class Race:

    def __init__(self, file):
        """initializes the instance
        file: filename for the log file"""
        self.log_file = file
        if not os.path.isfile(self.log_file):
            with open(self.log_file, 'w') as f:
                pass

    def update_announcements(self, screen, announcements):
        """blits announcements and eliminates the ones obsolete
        screen: pygame canvas object
        announcements: list of Announcement instances
        returns: announcements: list of Announcement instances"""
        for announcement in announcements:
            announcement.update(screen)
        announcements = [announcement for announcement in announcements if announcement.active]
        return announcements

    def move_cars(self, track, joysticks, cars, par):
        """moves the cars"""
        for i, car in enumerate(cars):
            if car.index < len(joysticks):
                command = (joysticks[car.index].get_axis(4), joysticks[car.index].get_axis(3))
                cars[i].move_car(track, command, cars, par)  # player directed
            else:
                cars[i].move_car(track, None, cars, par)  # auto directed
        return cars

    def draw_cars(self, screen, cars):
        """blits each car in the screen
        screen; pygame canvas instance
        cars: list of Car instances
        returns: screen; pygame canvas instance"""
        for car in cars:
            screen = car.draw_checkpoint(screen)
        for car in cars:
            screen = car.draw_car(screen)
        return screen

    def run_race(self, mode, screen, track, cars, scoreboard, announcements, joysticks, parameters, clock):
        """runs the race
        mode: str : race or qualification
        screen: pygame canvas instance
        track: instance of Track class
        cars: list of Car class instances
        scoreboard: instance of Scoreboard class
        announcements: list of Announcement class instances
        joysticks: list of pygame.joystick.Joystick instances
        clock: pygame.time.Clock instance
        returns cars: list of Car class instances"""
        race_exit = False
        while not race_exit:
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                    race_exit = True
            screen.fill((255, 255, 255))
            screen.blit(track.image, (0, 0))
            cars = self.move_cars(track, joysticks, cars, parameters)
            result, screen = scoreboard.update(cars, screen, mode)
            screen = self.draw_cars(screen, cars)
            announcements = self.update_announcements(screen, announcements)
            pygame.display.update()
            clock.tick(20)
            race_exit = race_exit or result
        return cars


if __name__ == '__main__':
    print version
