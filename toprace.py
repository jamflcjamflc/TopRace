# -*- coding: utf8 -*-
# toprace
# main toprace script
# Alfredo Martin 2021

import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (90, 30)  # positions the screen in a specific position of the monitor
import pygame
import numpy as np
import random
import argparse
import time
from classes.intro import Intro
from classes.track import Track
from classes.parameters import Parameters
from classes.car import Car

from classes.scoreboard import ScoreBoard
from classes.race import Race
from classes.countdown import Countdown
from classes.display_result import DisplayResult
from classes.wrapup import Wrapup


# positions the screen in a specific position of the monitor
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (90, 30)

def initiallize_game(n_joys):
    """initiallizes the game
    n_joys: number of game pads detected"""
    # initiallizing screen
    # todo code the parameters used soft instead of hard
    countdown = Countdown()
    result_displayer = DisplayResult()
    wrapup = Wrapup(wrapup_image=os.path.join('images', 'wrapup.png'))
    race1 = Race(os.path.join('data', 'log.log'), race_type='qualification')
    race2 = Race(os.path.join('data', 'log.log'), race_type='race')
    # resizes the screen to the resolution of the monitor
    x_res, y_res = pygame.display.Info().current_w, pygame.display.Info().current_h
    screen_width = int(0.9 * x_res)
    screen_height = int(0.9 * y_res)
    screen = pygame.display.set_mode((screen_width, screen_height))
    intro = Intro(cover_image=os.path.join('images', 'main_cover.png'),
                  menu_image=os.path.join('images', 'track_menu.png'))
    announcements = []
    music = pygame.mixer.Sound(os.path.join('sounds', 'music.wav'))
    music.set_volume(0.3)
    noise = pygame.mixer.Sound(os.path.join('sounds', 'background.wav'))
    noise.set_volume(0.3)
    return screen, intro, announcements, music, noise, countdown, race1, race2, result_displayer, wrapup

def create_cars(par, track, screen):
    """creates the list of cars
    par: instance of Parameters class
    track: instance of Track class
    screen: instance of pygame canvas
    returns: list of instances of class Car"""
    cars = [Car(i, par, track, screen) for i in range(len(par.par['driver']))]
    return cars


if __name__ == '__main__':
    pygame.display.init()
    pygame.mixer.init()
    pygame.font.init()
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    for joystick in joysticks:
        joystick.init()
    screen, intro, announcements, music, noise, countdown, race1, race2, result_displayer, wrapup = initiallize_game(len(joysticks))
    _, _, w, h = screen.get_rect()
    clock = pygame.time.Clock()
    # read the parameters file
    parameters = Parameters(path=os.path.join('resources', 'par.ini'))
    output = 'new_game'
    while output == 'new_game':  # make a loop here
        # Run the intro, select the track and prepare the track image
        music.play(loops=-1)
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
        noise.play(loops=-1)
        cars = countdown.run_countdown('qualification', screen, track, cars, clock)
        cars = race1.run_race('qualification', screen, track, cars, scoreboard, announcements, joysticks, parameters, clock)
        result_displayer.run_results('qualification', screen, track, cars, clock)
        cars = countdown.run_countdown('race', screen, track, cars, clock)
        cars = race2.run_race('race', screen, track, cars, scoreboard, announcements, joysticks, parameters, clock)
        result_displayer.run_results('race', screen, track, cars, clock)
        output = wrapup.run_wrapup(screen, joysticks[0], clock)
        music.stop()
        noise.stop()

    pygame.quit()
    quit()



