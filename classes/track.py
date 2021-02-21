# -*- coding: utf8 -*-
# track
# helper class for toprace
# Alfredo Martin 2021

import numpy as np
import pygame
import os
import pickle as pic

version = 'track.v.1.0.0'


class Track:
    """The instance of this class controls the creation and usage of the track
    instance attributes:
    track_pixel: tuple of three ints: color of the track pixels in the raw track image
    checkpoint_pixel: tuple of three ints: color of the checkpoint pixels in the raw track image
    scoreboard_pixel: tuple of three ints: color of the scoreboard pixel in the raw track image
    w: int: width of the raw track image
    h: int: height of the raw track image
    w: int: width of the final track image adapted to the resolution
    h: int: height of the final track image adapted to the resolution
    track: numpy array containing the coordinates of the points of the track
    checkpoint: numpy array containing the coordinates of the checkpoints
    checkpoint_index: list of indexes of the track that correspond to checkpoints
    scoreboard: position of the upper left corner of the scoreboard in this track
    boxes: list of int: containing the index of the track
    image: image of the track ready to blit in the screen
    width: width of the track in pixels (please note that the width is resized with change in the screen resolution
    width_ratio: float: ratio between the smallest screen dimension and the width of the track
    point_dist: int: minimum separation of points defining the track in pixels
    miniature_w: with of the miniature image of the track in pixels
    miniature_h: height of the miniature image of the track in pixels
    name: name of the track, used to load and save miniatures and track objects
    miniature: image of a miniature of the track
    """

    def __init__(self, par=None, width_ratio=0.04):
        """initiallizes the instance
        par: dictionary containing parameters
        width_ratio: float: ratio between the width of the track and the smaller dimension of the screen"""
        if par is None:
            self.checkpoint_pixel = None
            self.track_pixel = None
            self.start_pixel = None
            self.scoreboard_pixel = None
            self.width_ratio = width_ratio
        else:
            self.checkpoint_pixel = par['checkpoint_pixel']
            self.track_pixel = par['track_pixel']
            self.start_pixel = par['start_pixel']
            self.scoreboard_pixel = par['scoreboard_pixel']
            self.width_ratio = par['track_width_ratio']
        self.scoreboard = None
        self.raw_w = None
        self.raw_h = None
        self.w = None
        self.h = None
        self.track = None
        self.checkpoint = None
        self.checkpoint_index = None
        self.boxes = None
        self.image = None
        self.width = None
        self.point_dist = 1
        self.name = None
        self.miniature = None

    def create_track(self, track_name):
        """this method creates the track object form a png raw track drawing
        track_name : name of the track
        returns : None"""
        self.name = track_name
        track_image = pygame.image.load(os.path.join('tracks', track_name + '.png'))
        x, y, self.raw_w, self.raw_h = track_image.get_rect()
        self.w = self.raw_w
        self.h = self.raw_h
        track = []
        checkpoint = []
        start = []
        for i in range(self.raw_w):
            for j in range(self.raw_h):
                this_pixel = track_image.get_at((i, j))
                if this_pixel == self.track_pixel:
                    track.append((i, j))
                elif this_pixel == self.checkpoint_pixel:
                    checkpoint.append((i, j))
                    track.append((i, j))
                elif this_pixel == self.start_pixel:
                    start.append((i, j))
                elif this_pixel == self.scoreboard_pixel:
                    self.scoreboard = np.array([i, j])
        # track and checkpoints are initialized with the start point which is then removed from the old track
        track = np.array(track)
        # consider reducing to float16 if performance is not good
        track = track.astype('float32')
        start = np.array(start)
        start = start.astype('float32')
        checkpoint = np.array(checkpoint)
        checkpoint = checkpoint.astype('float32')
        self.scoreboard = self.scoreboard.astype('float32')
        self.checkpoint = [np.array(start[0])]
        self.track = [np.array(start[0])]
        # now we find the closest point to the last point in new track and repeat the update
        # until there is no more points in old track
        exit_loop = False
        while not exit_loop:
            dists = ((self.track[-1].reshape(1, 2) - track) ** 2).sum(axis=1)
            if checkpoint.shape[0] > 0:
                cp_dists = ((self.track[-1].reshape(1, 2) - checkpoint) ** 2).sum(axis=1)
                if cp_dists.min() < 0.000000001:
                    cp_min_index = np.argmin(cp_dists)
                    self.checkpoint.append(np.copy(checkpoint[cp_min_index]))
                    checkpoint = np.delete(checkpoint, cp_min_index, axis=0)
            min_index = np.argmin(dists)
            self.track.append(np.copy(track[min_index]))
            track = np.delete(track, min_index, axis=0)
            if track.shape[0] == 0:
                exit_loop = True
        self.track = np.concatenate(self.track).reshape(-1, 2)
        self.checkpoint = np.concatenate(self.checkpoint).reshape(-1, 2)
        self.save_track()  # raw track is stored to disk before processing it

    def resize_track(self, res):
        """this method resizes the track to adapt to a different screen size based on the monitor resolution
        res: tuple of two ints cotaining the resolution of the screen
        returns :None"""
        ratio_w = res[0] / float(self.raw_w)
        ratio_h = res[1] / float(self.raw_h)
        self.width = min(res[0], res[1]) * self.width_ratio
        ratio = min(ratio_w, ratio_h)
        self.track *= ratio
        self.checkpoint *= ratio
        self.scoreboard *= ratio
        self.h = int(self.raw_h * ratio)
        self.w = int(self.raw_w * ratio)

    def reduce_track(self, npixels):
        """this method reduces the number of points in the track so each point is separated at leas the number of
        pixels indicated by npixels. This is done to reduce the computation during the execution of the game but if
        there is too much reduction (npixels is a big number) the resolution of the track picture will be poorer and
        the calculation of when the car is out of the track will give errors. Recommended 3 to 6 pixels.
        npixesls: int
        returns :None"""
        self.point_dist = npixels
        npixels2 = npixels ** 2
        track = self.track[0].reshape(1, 2)
        for i in range(1, self.track.shape[0]):
            if ((self.track[i] - track[-1]) ** 2).sum() > npixels2:
                track = np.append(track, self.track[i].reshape(1, 2), axis=0)
        self.track = np.copy(track)
        # now we calculate the checkpoint_indexes
        dists2 = self.track.reshape(1, self.track.shape[0], 2) - self.checkpoint.reshape(self.checkpoint.shape[0], 1, 2)
        dists2 = (dists2 ** 2).sum(axis=2)
        self.checkpoint_index = np.argmin(dists2, axis=1)

    def create_track_image(self):
        """this method uses the points in the track to build a track image
        track_image : pygame image
        track : dictionary of lists of tuples
        par : dictionary
        returns : track_image (pygame image)"""
        self.image = pygame.Surface((self.w, self.h))
        self.image.fill((255, 255, 255))
        for point in self.track:
            pygame.draw.circle(self.image, (255, 0, 0), point, int(self.width) + 2, 2)
        for point in self.track:
            pygame.draw.circle(self.image, (150, 150, 150), point, int(self.width))
        # finish line generation
        square = np.array([[0., 0.], [0., 1.], [1., 1.], [1., 0.]])
        f_line = []
        for i in range(6):
            for j in range(3):
                shift = np.array([[i, j]])
                f_line.append(square + shift)
        f_line = np.concatenate(f_line, axis=0)
        f_line *= self.width / 3.
        f_line -= f_line.mean(axis=0)
        v = self.track[4] - self.track[0]
        v /= np.linalg.norm(v)
        h = np.array([0., 1.])
        rot = np.array([[np.dot(h, v), -np.cross(h, v)], [np.cross(h, v), np.dot(h, v)]])
        f_line = self.track[0] + np.dot(f_line, rot.T)
        # finish line drawing
        f_line_color = (0, 0, 0)
        for i in range(f_line.shape[0] // 4):
            if f_line_color == (0, 0, 0):
                f_line_color = (255, 255, 255)
            else:
                f_line_color = (0, 0, 0)
            pygame.draw.polygon(self.image, f_line_color, f_line[4 * i: 4 * i + 4])

    def save_track_image(self):
        """this method shaves the full track image into disk"""
        pygame.image.save(self.image, os.path.join('tracks', self.name + '_full.png'))

    def create_track_miniature(self, res):
        """this method uses the points in the track to build a track image miniature and stores it to disk
        res: tuple of 2 ints (resolution of the miniature)"""
        self.resize_track(res)
        self.reduce_track(3)
        self.create_track_image()
        self.miniature = pygame.transform.smoothscale(self.image, res)  # just self.miniature = self.image ?
        pygame.image.save(self.miniature, os.path.join('tracks', self.name + '_miniature.png'))

    def load_track_miniature(self):
        """this loads a miniature of the track from disk"""
        self.miniature = pygame.image.load(os.path.join('tracks', self.name + '_miniature.png'))

    def erase_checkpoints(self):
        """this method erases the highlighted checkpoints by drawing the basic track color on top of it
        track_image : pygame image
        track : dictionary of lists of tuples
        par : dictionary
        returns : track_image (pygame image)"""
        for item in self.checkpoint:
            pygame.draw.circle(self.image, (150, 150, 150), item, self.width)

    def show_checkpoints(self):
        """"this method creates an image with all the checkpoints highlighted
        track_image : pygame image
        track : dictionary of lists of tuples
        par : dictionary
        returns : track_image (pygame image)"""
        for item in self.checkpoint:
            pygame.draw.circle(self.image, (255, 0, 0), item, self.width)
        pygame.draw.circle(self.image, (255, 0, 0), self.scoreboard, self.width)

    def save_track(self):
        """this method saves the track as a picled object containing the tuple of track and checkpoints"""
        object = (self.track, self.checkpoint, self.scoreboard, self.name, self.raw_w, self.raw_h)
        with open(os.path.join('tracks', self.name + '.pic'), 'w') as f:
            pic.dump(object, f)

    def load_track(self, name):
        """this method reads the track from disk and processes it
        name: str: name of the track
        res: tuple of two ints cotaining the resolution of the screen
        npixesls: int representing the separation between points in the track
        npixels:
        """
        with open(os.path.join('tracks', name + '.pic'), 'r') as f:
            object = pic.load(f)
        self.track, self.checkpoint, self.scoreboard, self.name, self.raw_w, self.raw_h = object

    def get_boxes(self, ncars):
        """calculates the boxes attribute for the track given a specific track width
        ncars: int: numner of cars in the race (boxes that have to be created"""
        min_dist = 2 + int(2 * self.width // self.point_dist)  # min_dist is the minimum number of points bwtween cars
        sequence = [min_dist * (i + 1) for i in range(ncars)]
        if self.track.shape[0] > max(sequence):
            self.boxes = [self.track.shape[0] - item for item in sequence]
        else:
            raise ValueError('range of point is the sequence of boxes cannot be higher than the number of points in the track')

    def get_vector(self, this_point, next_point):
        """returns a vector (numpy array) with the unit vector joining point this_point and next_point in the track
        this_point: int: index of a point in the track
        next_point: int: index of a point in the track"""
        assert this_point != next_point, 'this_point cannot be the same than next_point'
        vector = self.track[next_point] - self.track[this_point]
        return vector / np.linalg.norm(vector)



if __name__ == '__main__':
    print(version)
