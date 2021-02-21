# -*- coding: utf8 -*-
# toprace
# main toprace script
# Alfredo Martin 2021

import pygame
import numpy as np
import os
import random
import argparse
import time
from classes.intro import Intro
from classes.track import Track
from classes.parameters import Parameters
from classes.car import Car
from classes.announcement import Announcement
from classes.scoreboard import ScoreBoard


# positions the screen in a specific position of the monitor
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (90, 30)

def initiallize_game(n_joys):
    """initiallizes the game
    n_joys: number of game pads detected"""
    # initiallizing screen
    # todo code the parameters used soft instead of hard
    screen = pygame.display.set_mode((1200, 800))
    intro = Intro(cover_image=os.path.join('images', 'main_cover.png'),
                  menu_image=os.path.join('images', 'track_menu.png'),
                  music=os.path.join('sounds', 'music.wav'))
    announcements = []
    return screen, intro, announcements

def update_announcements(screen, announcements):
    """blits announcements and eliminates the ones obsolete
    screen: pygame canvas object
    announcements: list of Announcement instances
    returns: announcements: list of Announcement instances"""
    for announcement in announcements:
        announcement.update(screen)
    announcements = [announcement for announcement in announcements if announcement.active]
    return announcements

def create_cars(par, track, screen):
    """creates the list of cars
    par: instance of Parameters class
    track: instance of Track class
    screen: instance of pygame canvas
    returns: list of instances of class Car"""
    cars = [Car(i, i, par, track, screen) for i in range(len(par.par['driver']))]
    return cars

def draw_cars(screen, cars):
    """blits each car in the screen
    screen; pygame canvas instance
    cars: list of Car instances
    returns: screen; pygame canvas instance"""
    for car in cars:
        screen = car.draw_car(screen)
    return screen

def move_cars(track, command, cars, par):
    for i, car in enumerate(cars):
        cars[i].move_car(track, command, cars, par)
    return cars

if __name__ == '__main__':
    pygame.display.init()
    pygame.mixer.init()
    pygame.font.init()
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    for joystick in joysticks:
        joystick.init()
    screen, intro, announcements = initiallize_game(len(joysticks))
    _, _, w, h = screen.get_rect()
    clock = pygame.time.Clock()
    # read the parameters file
    parameters = Parameters(path=os.path.join('resources', 'par.ini'))
    # Run the intro, select the track and prepare the track image
    intro.run_intro(screen, clock)
    track_name = intro.run_menu(screen, joysticks[0], clock)
    track = Track()
    track.load_track(track_name)
    track.resize_track((w, h))
    track.reduce_track(4)
    track.create_track_image()
    track.get_boxes(len(parameters.par['driver']))  # creates one box for each car
    cars = create_cars(parameters, track, screen)
    scoreboard = ScoreBoard(track, parameters)
    announcements.append(Announcement(screen=screen, text='Ready for the qualification', time=50))

    game_exit = False
    while not game_exit:
        # event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                game_exit = True
        screen.fill((255, 255, 255))
        screen.blit(track.image, (0, 0))
        cars = move_cars(track, None, cars, parameters)
        result, screen = scoreboard.update(cars, screen, 'qualification')
        screen = draw_cars(screen, cars)
        announcements = update_announcements(screen, announcements)
        pygame.display.update()
        clock.tick(20)
        game_exit = result
    pygame.quit()
    quit()



