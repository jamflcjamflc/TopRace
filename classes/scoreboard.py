# -*- coding: utf8 -*-
# scoreboard
# helper class for cuatro
# Alfredo Martin 2021

import time
import numpy as np
import pygame

version = 'scoreboard.v.1.0.0'

class ScoreBoard:
    """this class represents the scoreboard
    instance attributes:
    """

    def __init__(self, track, par):
        """initiallizes the instance:
        track: instance of class Track
        par: instance of Parameters class"""
        self.style = pygame.font.SysFont('comicsans', 25)
        self.pos = track.scoreboard
        self.header_pos = self.pos + np.array([5., 5.])
        self.header1_pos = self.pos + np.array([5., 25.])
        self.header2_pos = self.pos + np.array([45., 25.])
        self.header3_pos = self.pos + np.array([90., 25.])
        self.header4_pos = self.pos + np.array([135., 25.])
        self.header5_pos = self.pos + np.array([215., 25.])
        self.header = self.style.render('remaining qualification time ', False, (255, 255, 255))
        self.header1 = self.style.render('pos', False, (255, 255, 255))
        self.header2 = self.style.render('car', False, (255, 255, 255))
        self.header3 = self.style.render('lap', False, (255, 255, 255))
        self.header4 = self.style.render('this lap', False, (255, 255, 255))
        self.header5 = self.style.render('best lap', False, (255, 255, 255))
        self.drivers = par.par['driver']
        self.n_cars = len(self.drivers)
        self.race_laps = par.par['race']
        self.q_time = par.par['qualification']
        self.tic = time.time()

    def update(self, cars, screen, mode):
        """updates de scoreboard with the last information
        cars: list of Car instances
        screen: instance of pygame canvas
        mode: str: mode of the race"""
        result = False
        tac = time.time()
        qnow = tac - self.tic
        if mode == 'race':
            cars.sort(key=lambda item: item.closest_index, reverse=True)
            cars.sort(key=lambda item: item.n_laps, reverse=True)
            self.header = self.style.render('remaining laps ' + str(self.race_laps - max([car.n_laps for car in cars])),
                                       False, (255, 255, 255))
            if self.race_laps - max([car.n_laps for car in cars]) <= 0:
                result = True
        else:
            cars.sort(key=lambda item: item.best_lap)
            self.header = self.style.render('remaining qualification time ' + self.minutes(self.q_time * 60 - qnow, False),
                                       False, (255, 255, 255))
            if self.q_time * 60 - qnow < 0:
                result = True
        position = []
        car_label = []
        n_lap = []
        this_lap = []
        best_lap = []
        for i, car in enumerate(cars):
            position.append(self.style.render(str(i + 1), False, car.color))
            car_label.append(self.style.render(car.driver, False, car.color))
            n_lap.append(self.style.render(str(car.n_laps), False, car.color))
            this_lap.append(self.style.render(self.minutes(car.this_lap, True), False, car.color))
            if car.best_lap < 10000:
                best_lap.append(self.style.render(self.minutes(car.best_lap, True), False, car.color))
            else:
                best_lap.append(self.style.render('', False, car.color))
        pygame.draw.rect(screen, (10, 10, 10), (int(self.pos[0]), int(self.pos[1]), 300, 30 + 20 * self.n_cars))
        screen.blit(self.header, self.header_pos)
        screen.blit(self.header1, self.header1_pos)
        screen.blit(self.header2, self.header2_pos)
        screen.blit(self.header3, self.header3_pos)
        screen.blit(self.header4, self.header4_pos)
        screen.blit(self.header5, self.header5_pos)
        for i in range(len(cars)):
            screen.blit(position[i], self.header1_pos + np.array([0., 20. + 15 * i]))
            screen.blit(car_label[i], self.header2_pos + np.array([0., 20. + 15 * i]))
            screen.blit(n_lap[i], self.header3_pos + np.array([0., 20. + 15 * i]))
            screen.blit(this_lap[i], self.header4_pos + np.array([0., 20. + 15 * i]))
            screen.blit(best_lap[i], self.header5_pos + np.array([0., 20. + 15 * i]))
        return result, screen

    def minutes(self, this_time, r_decimas):
        """this function returns a string with the time in minutes:seconds:decimas or
        minutes:seconds depending whether r_decimas is True of False
        this_time : float
        r_decimas : bool
        returns : result (str)"""
        minutes = int(this_time // 60)
        seconds = int(this_time % 60)
        decimas = int(100 * ((this_time % 60) - seconds))
        if r_decimas:
            result = str(minutes).rjust(2, '0') + ':' + str(seconds).rjust(2, '0') + ':' + str(decimas).rjust(2, '0')
        else:
            result = str(minutes).rjust(2, '0') + ':' + str(seconds).rjust(2, '0')
        return result


if __name__ == '__main__':
    print(version)
