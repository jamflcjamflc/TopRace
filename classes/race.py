# -*- coding: utf8 -*-
# race
# helper class for toprace
# Alfredo Martin 2021

import pygame
import os
from classes.announcement import Announcement
import time

version = 'race.v.1.0.0'


class Race:

    def __init__(self, file, race_type='qualification'):
        """initializes the instance
        file: filename for the log file
        race_type: str: type of race"""
        self.race_type = race_type
        self.timestamp = time.asctime(time.gmtime())
        self.log_file = os.path.join('data', 'log.log')
        if not os.path.isdir('data'):
            os.mkdir('data')
        if not os.path.isfile(self.log_file):
            with open(self.log_file, 'w') as f:
                line = 'time_stamp\ttrack\tresolution\tn_laps\ttype\tcar\tbest_lap\trank\n'
                f.write(line)
        with open(os.path.join('resources', 'os_mask.ini'), 'r') as f:
            lines = f.readlines()
            self.invert_axes = lines[0].rstrip('\r\n').upper() == 'TRUE'
        if self.invert_axes:
            self.x_axis = 3
            self.y_axis = 4
        else:
            self.x_axis = 4
            self.y_axis = 3

    def update_announcements(self, screen, announcements):
        """blits announcements and eliminates the ones obsolete
        screen: pygame canvas object
        announcements: list of Announcement instances
        returns: tuple of screen and announcements after being updated"""
        for announcement in announcements:
            screen = announcement.update(screen)
        announcements = [announcement for announcement in announcements if announcement.active]
        return screen, announcements

    def move_cars(self, screen, track, joysticks, cars, par, announcements):
        """moves the cars and appends new announcements
        screen: pygame canvas instance
        track: instance of Track class
        joysticks: list of pygame.joystick instances
        cars: list of instances of Car class
        par: instance of Parameters class
        announcements: list of instances of Announcement class
        returns: tuple of updated cars and announcements"""
        for i, car in enumerate(cars):
            cars[i].get_closest_index(track)
        for i, car in enumerate(cars):
            this_announcement = cars[i].calculate_loops(par, track, cars)
            if this_announcement is not None:
                announcements.append(Announcement(screen=screen,
                                                  text=this_announcement,
                                                  time=9,
                                                  color=car.color))
        for i, car in enumerate(cars):
            cars[i].get_orientation()
        for i, car in enumerate(cars):
            if car.index < len(joysticks):
                command = (joysticks[car.index].get_axis(self.x_axis), joysticks[car.index].get_axis(self.y_axis))
                cars[i].calculate_force(command, cars)  # player directed
            else:
                cars[i].calculate_force(None, cars)  # auto directed
        for i, car in enumerate(cars):
            cars[i].calculate_new_pos()
        return cars, announcements

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

    def update_file(self, cars, track):
        """updates the log file
        cars: list of instances of Car class"""
        if self.race_type == 'qualification':
            cars.sort(key=lambda item: item.best_lap)
        else:
            cars.sort(key=lambda item: item.closest_index, reverse=True)
            cars.sort(key=lambda item: item.n_laps, reverse=True)
        with open(self.log_file, 'a') as f:
            for i, car in enumerate(cars):
                line = ''
                line += self.timestamp + '\t'
                line += track.name + '\t'
                line += str(track.w) + ':' + str(track.h) + '\t'
                line += str(car.n_laps) + '\t'
                line += self.race_type + '\t'
                line += car.driver + '\t'
                line += str(car.best_lap) + '\t'
                line += str(i + 1) + '\n'
                f.write(line)

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
            cars, announcements = self.move_cars(screen, track, joysticks, cars, parameters, announcements)
            result, screen = scoreboard.update(cars, screen, mode)
            screen, announcements = self.update_announcements(screen, announcements)
            screen = self.draw_cars(screen, cars)
            pygame.display.update()
            clock.tick(20)
            race_exit = race_exit or result
        self.update_file(cars, track)
        return cars


if __name__ == '__main__':
    print(version)
