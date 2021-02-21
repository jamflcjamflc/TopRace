# -*- coding: utf8 -*-
# parameters
# helper class for toprace
# Alfredo Martin 2021

version = 'parameters.v.1.0.0'


class Parameters:
    """reader of parameters.ini files.
    instance attributes:
    par: dictionary"""

    def __init__(self, path):
        """this method reads the a standard par file and creates a par dictionary
        path : str: path to the parameters file
        returns : None"""
        self.par = dict()
        self.types = {'FLOAT': float,
                      'INT': int,
                      'BOOL': self.process_bool,
                      'STR': self.process_str}
        print('reading stadard parameters...')
        with open(path, 'r') as f:
            lines = f.readlines()
        lines = [line.rstrip('\r\n').split('\t') for line in lines]
        for i, line in enumerate(lines[1:]):
            if line[0][0] != '#':
                if line[2] == '':
                    if ',' not in line[1]:
                        self.par[line[0]] = self.types[line[3].upper()](line[1])
                        if line[3].upper() == 'FLOAT':
                            self.par[line[0]] = float(line[1])
                    else:
                        self.par[line[0]] = tuple([self.types[line[3].upper()](item) for item in line[1].split(',')])

                else:
                    #todo modify this part is a similar way tan the part above
                    line[1] = line[1].split(line[2])
                    if ',' in line[1][0]:
                        self.par[line[0]] = tuple([tuple([self.types[line[3].upper()](subitem) for subitem in item.split(',')]) for item in line[1]])
                    else:
                        self.par[line[0]] = tuple([self.types[line[3].upper()](item) for item in line[1]])

    def process_bool(self, item):
        return item.upper()[0] == 'Y' or item.upper()[0] == 'T'

    def process_str(self, item):
        if item.upper() == 'NONE' or item.upper() == 'NULL':
            return None
        return str(item)

if __name__ == '__main__':
    print(version)
