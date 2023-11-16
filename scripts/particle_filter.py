import socket
import struct
import time
import math
from threading import Thread
import _thread
from datetime import datetime
import copy
import numpy as np
import matplotlib.pyplot as plt
from numpy import dot
from numpy.linalg import norm

def transmit(data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT_TX))
            s.send(data.encode('utf-8'))
        except (ConnectionRefusedError, ConnectionResetError):
            print('Tx Connection was refused or reset.')
            _thread.interrupt_main()
        except TimeoutError:
            print('Tx socket timed out.')
            _thread.interrupt_main()
        except EOFError:
            print('\nKeyboardInterrupt triggered. Closing...')
            _thread.interrupt_main()

def receive():
    global responses
    global time_rx
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
            try:
                s2.connect((HOST, PORT_RX))
                response_raw = s2.recv(1024)
                if response_raw:
                    responses = bytes_to_list(response_raw)
                    time_rx = datetime.now().strftime("%H:%M:%S")
            except (ConnectionRefusedError, ConnectionResetError):
                print('Rx connection was refused or reset.')
                _thread.interrupt_main()
            except TimeoutError:
                print('Response not received from robot.')
                _thread.interrupt_main()

def bytes_to_list(msg):
    num_responses = int(len(msg)/8)
    data = struct.unpack("%sd" % str(num_responses), msg)
    return data


### Network Setup ###
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT_TX = 61200     # The port used by the *CLIENT* to receive
PORT_RX = 61201     # The port used by the *CLIENT* to send data

# Received responses
responses = [False]
time_rx = 'Never'

# Create tx and rx threads
Thread(target = receive, daemon = True).start()



# simulation parameters
NOISE_RANGE = 2.0  # [m] 1σ range noise parameter
NOISE_SPEED = 0.5  # [m/s] 1σ speed noise parameter

size_of_bloc = 7.62 # 12 inches is 30.48 cm

# What the map looks like
MAP =  [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1]]


PROB_MAP = copy.deepcopy(MAP)
PARTICLE_MAP = copy.deepcopy(MAP)
ROW_LEN = len(MAP[0])  # 10 buffer of two cols, number of columns
COL_LEN = len(MAP)     # 6  buffer of two rows, number of rows
CONSTANT = 7.62        # to map the list to 12 inch grids, 12 inch is read as 30.48 cm

# Create tx and rx threads
# Thread(target = receive, daemon = True).start()

show_animation = True

def map_extend(map):
    final = []
    temp = []
    for row in map:
        for element in row:
            if element == 0:
                temp.append(1)
            else:
                temp.append(0)
        final.append(temp)
        temp = []
    print(final)
    

def cosine_distance(a, b):
    """_summary_

    Args:
        a (_type_): _description_ vector a
        b (_type_): _description_ vector b

    Returns:
        _type_: value from 0 to 1 of similarity
        
    calculates cosine similarity
    """
    return np.dot(a, b)/(norm(a) * norm(b))


def manhattan_distance(a, b):
    return np.abs(a-b).sum()
       
     
class Rover:
    def __init__(self):
        self.readings = [None, None, None, None, None, None]    # initialize self.readings as list with None Values (no readigs yet)
        self.update_directions()       # populate readings list
        
        
    def run_sensor(self, name:str, index:int, directions:list):
        """_summary_
        takes in the sensor name string and the index that the dirction the sensor reads in. The direction index
        is insipired from the directions list. The funtion takes this information, reads from the sensor and 
        stores the value in the directions list.
        Args:
            name (str): _description_
            name of the sensor
            index (int): _description_
            the index of the direction this sensor reads in. The direction is inspired from the directions list. 
            val (int):
            value of sensor
        Returns:
            _type_: _description_
            returns updated directions list
        """
        transmit(name)
        time.sleep(0.05)
        try:
            directions[index] = round(responses[0])
        finally:
            pass
        self.readings = directions
    
    def update_directions(self):
        """
        Args:
            directions (list): _description_
        """
        self.run_sensor('u0', 0, self.readings)
        time.sleep(0.05)
        self.run_sensor('u1', 3, self.readings)
        time.sleep(0.05)
        self.run_sensor('u2', 1, self.readings)
        time.sleep(0.05)
        self.run_sensor('u3', 2, self.readings)
        time.sleep(0.05)
        self.run_sensor('u4', 4, self.readings)
        time.sleep(0.05)
        self.run_sensor('u5', 5, self.readings)
        time.sleep(0.05)
        
        
class HistMap:
    def __init__(self):
        self.map_openings = 24  # 24 blocks that the robot could exist in 
        self.probabilities = self.init_probabilities()  # set initial probablities
        self.particle_placements = {}
        self.particle_readings = {}
        self.particle_place_count = {}
        self.isinit = True
        self.MAP = np.array(MAP)
        self.PROB_MAP = np.array(PROB_MAP)
        self.COLS = len(self.MAP[0])
        self.ROWS = len(self.MAP)
        self.PARTICLE_MAP = np.zeros((self.ROWS, self.COLS)) 
        self.num_particles = 119
        self.kernel = [[0.2 , 0.25, 0.2 ],
                       [0.2 , 1   , 0.25],
                       [0.25, 0   , 0.25]]
        self.threshold = 0.80
    
    
    
    def add_rover(self, rover):
        """ add an instance of the rover into the code """
        self.rover = rover
        
        
        
    def normalize_probmap(self, particle=0):
        """ normalize the probability map """
        if not particle:
            probmax, probmin = self.PROB_MAP.max(), self.PROB_MAP.min()
            mask = (self.PROB_MAP != 0)
            np.putmask(self.PROB_MAP, mask, (self.PROB_MAP - probmin) / (probmax - probmin) + 0.05)
        else:
            probmax, probmin = self.PARTICLE_MAP.max(), self.PARTICLE_MAP.min()
            mask = (self.PARTICLE_MAP != 0)
            np.putmask(self.PARTICLE_MAP, mask, (self.PARTICLE_MAP - probmin) / (probmax - probmin) + 0.05)
            
        # self.PROB_MAP[self.PROB_MAP != 0] = (self.PROB_MAP - probmin) / (probmax - probmin)
    
    
    
    def init_probabilities(self):
        """ 
        At the end of this function the probability of the robot being in any square is uniform
        i.e. it is 1/24 chance the robot is in any of the squares initially
        """
        for row in PROB_MAP:
            for element in row:
                if element==1:
                    PROB_MAP[PROB_MAP.index(row)][row.index(element)] = round(element/self.map_openings, 8)

        return PROB_MAP
    
    
    
    def place_init_particles(self):
        """
        Places particles in the probable areas, if the probability is above a certain threshold i.e. 1/self.map_openings
        """
        count = 0
        for r in range(len(MAP)):
            for j in range(len(MAP[r])):
                
                # only go into this if the particles have not been placed yet
                if MAP[r][j] == 1:
                    count += 1
                    prob = self.probabilities[r][j] * self.map_openings
                    if math.floor(prob) >= 1:
                        for i in range(math.floor(prob)):
                            self.particle_placements[r, j] = self.PROB_MAP[r][j]
             
       
                            
    def place_rand_particles(self):
        """ 
        places particles randomly upto an N amount, this will help speed up the localization process
        """
        # self.particle_placements = {}
        print(f"sum(self.particle_place_count.values()): {sum(self.particle_place_count.values())}")
        print(f"len(self.particle_readings): {len(self.particle_readings)}")
        print(f"len(self.particle_placements): {len(self.particle_placements)}")
        while sum(self.particle_place_count.values()) <= self.num_particles:
            coor = [np.random.randint(0, self.ROWS), np.random.randint(0, self.COLS)]
            while self.MAP[coor[0]][coor[1]] == 0:
                coor = [np.random.randint(0, self.ROWS), np.random.randint(0, self.COLS)]
            
            print(f"self.particle_place_count: {self.particle_place_count}")
            print(f"len(self.particle_place_count): {len(self.particle_place_count)}")
            
            if (coor[0], coor[1]) not in self.particle_place_count:
                self.particle_place_count[coor[0], coor[1]] = 1
            else:
                self.particle_place_count[coor[0], coor[1]] += 1
            
            print(f"self.PROB_MAP[coor[0]][coor[1]]: {self.PROB_MAP[coor[0]][coor[1]]}")

            # self.particle_placements[coor[0], coor[1]] = self.PROB_MAP[coor[0]][coor[1]]
            
    
    
    def particle_thresholding(self):
        """ decides the threshold for each particle and removes them """
        temp_dict_placements = copy.deepcopy(self.particle_placements)
        temp_dict_readings = copy.deepcopy(self.particle_readings)        
        temp_particle_place_count = copy.deepcopy(self.particle_place_count)        
        for k, v in self.particle_placements.items():
            if v < self.threshold:
                temp_dict_placements.pop(k)
                temp_dict_readings.pop(k)
                if k in temp_particle_place_count:
                    temp_particle_place_count.pop(k)
                else:
                    pass

                
        self.particle_place_count = temp_particle_place_count
        self.particle_readings = temp_dict_readings
        self.particle_placements = temp_dict_placements
        
         
           
    def measure_particles(self):
        """
        for every particle, four readings will be taken and the readings will be compared to the actual robot readings
        """
        for i, particle in enumerate(self.particle_placements.items()):
            guess = [None, None, None, None, None, None]   # the guessed distances of each particle   N, E, S, W

            # check north
            placement = particle[0]
            if placement[0] == 0:  
                guess[0] = 0   # set north to be 0
            elif placement[0] == self.ROWS - 1:
                guess[2] = 0   # set south to 0
            elif placement[1] == 0:
                guess[3] = 0   # set west to 0
            elif placement[1] == self.COLS - 1:
                guess[1] = 0   # set east to zero
            
            # check north
            N, distN = placement[0], 0
            while N > 0:
                if self.MAP[int(N)][int(placement[1])] == 1:
                    distN += 1
                    N -= 1
                else:
                    break
            
            # check east
            E, distE = placement[1], 0
            while E < self.COLS - 1:
                if self.MAP[int(placement[0])][int(E)] == 1:
                    distE += 1
                    E += 1
                else:
                    break
            
            # check south
            S, distS = placement[0], 0
            while S < self.ROWS - 1:
                if self.MAP[int(S)][int(placement[1])] == 1:
                    distS += 1
                    S += 1
                else:
                    break
            
            # check north
            W, distW = placement[1], 0
            while W > 0:
                if self.MAP[int(placement[0])][int(W)] == 1:
                    distW += 1
                    W -= 1
                else:
                    break
            
            distNE = math.sqrt(distN**2 + distE**2)
            distNW = math.sqrt(distN**2 + distW**2)
            
            guess = [distN, distE, distS, distW, distNE, distNW]
            self.particle_readings[placement] = guess
            self.particle_placements[placement] = cosine_distance(np.array(guess), np.array(self.rover.readings))
            
            # cosine = cosine_distance(guess, self.rover.readings)
            
            # print(f"{i}: {placement} {guess} {cosine}") 
        # print(f'The rover readings are {np.array(self.rover.readings)/CONSTANT}')
        
        
        
    def update_prob_map(self):
        """ takes the virtual particle readings and probabilities and updates probabilities"""
        for k, v in self.particle_readings.items():
            similarity = cosine_distance(np.array(v), np.array(self.rover.readings))
            # try:
            #     similarity = cosine_distance(v.sort(), self.rover.readings.sort())
            # except:
            #     similarity = cosine_distance(v, self.rover.readings)
            
            self.PROB_MAP[k[0]][k[1]] = 2*(self.PROB_MAP[k[0]][k[1]]) + similarity * self.kernel[1][1]
            
            try: self.PROB_MAP[k[0]][k[1]] += self.PROB_MAP[k[0] - 1][k[1]] * self.kernel[0][1]
            except: pass
            
            try: self.PROB_MAP[k[0]][k[1]] += self.PROB_MAP[k[0] + 1][k[1]] * self.kernel[2][1]
            except: pass
            
            try: self.PROB_MAP[k[0]][k[1]] += self.PROB_MAP[k[0]][k[1] - 1] * self.kernel[1][0]
            except: pass
            
            try: self.PROB_MAP[k[0]][k[1]] += self.PROB_MAP[k[0]][k[1] + 1] * self.kernel[1][2]
            except: pass
            
            try: self.PROB_MAP[k[0]][k[1]] += self.PROB_MAP[k[0] - 1][k[1] - 1] * self.kernel[0][0]
            except: pass
            
            try: self.PROB_MAP[k[0]][k[1]] += self.PROB_MAP[k[0] - 1][k[1] + 2] * self.kernel[0][2]
            except: pass
            
            try: self.PROB_MAP[k[0]][k[1]] += self.PROB_MAP[k[0] + 1][k[1] - 1] * self.kernel[2][0]
            except: pass
            
            try: self.PROB_MAP[k[0]][k[1]] += self.PROB_MAP[k[0] + 1][k[1] + 2] * self.kernel[2][2]
            except: pass
          
            
        
    def update_particle_map(self):
        """ 
        set a threshold for how many particles they have there 
        """
        self.PARTICLE_MAP = np.zeros((self.ROWS, self.COLS))
        for k, v in self.particle_place_count.items():
            # print(f"this is how many particle readings there are in update particle map {len(self.particle_readings)}")
            # similarity = cosine_distance(np.array(v), np.array(self.rover.readings))
            self.PARTICLE_MAP[k[0]][k[1]] = v
            # if float(similarity) > self.threshold:
            #     self.PARTICLE_MAP[k[0]][k[1]] += 1    
            
            
    
    def plot_probs(self, use_particle_map=False):
        """ 
        plot MAP
        """
        plt.matshow(self.PARTICLE_MAP, cmap="RdYlGn")
        plt.colorbar()
        plt.title("Robot Maze")
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.savefig("picture.png")

        
                
if __name__ == '__main__':
    hist = HistMap()
    rover = Rover()
    hist.add_rover(rover)
    hist.place_init_particles()
    hist.measure_particles()
    # hist.normalize_probmap(False)
    threshold = 0.85
    use_particle_map = True

    while True:        
        start = time.time()
        rover.update_directions()
        hist.place_rand_particles()
        hist.update_particle_map()
        # hist.update_prob_map()
        # hist.normalize_probmap(use_particle_map)
        hist.measure_particles()
        hist.particle_thresholding()   
        hist.plot_probs()
        end = time.time()
        print(f"time step: {end-start}s")    
    
