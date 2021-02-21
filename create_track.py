# -*- coding: utf8 -*-
# create_track
# main create_track for toprace script
# Alfredo Martin 2021

from classes.track import Track
import argparse
import os
from classes.parameters import Parameters


def parse_args():
    parser = argparse.ArgumentParser(description="""The create_track script is used to create a 
    playable track from a track sketch drawing stored as a .png image. You can draw your track 
    using a program like paint or any other drawing software. Draw a closed loop line, as thin as 
    possible, in a canvas with a color with a rgb code as stated in the par.ini file (0, 0, 0). 
    It is better if the canvas size approximates the resolution of the 
    game (this is not an absolute requirement because you can resize later). Then paint one point 
    with a color with a rgb code equal to the parameter start_pixel in the par.ini file (255, 0, 0), 
    delete the point just before that (to indicate which is the end point of the track, and then color a number of 
    points in the track (select points in de turns) with a color with rgb code exactly as the one passed in the 
    parameter checkpoint_pixel in the par.ini file (255, 0, 255). Then draw a point with a color exactly as 
    passed in the scoreboard_pixel in the par.ini file (0, 255, 0)""")
    parser.add_argument('-na', '--name',
                        help="""Name of the track. The name will be used to fing the raw trakc drawing that 
                        must be located in the folder images and namer <--name>.png. 
                        Default: 'montmelo' """,
                        type=str,
                        default='montmelo')
    parser.add_argument('-mw', '--miniature_width',
                        help="""Width of the miniature image of the track (to be used in the selection menu). 
                        Default: 200 """,
                        type=int,
                        default=200)
    args = parser.parse_args()
    assert os.path.isfile(os.path.join('tracks', args.name + '.png')), os.path.join('tracks', args.name + '.png') + ' does not exist'
    return args


if __name__ == '__main__':
    args = parse_args()
    par = Parameters(os.path.join('resources', 'par.ini'))
    track = Track(par=par.par)
    track.create_track(args.name)
    track.create_track_miniature((240, 160))
