''' 
This file is part of SimMeR, an educational mechatronics robotics simulator.
Initial development funded by the University of Toronto MIE Department.
Copyright (C) 2023  Ian G. Bennett

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import numpy as np

class Maze:
    '''This class represents the maze/environment'''
    def __init__(self):
        self.walls = 0
        self.floor = 0

    def import_walls(self, maze_filename):
        '''Imports the walls from a csv file and sets up lines representing them'''
        self.walls = np.loadtext(maze_filename, delimiter=',', dtype=str)
