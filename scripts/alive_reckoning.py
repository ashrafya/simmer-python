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

# Basic echo client, for testing purposes
# Code modified from examples on https://realpython.com/python-sockets/
# and https://www.geeksforgeeks.org/python-display-text-to-pygame-window/

import socket
import struct
import time
import math
from threading import Thread
import _thread
from datetime import datetime

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

# Run the sequence of commands
RUNNING = True
cmd_sequence = ['w0-36', 'r0-90', 'w0-36', 'r0-90', 'w0-12', 'r0--90', 'w0-24', 'r0--90', 'w0-6', 'r0-720']

ct = 0


"""
Rover description
    __u5_______u0________u4__
    |                       |
    |                       |
    |                       |
    |                       |
  u1|                       |u2
    |                       |
    |                       |
    |                       |
    |                       |
    __u6_______u3_________u7__    
""" 

commands  = {"forward": 'w0-1', 
             "backward": 'w0--1',
             "clockwise": 'r0-1',
             "anticlockwise": 'r0--1'}


def new_seq(sequence):
    final = []
    for x in sequence:
        if 'w' not in x: 
            final.append(x)
            continue
        x = x.split('-')
        for i in range(int(x[1])):
            final.append('w0-1')
    return final
        

def check_stop(value):    
    if value <= 2: return 1 


def print_text(directions:list):
    """_summary_
    takes a list of the four cardinal directions and outputs a vidual text represnetation
    of the robot's state
    Args:
        directions (list): _description_
        directions[0] = north/u0
        directions[1] = east/u2
        directions[2] = south/u3
        directions[3] = west/u1
        directions[4] = northeast/u1   
        directions[5] = northwest/u1   
        directions[6] = southwest/u1   
        directions[7] = southeast/u1       
    """
    print(f"FR:{int(directions[5]):02d} .. F:{int(directions[0]):02d} .. FR:{int(directions[4]):02d}")
    print(f"..................")
    print(f"L:{int(directions[3]):02d} ............ R:{int(directions[1]):02d}")
    print(f"..................")
    print(f"BL:{int(directions[6]):02d} .. B:{int(directions[2]):02d} .. BR:{int(directions[7]):02d}")
    print("_________________________________________")
    
    
def run_sensor(name:str, index:int, val:int, directions:list):
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
    """
    transmit(str)
    directions[index] = val
    time.sleep(0.1)
    return directions


        
while RUNNING:
    directions = [-1, -1, -1, -1, -1, -1, -1, -1] # u0, u2, u3, u1, u4, u5, u6. u7

    if ct < len(cmd_sequence):
        directions = run_sensor('u0', 0, responses[0], directions)
        directions = run_sensor('u1', 3, responses[0], directions)
        directions = run_sensor('u2', 1, responses[0], directions)
        directions = run_sensor('u3', 2, responses[0], directions)
        directions = run_sensor('u4', 4, responses[0], directions)
        directions = run_sensor('u5', 5, responses[0], directions)
        directions = run_sensor('u6', 6, responses[0], directions)
        directions = run_sensor('u7', 7, responses[0], directions)
        
        transmit(cmd_sequence[ct])
        time.sleep(0.1)

        if responses[0] == math.inf:
            ct += 1

        time.sleep(0.1)
    else:
        RUNNING = False
        print("Sequence complete!")

