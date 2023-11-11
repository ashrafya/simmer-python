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

size_of_bloc = 30.48 # 12 inches is 30.48 cm

# What the map looks like
MAP = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
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
ROW_LEN = len(MAP[0])  # 10 buffer of two cols, number of columns
COL_LEN = len(MAP)     # 6  buffer of two rows, number of rows
CONSTANT = 30.48       # to map the list to 12 inch grids, 12 inch is read as 30.48 cm

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
            
class Rover:
    def __init__(self):
        self.readings = [None, None, None, None]    # initialize self.readings as list with None Values (no readigs yet)
        self.update_directions(self.readings)       # populate readings list
        
        
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
        time.sleep(0.1)
        try:
            directions[index] = round(responses[0])
        finally:
            pass
        return directions
    
    def update_directions(self, directions:list):
        """
        Args:
            directions (list): _description_
        """
        directions = self.run_sensor('u0', 0, directions)
        time.sleep(0.1)
        directions = self.run_sensor('u1', 3, directions)
        time.sleep(0.1)
        directions = self.run_sensor('u2', 1, directions)
        time.sleep(0.1)
        directions = self.run_sensor('u3', 2, directions)
        time.sleep(0.1)
        
        self.readings = directions
        
        
class HistMap:
    def __init__(self):
        self.map_openings = 24  # 24 blocks that the robot could exist in 
        self.probabilities = self.init_probabilities()  # set initial probablities
        self.particle_placements = {}
        self.particle_readings = {}
        self.isinit = True
        self.MAP = MAP
        self.PROB_MAP = PROB_MAP
        self.COLS = len(self.MAP[0])
        self.ROWS = len(self.MAP)
    
    
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
        # sample the measurements for each particle
        # copmare measurements with the actual measurements
        # update probabilities
        # propagate particles
        # repeat
    
    
    def place_particles(self):
        """
        Places particles in the probable areas, if the probability is above a certain threshold i.e. 1/self.map_openings
        """
        count = 0
        for r in range(len(MAP)):
            for j in range(len(MAP[r])):
                
                # only go into this if the particles have not been placed yet
                if self.isinit == True:
                    if MAP[r][j] == 1:
                        count += 1
                        prob = self.probabilities[r][j] * self.map_openings
                        if math.floor(prob) >= 1:
                            for i in range(math.floor(prob)):
                                self.particle_placements[count] = [r, j]
                
                # go here if the initial particles have already been placed
                else:
                    pass
        self.isinit = False    # so we dont place the initial particles again

                
    def measure_particles(self):
        """
        for every particle, four readings will be taken and the readings will be compared to the actual robot readings
        """
        print(len(self.particle_placements))
        for i, particle in enumerate(self.particle_placements.items()):
            guess = [None, None, None, None]   # the guessed distances of each particle   N, E, S, W

            # check north
            placement = particle[1]
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
            
            guess = [distN, distE, distS, distW]
                
            print(f"{i}: {particle[1]} {guess}") 

        
            
            
                
    
    def plot_probs(self):
        """ 
        plot MAP
        """
        # print(self.PROB_MAP)
        # plt.imshow(np.random.random((50,50)))
        plt.matshow(self.PROB_MAP, cmap="RdYlGn")
        plt.colorbar()
        plt.savefig("picture.png")
        plt.show()
        

                
if __name__ == '__main__':
    hist = HistMap()
    rover = Rover()
    hist.place_particles()
    # hist.plot_probs()
    hist.measure_particles()
    
    
    
    
    # print(f'how many openings in the map: {hist.map_openings}')
    # print(f'Probabiliities of the map: {hist.probabilities}')
    # print(f'Length of the MAP, i.e. number of rows: {len(MAP)}')
    # print(f'Length of the MAP row, i.e. number of cols: {len(MAP[0])}')
    # print(f'this is the particle placements{hist.particle_placements}')
    
    
