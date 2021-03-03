# -*- coding: utf8 -*-
# car
# helper class for toprace
# Alfredo Martin 2021

import pygame
import numpy as np
import time

version = 'car.v.1.0.0'


class Car:
    """Class covering the car. Each car in the race is an instance of the Car class
    instance attributes:
    """

    def __init__(self, index,  par, track, screen):
        """initializes the class
        a : float (initial angle of the car)
        rank : int (initial rank order of the car)
        index: int (index of the car, this helps to extract attributes from parameters)
        par : instance of Parameters class
        track: instance of Track class (track in which the car will race)
        screen: instance of pygame canvas"""
        self.fwd_dist = 12
        chasis = np.array([(-21, -3), (-18, -6), (-15, -3), (-9, -3), (-6, -6), (0, -6), (3, -3), (9, -3), (12, -6),
                           (15, -6), (15, 6), (12, 6), (9, 3), (3, 3), (0, 6), (-6, 6), (-9, 3), (-15, 3), (-18, 6),
                           (-21, 3)])
        weel1 = np.array([(-15, 3), (-15, 9), (-9, 9), (-9, 3)])
        weel2 = np.array([(-15, -3), (-15, -9), (-9, -9), (-9, -3)])
        weel3 = np.array([(3, 5), (3, 8), (9, 8), (9, 5)])
        weel4 = np.array([(3, -5), (3, -8), (9, -8), (9, -5)])
        axis1 = np.array([(5, 3), (5, 5), (7, 5), (7, 3)])
        axis2 = np.array([(5, -3), (5, -5), (7, -5), (7, -3)])
        window = np.array([(-3, 3), (0, 3), (3, 0), (0, -3), (-3, -3)])
        self.points = np.concatenate([chasis, weel1, weel2, weel3, weel4, axis1, axis2, window], axis=0)
        self.points = self.points.astype('float32')
        self.chasis = tuple(range(0, 20))
        self.weel1 = tuple(range(20, 24))
        self.weel2 = tuple(range(24, 28))
        self.weel3 = tuple(range(28, 32))
        self.weel4 = tuple(range(32, 36))
        self.axis1 = tuple(range(36, 40))
        self.axis2 = tuple(range(40, 44))
        self.window = tuple(range(44, 49))
        self.points -= self.points.mean(axis=0)
        scaling_factor = (self.points.max(axis=0) - self.points.min(axis=0)).max()
        self.points /= scaling_factor  # now the car is resized so the long axis equals to 1.0
        self.points *= track.width * 1.2  # Now the car is rescaled with respect to the width of the track
        self.parts = [self.chasis, self.weel1, self.weel2, self.weel3, self.weel4, self.axis1, self.axis2, self.window]
        self.huv = np.array([1., 0.])  # horizontal unit vector used to rotate the car
        _, _, w, h = screen.get_rect()
        self.res = np.array([float(w), float(h)])
        self.rank = index  # initial rank of the car
        self.index = index  # index of this car
        self.color = par.par['car_colors'][self.index]  # color of the car
        self.colors = [self.color] + [(0, 0, 0) for _ in range(6)] + [(0, 0, 255)]  # color for each part of the car
        self.driver = par.par['driver'][self.index]
        self.m = par.par['car_mass'][self.index]  # mass of this car
        self.lateral_drag = par.par['lateral_drag']
        self.collision_distance = par.par['collision_distance']
        self.collision_constant = par.par['collision_constant']
        self.on_road_drag = par.par['on_road_drag']
        self.off_road_drag = par.par['off_road_drag']
        self.max_speed = par.par['max_speed'][self.index]
        self.pos = np.copy(track.track[track.boxes[self.rank]])  # initial position of the car (vector indicating position)
        if track.boxes[self.rank] + self.fwd_dist < track.track.shape[0]:
            self.fwd_index = track.boxes[self.rank] + self.fwd_dist
        else:
            track.boxes[self.rank] + self.fwd_dist - track.track.shape[0]
        self.fwd_pos = track.track[self.fwd_index]
        self.dir = track.get_vector(track.boxes[self.rank], track.boxes[self.rank] + 1)  # unit vector indicatind the direction of the car
        self.track_size = track.track.shape[0]
        self.track_width = track.width
        self.checkpoint_index = track.checkpoint_index  # indexes of the points in the track closest to each checkpoint
        self.checkpoint = track.checkpoint  # coordinates of the different checkpoint
        self.last_time = time.time()  # this is the time to start counting a lap
        self.n_laps = - 1  # number of laps run
        self.this_lap = 0.0  # time taken to run this lap
        self.last_lap = 0.0  # time taken to run last lap
        self.best_lap = 10000.0  # time of best lap
        self.v = np.array([0., 0.])  # current velocity
        self.v_l = np.array([0., 0.])  # longitudinal velocity
        self.v_n = np.array([0., 0.])  # normal velocity
        self.f = np.array([0., 0.])  # combined force for the car
        self.f_n = np.array([0., 0.])  # normal drag force
        self.f_l = np.array([0., 0.])  # longitudinal drag force
        self.f_c = np.array([0., 0.])  # force coming from a collision
        self.acceleration = np.array([0., 0.])  # acceleration of the car
        self.command = np.array([0., 0.])  # external force applied
        self.scalar_command = 0.  # magnitude of the force applied to the car in the forward direction
        self.command_center = (0, 0)  # position of the command display for this car ????
        self.drag = 100.0  # current drag  ????
        self.current_check = 0  # index of the last checkpoint checked ##
        self.next_check = 0  # index of the next point checked ##
        self.info = None  # dictionary including info useful for getting the next command in auto cars
        self.closest_index = track.boxes[self.rank]  # index of the track point that is the closest to the car
        self.on_road = True  # whether the car is in the road (True) or off the road (False)
        self.orientation = 1  # initial orientation of the car, (for auto-cars, they go with the track)
        self.in_checkpoint = -1  # in in a checkpoint indicates the checkpoint index otherwise -1

    def goto_start(self, rank, track):
        """positions the car at the start of the race in the position indicated by rank
        rank: int: initial rank for this car
        track: instance of Track class"""
        self.rank = rank
        self.current_check = 0
        self.next_check = 0
        self.last_time = time.time()  # this is the time to start counting a lap
        self.n_laps = - 1  # number of laps run
        self.this_lap = 0.0  # time taken to run this lap
        self.last_lap = 0.0  # time taken to run last lap
        self.best_lap = 10000.0  # time of best lap
        self.v = np.array([0., 0.])  # current velocity
        self.v_l = np.array([0., 0.])  # longitudinal velocity
        self.v_n = np.array([0., 0.])  # normal velocity
        self.pos = np.copy(track.track[track.boxes[self.rank]])
        if track.boxes[self.rank] + self.fwd_dist < track.track.shape[0]:
            self.fwd_index = track.boxes[self.rank] + self.fwd_dist
        else:
            track.boxes[self.rank] + self.fwd_dist - track.track.shape[0]
        self.fwd_pos = track.track[self.fwd_index]
        self.dir = track.get_vector(track.boxes[self.rank], track.boxes[self.rank] + 1)

    def get_closest_index(self, track):
        """ this function updates the index for the track point that is the closest to this car
        track: instance of the class Track
        returns : None"""
        # consider reducing the number of points in the track searched if the calculation slows down the race
        dists2 = ((track.track - self.pos.reshape(1, 2)) ** 2).sum(axis=1)
        self.closest_index = np.argmin(dists2)
        if dists2[self.closest_index] <= track.width ** 2:
            self.on_road = True
        else:
            self.on_road = False
        if self.orientation == 1:
            self.fwd_index = self.closest_index + self.fwd_dist if self.closest_index < self.track_size - self.fwd_dist else self.track_size - self.closest_index + self.fwd_dist
        else:
            self.fwd_index = self.closest_index - self.fwd_dist if self.closest_index > self.fwd_dist - 1 else self.track_size + self.closest_index - self.fwd_dist
        self.fwd_pos = track.track[self.fwd_index]

    def get_orientation(self):
        """updates the orientation parameter, +1 if forward, -1 if backward
        returns None"""
        if self.next_check == 0:  # next checkpoint is 0
            if self.track_size - self.closest_index < self.track_size // 2:  # going forward is shorter
                self.orientation = 1
            else:  # going backward is shorter
                self.orientation = -1
        else:  # next checkpoint is not 0
            if self.checkpoint_index[self.next_check] > self.closest_index:  # next checkpoint is ahead
                if self.checkpoint_index[self.next_check] - self.closest_index < self.track_size // 2:  # going forward is shorter
                    self.orientation = 1
                else:  # is shorter going backwards
                    self.orientation = -1
            else:  # next checkpoint is behind
                if self.closest_index - self.checkpoint_index[self.next_check] < self.track_size // 2:  # it is shorter going backward
                    self.orientation = -1
                else:  # it is shorter going forward
                    self.orientation = 1

    def calculate_force(self, command, cars):
        """ this calculates the force that is the sum of all forces affecting the car, and also its new direction
        command : tuple of float (external force)
        cars : list of instances of car Class
        """
        if command is None:  # the car drives automatically, we calculate self command before going on
            fwd_vector = self.fwd_pos - self.pos
            self.command = self.max_speed * fwd_vector / np.linalg.norm(fwd_vector)
        else:  # the command is received so the car does not run automatically
            self.command = self.max_speed * np.array(command)  # gets the command

        self.scalar_command = np.linalg.norm(self.command)
        # if the joy axes are close to the center the car direction does not change and no force is applied
        if self.scalar_command < 0.1:
            self.command = np.array([0., 0.])
            self.scalar_command = 0.0
            # self.dir is maintained unchanged
        else:
            self.dir = self.command / self.scalar_command  # unit vector in the direction of the car
        # this part calculates the normal drag force. Remember that selc.scalar_command is not 0. by definition
        self.v_l = self.dir * np.dot(self.v, self.dir)  # longitudinal velocity
        self.v_n = self.v - self.v_l  # normal velocity
        # calculates the force
        self.f_n = - self.v_n * self.lateral_drag
        # calculate the longitudinal drag and the longitudinal drag force
        if self.on_road:
            self.f_l = -self.v_l * self.on_road_drag
        else:
            self.f_l = -self.v_l * self.off_road_drag
        # this part calculates the collision forces
        self.f_c = np.array([0., 0.])
        for car in cars:
            collision_vector = self.pos - car.pos
            distance = np.linalg.norm(collision_vector)
            if self.collision_distance > distance > 0.1:  # this ensures a car does not crash into itself
                collision_vector /= distance
                self.f_c += collision_vector * min(1., self.collision_distance - distance) * self.collision_constant
        self.f = self.f_c + self.f_l + self.f_n + self.command

    def calculate_new_pos(self):
        self.acceleration = self.f / self.m
        self.v += self.acceleration
        self.pos += self.v
        # now we rebound the car if it has gone out of the limits of the screen
        if (self.pos[0] < 0 and self.v[0] < 0) or (self.pos[0] > self.res[0] and self.v[0] > 0):
            self.v *= np.array([-1., 1.])
        if (self.pos[1] < 0 and self.v[1] < 0) or (self.pos[1] > self.res[1] and self.v[1] > 0):
            self.v = (self.v[0], -self.v[1])

    def draw_car(self, screen):
        """this method rotates the car, translates it ot its final ppsition and blits the car into the screen
        screen: pygame canvas instance
        returns: screen: pygame canvas instance"""
        sina = np.cross(self.huv, self.dir)  # sin of the angle with the horizontal line pointing to the right
        cosa = np.dot(self.huv, self.dir)  # cos of the angle with the horizontal line pointing to the right
        rot_matrix = np.array([[cosa, -sina], [sina, cosa]])  # rotation matrix
        points = self.pos.reshape(1, 2) + np.dot(self.points, rot_matrix.T)
        for i, part in enumerate(self.parts):
            pygame.draw.polygon(screen, self.colors[i], np.take(points, part, axis=0))
        return screen

    def draw_checkpoint(self, screen):
        """draws the checkpoint in the screeen if required
        screen: pygame canvas instance
        returns: screen: pygame canvas instance"""
        if self.in_checkpoint > -1:
            pygame.draw.circle(screen, self.color, self.checkpoint[self.in_checkpoint], int(self.track_width))
        return screen

    def calculate_loops(self, par, track, cars):
        """this function checks that the car has passed for all the checkpoints and then updates the
        number of loops, time spent in the current loop
        par : dictionary
        track : dictionary of lists of tuples"""
        # this part updates the checks of the loops
        this_announcement = None
        self.this_lap = time.time() - self.last_time
        check_distance = np.linalg.norm(self.checkpoint[self.next_check] - self.pos)
        if check_distance <= self.track_width:
            self.in_checkpoint = self.next_check
        else:
            self.in_checkpoint = -1
        if self.in_checkpoint > -1:  # we are at a checkpoint
            if self.next_check == 0 and self.n_laps == -1:  # the race starts now
                self.last_lap = self.this_lap
                self.last_time = time.time()
                self.n_laps += 1
            elif self.next_check == 0 and self.n_laps > -1:  # the rece is already in place
                self.n_laps += 1
                self.last_lap = self.this_lap
                self.last_time = time.time()
                if self.last_lap < min([car.best_lap for car in cars]):
                    self.best_lap = self.last_lap
                    this_announcement = 'Best lap:  ' + str(round(self.best_lap, 2)) + ' sec'
                elif self.last_lap < self.best_lap:  # the lap has not completed with record
                    self.best_lap = self.last_lap
                    this_announcement = 'Best personal lap:  ' + str(round(self.best_lap, 2)) + ' sec'
            # update the next checkpoint
            if len(self.checkpoint_index) == self.next_check + 1:
                self.next_check = 0
            else:
                self.next_check += 1
        return this_announcement

    def move_car(self, track, command, cars, par):
        """wrapper for all the functions except the drawing of the car
        track: instance of Track class
        command: tuple of two floats or None
        cars: list of Car instances
        par: Parameters instance"""
        self.get_closest_index(track)
        self.calculate_loops(par, track, cars)
        self.get_orientation()
        self.calculate_force(command, cars)
        self.calculate_new_pos()


if __name__ == '__main__':
    print(version)
