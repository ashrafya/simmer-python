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

def log_to_file_and_print(input_string, log_file_path='boi.txt'):
    try:
        # Open the log file in append mode
        with open(log_file_path, 'a') as log_file:
            # Write the input string to the log file
            log_file.write("\t" + input_string)
        
        # Print the input string to the console
        print(input_string)

    except Exception as e:
        # Handle any exceptions that may occur
        print(f"An error occurred: {str(e)}")
        
ct = 0
while RUNNING:

    if ct < len(cmd_sequence):

        transmit('u0')
        time.sleep(0.05)
        log_to_file_and_print("U0: " + '{:06.6}'.format(round(responses[0], 3)))
        if responses[0]<2:
            transmit('xx')
            log_to_file_and_print("TOO CLOSE TO WALL I\"M SCARED!!!")
            time.sleep(0.05)
            break

        transmit('u1')
        time.sleep(0.05)
        log_to_file_and_print("U1: " + '{:06.6}'.format(round(responses[0], 3)))
        if responses[0]<2:
            transmit('xx')
            log_to_file_and_print("TOO CLOSE TO WALL I\"M SCARED!!!")
            time.sleep(0.05)
            break

        transmit('u2')
        time.sleep(0.05)
        log_to_file_and_print("U2: " + '{:06.6}'.format(round(responses[0], 3)))
        if responses[0]<2:
            transmit('xx')
            log_to_file_and_print("TOO CLOSE TO WALL I\"M SCARED!!!")
            time.sleep(0.05)
            break

        transmit('u3')
        time.sleep(0.05)
        log_to_file_and_print("U3: " + '{:06.6}'.format(round(responses[0], 3)))
        if responses[0]<2:
            transmit('xx')
            log_to_file_and_print("TOO CLOSE TO WALL I\"M SCARED!!!")
            time.sleep(0.05)
            break

        transmit('u4')
        time.sleep(0.05)
        log_to_file_and_print("U4: " + '{:06.6}'.format(round(responses[0], 3)))
        if responses[0]<2:
            transmit('xx')
            log_to_file_and_print("TOO CLOSE TO WALL I\"M SCARED!!!")
            time.sleep(0.05)
            break
        
        transmit('u5')
        time.sleep(0.05)
        log_to_file_and_print("U5: " + '{:06.6}'.format(round(responses[0], 3)))
        if responses[0]<2:
            transmit('xx')
            log_to_file_and_print("TOO CLOSE TO WALL I\"M SCARED!!!")
            time.sleep(0.05)
            break
        
        log_to_file_and_print("\n")
        transmit(cmd_sequence[ct])
        time.sleep(0.05)

        if responses[0] == math.inf:
            ct += 1

        time.sleep(0.05)
    else:
        RUNNING = False
        log_to_file_and_print("Sequence complete!")
