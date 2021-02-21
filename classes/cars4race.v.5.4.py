version = 'cars4race.v.5.2'
# this version enables different masses for each car and implements rebound of the cars with the screen limits
# version 5.2 incorporates independent max speed for each car

print 'importing modules...'
import pygame
import sys
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (90, 30) # positions the screen in a specific position of the monitor
import time
import random as rnd
import math
import cPickle as pic
import copy

print 'initializing pygame...'
pygame.display.init()
pygame.mixer.init()
pygame.font.init()
pygame.joystick.init()


x_res, y_res = pygame.display.Info().current_w, pygame.display.Info().current_h
print x_res, y_res
x_res -= 90
y_res -= 30



def v_multiply(vector, scalar):
    return (vector[0] * scalar, vector[1] * scalar)

def v_divide(vector, scalar):
    return (vector[0] / scalar, vector[1] / scalar)

def v_invert(vector):
    return (- vector[0], - vector[1])

def v_add(vector1, vector2):
    return (vector1[0] + vector2[0], vector1[1] + vector2[1])

def v_substract(vector1, vector2):
    return (vector1[0] - vector2[0], vector1[1] - vector2[1])

def v_uvector(vector):
    if vector != (0, 0):
        module = (vector[0] * vector[0] + vector[1] * vector[1]) ** 0.5
        return (vector[0] / module, vector[1] / module)
    else:
        return (0.0, 0.0)

def v_module(vector):
    return (vector[0] * vector[0] + vector[1] * vector[1]) ** 0.5

def v_ctp(vector):
    if vector == (0.0, 0.0):
        return (0.0, 0.0)
    else:
        module = v_module(vector)
        angle = math.atan2(vector[1], vector[0])
        return (module, angle)

def v_ptc(vector):
    x = vector[0] * math.cos(vector[1])
    y = vector[0] * math.sin(vector[1])
    return (x, y)


       

class announcement:
    def __init__(self, text, time, color):
        self.t = 0
        self.color = color
        self.time = time
        self.active = True
        style = pygame.font.SysFont('comicsans', 70)
        self.text = style.render(text, False, self.color)
        x, y, w, h = self.text.get_rect()
        text_x = (screen_width / 2) - (w / 2)
        text_y = (screen_height / 2) - (h / 2)
        self.pos = (text_x, text_y)
        return None
    def update(self):
        self.t += 1
        self.active = self.t <= self.time
        screen.blit(self.text, self.pos)
        return None

class coche:
    def __init__(self, tipo, par, track):
        """inits the class
        a : float (initial angle of the car)
        tipo : int (type of car)
        par : dictionary
        track: dictionary of lists"""
        self.tipo = tipo # type of car (color)
        self.color = par['car_colors'][tipo] # color of the car
        self.driver = par['driver'][tipo]
        self.last_time = time.time() # this is the time to start counting a lap
        self.n_laps = - 1 # number of laps run
        self.this_lap = 0.0 # time taken to run this lap
        self.last_lap = 0.0 # time taken to run last lap
        self.best_lap = 10000.0 # time of best lap
        self.pos = track['boxes'][tipo] # initial position of the car
        self.a = track['aboxes'][tipo] # initial angle of the car
        self.v = (0, 0) # current velocity
        self.m = par['car_mass'][tipo] # mass of this car
        self.f = (0.0, 0.0)# combined force for the car
        self.command = (0.0, 0.0) # external force applied
        self.command_center = (0, 0) # position of the command dysplay for this car
        self.drag = 100.0 # current drag
        self.lateral_drag = par['lateral_drag']
        self.colors = [self.color, black, black, black, black, black, black, blue] # colors of the different parts of the car
        self.current_check = 0 # index of the last checkpoint checked ##
        self.next_check = 0 # index of the next point checked ##
        self.info = None # dictionary including info useful for getting the next command in auto cars

    def get_info_orientation(self, track):
        """updates the orientation parameter, +1 if forward, -1 if backward
        track : dictionary of lists of tuples
        returns None"""
        if self.info['icheck'] == 0: #next checkpoint is 0
            if len(track['track']) - self.info['itrack'][0] < self.info['itrack'][0]: #going forward is shorter
                self.info['orientation'] = 1
                oidistance = len(track['track']) - self.info['itrack'][0] # smalest distance in index value
            else: # going backward is shorter
                self.info['orientation'] = -1
                oidistance = self.info['itrack'][0]
        else: # next checkpoint is not 0
            if self.info['icheck'] >= self.info['itrack'][0]: # next checkpoint is ahead
                if self.info['icheck'] - self.info['itrack'][0] <= len(track['track']) + self.info['itrack'][0] - self.info['icheck']: #going forward is shorter
                    self.info['orientation'] = 1
                    oidistance = self.info['icheck'] - self.info['itrack'][0]
                else: # is shorter going backwards
                    self.info['orientation'] = -1
                    oidistance = len(track['track']) + self.info['itrack'][0] - self.info['icheck']
            else: # next checkpoint is behind
                if self.info['itrack'][0] - self.info['icheck'] < len(track['track']) + self.info['icheck'] - self.info['itrack'][0]: # it is shorter going backward
                    self.info['orientation'] = -1
                    oidistance = self.info['itrack'][0] - self.info['icheck']
                else : # it is shorter going forward
                    self.info['orientation'] = -1
                    oidistance = len(track['track']) + self.info['icheck'] - self.info['itrack'][0]
        if oidistance < 40:
            self.info['itrack'][1] = self.info['itrack'][0] + 20 * self.info['orientation']
        else:
            self.info['itrack'][1] = self.info['itrack'][0] + 40 * self.info['orientation']
        if self.info['itrack'][1] >= len(track['track']):
                self.info['itrack'][1] -= len(track['track'])
        if self.n_laps == -1:
            self.info['orientation'] = 1
        return None
                
    def get_closest_index(self, track):
        """ this function updates the index for the track point that is the closest to this car
        track: dictionary of lists of tuoles
        returns : None (list of three integers)"""
        indexes = [i if i < len(track['track']) else len(track['track']) -i for i in range(self.info['itrack'][0] - 40, self.info['itrack'][0] + 40)]
        distances = [v_module(v_substract(track['track'][i], self.pos)) for i in indexes]
        this_index = distances.index(min(distances))
        self.info['itrack'][0] = indexes[this_index]
        return None
    
    def calculate_loops(self, par, track, cars):
        """this function checks that the car has passed for all the checkpoints and then updates the
        number of loops, time spent in the current loop
        par : dictionary
        track : dictionary of lists of tuples"""
        # this part updates the checks of the loops
        this_announcement = None
        self.this_lap = time.time() - self.last_time
        check_distance = v_module(v_substract(track['checkpoint'][self.next_check], self.pos))
        if v_module(v_substract(track['checkpoint'][self.current_check], self.pos)) <= par['road_width']:
            pygame.draw.circle(track_image, self.color, track['checkpoint'][self.current_check], par['road_width']) # checkpoint is highlighted
        if check_distance <= par['road_width']: # we are within the next checkpoint distance
            if self.next_check == 0 and self.n_laps > -1: # the lap was completed
                self.current_check = 0
                self.next_check = 1 # 0 is never the next check because it is in the same place than the last one
                self.last_lap = self.this_lap
                self.last_time = time.time()
                self.n_laps += 1
                if self.last_lap < min([cars[i].best_lap for i in range(len(cars))]):
                    this_announcement = 'Best lap:  ' + str(round(self.best_lap, 2)) + ' sec'
                    self.best_lap = self.last_lap
                elif self.last_lap < self.best_lap: # the lap has not completed with record
                    self.best_lap = self.last_lap
                    this_announcement = 'Best personal lap:  ' + str(round(self.best_lap, 2)) + ' sec'
                
            elif self.next_check == 0 and self.n_laps == -1: # the race starts
                self.current_check = 0
                self.next_check = 1 # 0 is never the next check because it is in the same place than the last one
                self.last_lap = self.this_lap
                self.last_time = time.time()
                self.n_laps += 1
            else: #the lap has not completed
                self.current_check = self.next_check
                if self.next_check == len(track['checkpoint']) -1:
                    self.next_check = 0
                else:
                    self.next_check += 1
        return this_announcement
            
    def update_info(self, cars, track):
        """extracts the information of the car to be passed to the command generator
        cars : list of cars objects
        track : dictionary of lists of tuples
        reruns : None"""
        #pinfo = copy.deepcopy(self.info)
        #self.info = {}
        self.info['pos'] = self.pos #position of this car
        self.info['cpos'] = [cars[i].pos for i in range(len(cars)) if i != self.tipo] # position of all other cars
        self.get_closest_index(track) # gets the index of the closest point in the track and updates self.info['itrack'][0]
        self.info['icheck'] = track['icheckpoint'][self.next_check] # index of the next checkpoint in the track
        self.get_info_orientation(track)
        return None
            
    def init_info(self, cars, track):
        """this method extracks the info object for the car without any previous info object
        (start of the race)
        cars : list of cars objects 
        track : dictionary of lists of tuples
        reruns : None"""
        self.info = {}
        self.info['pos'] = self.pos #position of this car
        self.info['cpos'] = [cars[i].pos for i in range(len(cars)) if i != self.tipo] # position of all other cars
        distances = [v_module(v_substract(track['track'][i], self.pos)) for i in range(len(track['track']))] # list of distances to the track
        min_distance = min(distances)
        imin_distance = distances.index(min_distance)
        self.info['itrack'] = [imin_distance, imin_distance + 40]
        self.info['itrack'] = [self.info['itrack'][i] if self.info['itrack'][i] < len(track['track']) else self.info['itrack'][i] - len(track['track']) for i in range(len(self.info['itrack']))]
        # itrack holds the indexes for track positions closest and and target
        self.info['icheck'] = track['icheckpoint'][self.next_check] # index of the next checkpoint in the track
        self.get_info_orientation(track) # calculates self.info['orientation'] and self.info['oidistance']
        return None

    def calculate_force(self, command, positions, track, par):
        """ this calculates the force that is the sum of all forces affecting the car, and also its new angle
        command : tuple of float (external force)
        positions : list of tuples of floats (positions of all the  except the current one)
        track : dictionary of lists of tuples
        par : dictionary"""
        self.command = command
        if self.command != (0.0, 0.0):
            # this part sets the value of the angle of the car
            if command != (0.0, 0.0): # if there is not a command the angle does not change
                self.a = v_ctp(command)[1] # returns the angle of cartessian to polar transformation
        # this part calculates the normal drag force
        if self.v != (0.0, 0.0):
            theta = math.atan2(self.v[1], self.v[0]) # this is the angle of the velocity
            v_direction = (math.cos(self.a), math.sin(self.a)) # thus us an unitary vector in the direction of the car
            vd = v_multiply(v_direction, v_module(self.v) * math.cos(theta - self.a)) # this is the vector velocity in the direction of the car
            vn = v_substract(self.v, vd) # this is the vector velocity normal to the car
            Fn = v_multiply(vn, -self.lateral_drag) # this is the lateral drag force
        else:
            Fn = (0.0, 0.0)
            vd = (0.0, 0,0)
            vn = (0.0, 0.0)
        # this part calculates the value of the drag constant based on the distance of the car to the track
        distances = [v_module(v_substract(track['track'][i], self.pos)) for i in range(len(track['track']))] # list of distances to the track
        min_distance = min(distances) 
        if min_distance < par['road_width']:
            self.drag = par['onroad_drag']
        else:
            self.drag = par['offroad_drag']
        # this part calculates the drag force based on the velocity
        Fd = v_multiply(vd, -self.drag)
        # this part calculates the colision forces
        Fc = (0.0, 0.0)
        for position in positions: # Here we could use the mass of the other car to calculate the colision force. not added at this point
            colision_vector = v_substract(self.pos, position)
            current_distance = v_module(colision_vector)
            if current_distance < par['colision_distance']:
                colision_vector = v_multiply(v_uvector(colision_vector), max(1, par['colision_distance'] - current_distance))
                Fc = v_add(Fc, v_multiply(colision_vector, par['colision_constant'])) # we could multiply this for the mass of the other car
        # this part sums all the forces
        fuerza = self.command
        fuerza = v_add(fuerza, Fn)
        fuerza = v_add(fuerza, Fd)
        fuerza = v_add(fuerza, Fc)
        self.f = fuerza

    def calculate_new_pos(self):
        aceleracion = v_divide(self.f, self.m)
        self.v = v_add(self.v, aceleracion)
        self.pos = v_add(self.pos, self.v)
        # now we rebound the car if it has gone out of the limits of the screen
        if (self.pos[0] < 0 and self.v[0] <0) or (self.pos[0] > screen_width and self.v[0] > 0):
            self.v = (-self.v[0], self.v[1])
        if (self.pos[1] < 0 and self.v[1] <0) or (self.pos[1] > screen_height and self.v[1] > 0):
            self.v = (self.v[0], -self.v[1])
        self.this_car = [[(p_master_car[i][j][0], p_master_car[i][j][1] + self.a) for j in range(len(p_master_car[i]))] for i in range(len(p_master_car))]
        self.this_car = [[v_ptc(self.this_car[i][j]) for j in range(len(self.this_car[i]))] for i in range(len(self.this_car))]
        self.this_car = [[v_add(self.this_car[i][j], self.pos) for j in range(len(self.this_car[i]))] for i in range(len(self.this_car))]
    def draw_car(self):
        for i in range(len(self.this_car)):
            pygame.draw.polygon(screen, self.colors[i], self.this_car[i])





#**********************************************************************************
def countdown(cars, text, maxtime, writenumber = True):
    """ creates a countdown
    cars : list of car objects
    text : str (text to dysplay before the number
    maxtime : int (number of seconds for the countdown)
    writenumber : bool (whether or not to write the number after the text
    returns : None"""
    global announcements
    start_time = time.time()
    end_time = start_time + maxtime
    counted = [False for i in range(maxtime)]
    while time.time() < end_time:
        #event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                game_exit = True
                break
        for count in range(maxtime):
            if time.time() > start_time + count and not counted[count]:
                counted[count] = True
                if writenumber:
                    announcements.append(announcement(text + str(maxtime - count), 15, blue))
                else:
                    announcements.append(announcement(text, 15, blue))
        screen.blit(track_image, (0,0))
        update_score_table(cars, track['score'][0], par)
        for this_announcement in announcements:
            this_announcement.update()
        for car in cars:
            car.draw_car()
        pygame.display.update()
        clock.tick(par['FPS'])
        announcements = [this_announcement for this_announcement in announcements if this_announcement.active]
    return None

def intro(texts, sizes, color, maxtime, clearscreen = True):
    """ creates an announcement with blank screen
    sizes : list of int (sizes for the different texts
    texts : list of str (text to dysplay before the number
    color : tuple of trhee integer
    maxtime : int (number of seconds that announcement lasts)
    clearscreen : bool (whether to clear the screen before writing the messages or not)
    returns : None"""
    start_time = time.time()
    end_time = start_time + maxtime
    text = []
    text_x = []
    text_y = []
    for i in range(len(texts)):
        style_2 = pygame.font.SysFont('comicsans', sizes[i])
        text.append(style_2.render(texts[i], False, color))

    for i in range(len(text)):
        x, y, w, h = text[i].get_rect()
        text_x.append((screen_width / 2) - (w / 2))
        text_y.append(((screen_height) / 2) + 60 * (i - len(text) / 2)   - (h / 2))
    while time.time() < end_time:
        #event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                game_exit = True
                break
        if clearscreen:
            screen.fill(white)
        for i in range(len(text)):
            screen.blit(text[i], (text_x[i], text_y[i]))    
        pygame.display.update()
        clock.tick(par['FPS'])
    return None

def select_track(par):
    """ menu to select track
    sizes : list of int (sizes for the different texts
    texts : list of str (text to dysplay before the number
    color : tuple of trhee integer
    maxtime : int (number of seconds that announcement lasts)
    clearscreen : bool (whether to clear the screen before writing the messages or not)
    returns : track_name"""

    screen.fill(white)
    for i, track_name in enumerate(par['track_names']):
        style = pygame.font.SysFont('comicsans', 50)
        text = style.render(str(i) + ' ' + track_name, False, (0, 0, 255))
        if i < 5:
            screen.blit(text, (100, 100 + 100 * i))
        else:
            screen.blit(text, (400, 100 + 100 * (i - 5)))
    keep = True
    selection = -1
    while keep:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    selection = 0
                elif event.key == pygame.K_1:
                    selection = 1
                elif event.key == pygame.K_2:
                    selection = 2
                elif event.key == pygame.K_3:
                    selection = 3
                elif event.key == pygame.K_4:
                    selection = 4
                elif event.key == pygame.K_5:
                    selection = 5
                elif event.key == pygame.K_6:
                    selection = 6
                elif event.key == pygame.K_7:
                    selection = 7
                elif event.key == pygame.K_8:
                    selection = 8
                elif event.key == pygame.K_9:
                    selection = 9
        if -1 < selection < len(par['track_names']):
            keep = False
        pygame.display.update()
        clock.tick(par['FPS'])
    return par['track_names'][int(selection)]


def minutes(this_time, r_decimas):
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
        
def update_score_table(cars, pos, par):
    """this function updates the score_table
    cars : list of car objects
    pos : tuple of int (position of the score table)
    par : dictionary
    returns : whether or not race has ended"""
    result = False
    header_pos = v_add(pos, (5, 5))
    header1_pos = v_add(pos, (5, 25))
    header2_pos = v_add(pos, (45, 25))
    header3_pos = v_add(pos, (90, 25))
    header4_pos = v_add(pos, (135, 25))
    header5_pos = v_add(pos, (215, 25))
                        
    style = pygame.font.SysFont('comicsans', 25)
    car_label = []
    n_lap = []
    position = []
    this_lap = []
    best_lap = []
    if par['race_type'] == 'race':
        cars.sort(key = lambda item: item.info['itrack'][0], reverse = True)
        cars.sort(key = lambda item: item.n_laps, reverse = True)
        header = style.render('remaining laps ' + str(par['race'] - max([cars[i].n_laps for i in range(len(cars))])), False, white)
        if par['race'] - max([cars[i].n_laps for i in range(len(cars))]) <= 0:
            result = True
    else:
        cars.sort(key = lambda item: item.best_lap)
        qunow = time.time()
        header = style.render('remaining qualification time ' + minutes(par['qualification'] * 60 + par['quini'] - qunow, False), False, white)
        if par['qualification'] * 60 + par['quini'] - qunow < 0:
            result = True
    for i, car in enumerate(cars):
        position.append(style.render(str(i + 1), False, car.color))
        car_label.append(style.render(car.driver, False, car.color))
        n_lap.append(style.render(str(car.n_laps), False, car.color))
        this_lap.append(style.render(minutes(car.this_lap, True), False, car.color))
        if car.best_lap < 10000:
            best_lap.append(style.render(minutes(car.best_lap, True), False, car.color))
        else:
            best_lap.append(style.render('', False, car.color))
    header1 = style.render('pos', False, white)
    header2 = style.render('car', False, white)
    header3 = style.render('lap', False, white)
    header4 = style.render('this lap', False, white)
    header5 = style.render('best lap', False, white)
    pygame.draw.rect(screen, (10, 10, 10), (pos[0], pos[1], 300, 30 + 20 * par['n_cars']))
    screen.blit(header, header_pos)    
    screen.blit(header1, header1_pos)
    screen.blit(header2, header2_pos)
    screen.blit(header3, header3_pos)
    screen.blit(header4, header4_pos)
    screen.blit(header5, header5_pos)
    for i in range(len(cars)):
        screen.blit(position[i], v_add(header1_pos, (0, 20 + 15 * i)))
        screen.blit(car_label[i], v_add(header2_pos, (0, 20 + 15 * i)))
        screen.blit(n_lap[i], v_add(header3_pos, (0, 20 + 15 * i)))
        screen.blit(this_lap[i], v_add(header4_pos, (0, 20 + 15 * i)))
        screen.blit(best_lap[i], v_add(header5_pos, (0, 20 + 15 * i)))
    return result

        

def read_std_par(path):
    """this funcion reads the a starndard par file and returns a par table
    path : str (complete path and filename for the par file)
    returns : par (dictionary)"""
    print 'reading stadard parameters...'
    f = open(path, 'r')
    lineas = f.readlines()
    lineas = [linea.rstrip('\r\n').split('\t') for linea in lineas]
    par = {}
    for i in range(1, len(lineas)):
        if lineas[i][2] == '':
            if lineas[i][3] == 'float':
                par[lineas[i][0]] = float(lineas[i][1])
            elif lineas[i][3] == 'int':
                par[lineas[i][0]] = int(lineas[i][1])
            elif lineas[i][3] == 'bool':
                par[lineas[i][0]] = lineas[i][1].upper() == 'TRUE' or lineas[i][1].upper() == 'YES' or lineas[i][1].upper() == 'Y'
            else:
                if lineas[i][1].upper() == 'NULL' or lineas[i][1].upper() == 'NONE' or lineas[i][1].upper() == '':
                    par[lineas[i][0]] = None
                else:
                    par[lineas[i][0]] = lineas[i][1]
        else:
            lineas[i][1] = lineas[i][1].split(lineas[i][2])
            if lineas[i][3] == 'float':
                par[lineas[i][0]] = [float(item) for item in lineas[i][1]]
            elif lineas[i][3] == 'int':
                par[lineas[i][0]] = [int(item) for item in lineas[i][1]]
            elif lineas[i][3] == 'bool':
                par[lineas[i][0]] = [item.upper() == 'TRUE' or item.upper() == 'YES' or item.upper() == 'Y' for item in lineas[i][1]]
            else:
                par[lineas[i][0]] = [None if item.upper() == 'NULL' or item.upper() == 'NONE' or item.upper() == '' else item for item in lineas[i][1]]
            par[lineas[i][0]] = tuple(par[lineas[i][0]])    
    return par

def get_track(par, track_name):
    """this funcion returns the track object form a png raw track drawing
    par : dictionary
    track_name : name of the track
    returns : tuple of track (dictionary of lists) and track_image (pygame image)"""
    print 'creating track...'
    track_image = pygame.image.load(os.path.join(par['sprites_path'], track_name + '.png'))
    x, y, w, h = track_image.get_rect()
    track = {'checkpoint' : [], 'track' : [], 'start' : [], 'end' : [], 'boxes' : [None for i in range(par['n_cars'])], 'aboxes' : [None for i in range(par['n_cars'])], 'score' : [], 'h' : h, 'w' : w}
    for i in range(w):
        for j in range(h):
            this_pixel = track_image.get_at((i, j))
            if this_pixel == par['background_pixel']:
                pass
            elif this_pixel == par['track_pixel']:
                track['track'].append((i, j))
            elif this_pixel == par['checkpoint_pixel']:
                track['checkpoint'].append((i, j))
                track['track'].append((i, j))
            elif this_pixel == par['start_pixel']:
                track['start'].append((i, j))
                track['track'].append((i, j))
            elif this_pixel == par['end_pixel']:
                track['end'].append((i, j))
                # end is not appended to track to allow the track to be ordered correctly               
            elif this_pixel == par['score_pixel']:
                track['score'].append((i, j))
    return track, track_image, w, h

def rearrange_track(track, par):
    """this funcion rearranges the track objects in such a way that the points in the track and checkpoints are ordered
    returns : track"""
    print 'sorting track points...'
    # new_track and new_checkpoints are initiallized with the start point which is then removed from the old track
    new_checkpoint = [track['start'][0]]
    new_track = [track['start'][0]]
    track['track'].remove(track['start'][0])
    # now we find the closest point to the last point in new track and repeat the update
    # until there is no more points in old track
    exit_loop = False
    while not exit_loop:
        min_list = [v_module(v_substract(new_track[-1], item)) for item in track['track']]
        closest_index = min_list.index(min(min_list))
        new_track.append(track['track'][closest_index])
        if new_track[-1] in track['checkpoint']:
            new_checkpoint.append(new_track[-1])
        track['track'].remove(new_track[-1])
        if len(track['track']) == 0:
            exit_loop = True
    # now the end point is added to the track
    new_track.append(track['end'][0])
    # We dont add the end point as a checkpoint
    # Now the track object is updated with the sorted points
    track['track'] = copy.deepcopy(new_track)
    track['checkpoint'] = copy.deepcopy(new_checkpoint)
    # Finally the boxes (starting positions for the cars in the track) are calculated for the track
    # also the angles corresponting to each box are calculated
    for i in range(par['n_cars']):
        track['boxes'][i] = track['track'][len(track['track'])  - par['ini_distance'] * (i + 2)]
        track['aboxes'][i] = v_ctp(v_substract(track['track'][len(track['track']) + 10 - par['ini_distance'] * (i + 2)], track['boxes'][i]))[1]
    return track

def reduce_track(track, par, ratio):
    """ this function reduces the number of track points by a factor set in the par object
    and then updates the track object with the indexes of the checkpoints
    track : dictionary of lists of tuples
    par : dictionary
    returns : track"""
    print 'reducing track points...'
    #reduction = int(par['track_reduction'] / ratio)
    # the points in the track that dont qualify are eliminated except if they are in a checkpoint or in the boxes
    #track['track'] = [track['track'][i] for i in range(len(track['track'])) if i % reduction == 0 or track['track'][i] in track['checkpoint'] or track['track'][i] in track['boxes']]
    track['icheckpoint'] = [i for i in range(len(track['track'])) if track['track'][i] in track['checkpoint']]
    return track

def resize_track(track, x_res, y_res):
    """this function resizes the track to adapt to a different screen size basedon the monitor resolotion
    track :dictionary of lists of tuples
    returns : track, ratio (float)"""
    print track['w'], track['h']
    ratio_w = x_res / float(track['w'])
    ratio_h = y_res / float(track['h'])
    ratio = min(ratio_w, ratio_h)
    for i in range(len(track['track'])):
        track['track'][i] = (int(track['track'][i][0] * ratio), int(track['track'][i][1] * ratio))
    for i in range(len(track['checkpoint'])):
        track['checkpoint'][i] = (int(track['checkpoint'][i][0] * ratio), int(track['checkpoint'][i][1] * ratio))
    for i in range(len(track['start'])):
        track['start'][i] = (int(track['start'][i][0] * ratio), int(track['start'][i][1] * ratio))    
    for i in range(len(track['end'])):
        track['end'][i] = (int(track['end'][i][0] * ratio), int(track['end'][i][1] * ratio))         
    for i in range(len(track['boxes'])):
        track['boxes'][i] = (int(track['boxes'][i][0] * ratio), int(track['boxes'][i][1] * ratio))
    for i in range(len(track['score'])):
        track['score'][i] = (int(track['score'][i][0] * ratio), int(track['score'][i][1] * ratio))        
    track['h'] = int(track['h'] * ratio)
    track['w'] = int(track['w'] * ratio)
    return track, ratio
    
def get_track_image(track_image, track, par):
    """this funcion uses the points ad the original track image to build a new basic image of the track
    track_image : pygame image
    track : dictionary of lists of tuples
    par : dictionary
    returns : track_image (pygame image)"""
    print 'getting track image'
    for item in track['track']:
        pygame.draw.circle(track_image, (255, 0, 0), item, par['road_width'] + 2, 2)
    for item in track['track']:    
        pygame.draw.circle(track_image, (150, 150, 150), item, par['road_width'])
    return track_image

def erase_checkpoints(track_image, track, par):
    """this funcion uses the points ad the original track image to erase the highlighted checkpoints and boxes
    track_image : pygame image
    track : dictionary of lists of tuples
    par : dictionary
    returns : track_image (pygame image)"""    
    for item in track['checkpoint']:
        pygame.draw.circle(track_image, (135, 135, 135), item, par['road_width'])
    return track_image

def get_commands(par, cars, track, announcements):
    """this function returns a list of tuples with the commands for all the cars
    par : dictionary
    cars : list of car objects
    track : dictionary of lists of tuples
    announcements : list of announcement objects
    returns : tuple of cars (list of car objects), announcements (list of announcement objects)"""
    # pygame.event.get()
    for i, car in enumerate(cars):
        if par['controls'][car.tipo] == 'joy':
            cmd = v_multiply(v_uvector((joystics[car.tipo].get_axis(4), joystics[car.tipo].get_axis(3))), par['max_speed'][car.tipo])
        elif par['controls'][car.tipo] == 'auto': # change this when this is implemented
            cmd =  v_multiply(v_uvector(v_substract(track['track'][car.info['itrack'][1]], car.pos)), par['max_speed'][car.tipo]) # move the car towards the target
        elif par['controls'][car.tipo] == 'smart': # change this when this is implemented
            cmd = v_multiply(v_uvector(v_substract(track['track'][car.info['itrack'][1]], car.pos)), par['max_speed'][car.tipo]) # move the car towards the target
        car.calculate_force(cmd, [cars[j].pos for j in range(len(cars)) if j != i], track, par)
        car.calculate_new_pos()
        car.update_info(cars, track)
        new_announcement = car.calculate_loops(par, track, cars)
        if new_announcement is not None:
            announcements.append(announcement(new_announcement, 30, car.color))
    return cars, announcements

def read_sounds(par):
    """this funcion reads the sounds and creates the sounds objects
    par: dictionary
    returns : tuple of music_sound and background_sound (sound objects)"""
    print 'initallizing music'
    path = 'C:\\Users\\JoseAlfredo\\Desktop\\COCHES\\'
    music_sound = pygame.mixer.Sound(os.path.join(par['sounds_path'],par['music']))
    music_sound.set_volume(par['music_volume'])
    background_sound = pygame.mixer.Sound(os.path.join(par['sounds_path'],par['background']))
    background_sound.set_volume(par['background_volume'])
    return (music_sound, background_sound)

def get_track_objects(par, track_name):
    try:
        f = open (os.path.join(par['data_path'], track_name + '.pic'), 'rb')
    except:
        print 'Creating track'
        track, track_image, screen_width, screen_height = get_track(par, track_name)
        track = rearrange_track(track, par)
        f = open(os.path.join(par['data_path'], track_name), 'wb')
        pic.dump(track, f)
        f.close()
    else:
        print 'Reading track'
        track = pic.load(f)
        f.close()
    track, ratio = resize_track(track, x_res, y_res)
    track = reduce_track(track, par, ratio)
    screen_width = track['w']
    screen_height = track['h']
    track_image = pygame.Surface((screen_width, screen_height))
    track_image.fill((255,255,255))
    track_image = get_track_image(track_image, track, par)
    track_image = erase_checkpoints(track_image, track, par)
    return track, track_image, screen_width, screen_height

#***************************************************************************************************
#                                         definitions
#***************************************************************************************************

# colors definitions
red = (255, 0, 0)
light_red = (200, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)
yellow = (255, 255, 0)
cyan = (0, 255, 255)
blue = (0, 0, 255)
grey = (200, 200, 200)
green = (0, 255, 0)

#initiallize the master car definition
chasis = [(-21, -3), (-18, -6), (-15, -3), (-9, -3),
          (-6, -6), (0, -6), (3, -3), (9, -3), (12, -6),
          (15, -6), (15, 6), (12, 6), (9, 3), (3, 3),
          (0, 6), (-6, 6), (-9, 3), (-15, 3), (-18, 6), (-21, 3)]         
rueda1 = [(-15, 3), (-15, 9), (-9, 9), (-9, 3)]
rueda2 = [(-15, -3), (-15, -9), (-9, -9), (-9, -3)]
rueda3 = [(3, 5), (3, 8), (9, 8), (9, 5)]
rueda4 = [(3, -5), (3, -8), (9, -8), (9, -5)]
eje1 = [(5, 3), (5, 5), (7, 5), (7, 3)]
eje2 = [(5, -3), (5, -5), (7, -5), (7, -3)]
ventana = [(-3, 3), (0, 3), (3, 0), (0, -3), (-3, -3)]
master_car = [chasis, rueda1, rueda2, rueda3, rueda4, eje1, eje2, ventana]
p_master_car = [[v_ctp(master_car[i][j]) for j in range(len(master_car[i]))] for i in range(len(master_car))]

#setup clock
clock = pygame.time.Clock()

#reading joysticks
print 'reading joysticks...'
joystics = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
for joystic in joystics:
    joystic.init()
print 'found ' + str(len(joystics)) + ' joysticks'    
# read parameters and adjust box pixels and commands with number of joystics
par = read_std_par('par.txt')
par['controls'] = list(par['controls'])
par['car_colors'] = list(par['car_colors'])
par['n_cars'] = len(par['driver'])
for i, this_color in enumerate(par['car_colors']):
    this_color = this_color.split(',')
    this_color = tuple([int(item) for item in this_color])
    par['car_colors'][i] = this_color
par['quini'] = time.time()
for i in range(par['n_cars']):
    if i < len(joystics):
        par['controls'][i] = 'joy'
    else:
        if par['controls'][i] == 'joy':
            par['controls'][i] = 'auto'



music_sound, background_sound = read_sounds(par)
screen_width = 1250
screen_height = 730
screen = pygame.display.set_mode((screen_width, screen_height))
# dysplay introintro
intro(['wellcome to cars4race',
       'Jose Alfredo Martin, 2018',
       'Music by ' + par['music_source'],
       'Used under ' + par['music_license'],
       'Background sound by ' + par['background_source'],
       'Used under ' + par['background_license']],
        [90, 70, 40, 40, 40, 40],
        blue,
        2)

track_name = select_track(par)
track, track_image, screen_width, screen_height = get_track_objects(par, track_name)
screen = pygame.display.set_mode((screen_width, screen_height))
print 'track n_points: ' + str(len(track['track']))

#Start preparing for countdown
screen.blit(track_image, (0,0)) # delete this after testing
#initiallize elements parameters
announcements = []

    
print 'initallizing cars command dysplay'
cars = [coche(i, par, track) for i in range(par['n_cars'])] # initiallizes the car list
for i, car in enumerate(cars): # initiallizes the position of the car command display
    car.command_center = v_add(track['score'][0], (295 + 30 + 60 * i, 55))
print 'initallizing cars info'
for car in cars:
    car.init_info(cars, track)
# draw the cars (delete this after testing)
cars, announcements = get_commands(par, cars, track, announcements)
# draw cars (delete this after testing?)
for car in cars:
    car.draw_car()
    
# start the music
music_sound.play(loops = -1)
background_sound.play(loops = -1)

#writes the score table
resultado = update_score_table(cars, track['score'][0], par)

# display screen
pygame.display.update()

countdown(cars, 'ready for the ' + par['race_type'] + ': ', 4)
countdown(cars, 'GO!', 1, False)

#******************************************************** game loop ********************************************
game_exit = False
while not game_exit:
    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
            game_exit = True   

    
    # erase outdated announcements
    announcements = [this_announcement for this_announcement in announcements if this_announcement.active]

    # update cars. This also blits checkpoints into the track
    cars, announcements = get_commands(par, cars, track, announcements)
    # draw the circuit    
    screen.blit(track_image, (0,0))
    # draw score. This blits the score in the screen and if race has ended display a message and starts next step
    if par['race_type'] == 'qualification' and update_score_table(cars, track['score'][0], par):
        par['race_type'] = 'race'
        for car in cars:
            car.draw_car()
        announcements = [] # this erases all the announcements
        intro(['Pool position for car', cars[0].driver], [70, 70], cars[0].color, 5, False)
        for i in range(len(cars)):
            cars[i].pos = track['boxes'][i]
            cars[i].a = track['aboxes'][i]
            cars[i].current_check = 0 # index of the last checkpoint checked ##
            cars[i].next_check = 0
            cars[i].n_laps = -1
            cars[i].v = (0.0, 0.0)
            cars[i].f = (0.0, 0.0)
        for car in cars:
            car.init_info(cars, track)
            car.calculate_new_pos()
            car.draw_car() # bit the car
        countdown(cars, 'ready for the ' + par['race_type'] + ': ', 5)
        countdown(cars, 'GO!', 1, False)
    elif par['race_type'] == 'race' and update_score_table(cars, track['score'][0], par):
        for car in cars: # blit the car
            car.draw_car()
        pygame.display.update()
        intro(['The race is over', 'The winner is', cars[0].driver], [70, 70, 70], cars[0].color, 10, False)
        announcements = []
        pygame.quit()
        quit()
        game_exit = True
    # draw announcements
    for this_announcement in announcements:
        this_announcement.update()
    # draw cars
    for car in cars:
        car.draw_car()
    pygame.display.update()
    # erase highlighted checkpoints
    track_image = erase_checkpoints(track_image, track, par)
    # erase outdated announcements
    announcements = [this_announcement for this_announcement in announcements if this_announcement.active]
    clock.tick(par['FPS'])

pygame.quit()
quit()







        
                                     




        
