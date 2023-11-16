"""
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
"""

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

LAG = 0.10


def transmit(data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT_TX))
            s.send(data.encode("utf-8"))
            
        except (ConnectionRefusedError, ConnectionResetError):
            print("Tx Connection was refused or reset.")
            _thread.interrupt_main()
        except TimeoutError:
            print("Tx socket timed out.")
            _thread.interrupt_main()
        except EOFError:
            print("\nKeyboardInterrupt triggered. Closing...")
            _thread.interrupt_main()
    
    time.sleep(LAG)


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
                print("Rx connection was refused or reset.")
                _thread.interrupt_main()
            except TimeoutError:
                print("Response not received from robot.")
                _thread.interrupt_main()


def bytes_to_list(msg):
    num_responses = int(len(msg) / 8)
    data = struct.unpack("%sd" % str(num_responses), msg)
    return data


# region: NetworkSetup
### Network Setup ###
HOST = "127.0.0.1"  # The server's hostname or IP address
PORT_TX = 61200  # The port used by the *CLIENT* to receive
PORT_RX = 61201  # The port used by the *CLIENT* to send data

# Received responses
responses = [False]
time_rx = "Never"

# Create tx and rx threads
Thread(target=receive, daemon=True).start()

# clear text file
open("boi.txt", "w", encoding="utf-8").close()
# endregion


def log_to_file_and_print(input_string, log_file_path="boi.txt"):
    try:
        # Open the log file in append mode
        with open(log_file_path, "a") as log_file:
            # Write the input string to the log file
            log_file.write(input_string + "\n")

        # Print the input string to the console
        print(input_string)

    except Exception as e:
        # Handle any exceptions that may occur
        print(f"An error occurred: {str(e)}")


# Run the sequence of commands
RUNNING = True
queuedCommands = []
interrupt = ""
grabbingLeftWall = True

def avoidObstacleLeft(u: list):
    # drive command to avoidObstacleLeft
    return ["w0--1", "w1-0.5", "r0-10"]


def avoidObstacleRight(u: list):
    # drive command to avoidObstacleRight
    return ["w0--1", "w1--0.5", "r0--10"]


def turnLeft(u: list):
    # drive command to turnLeft
    global grabbingLeftWall
    log_to_file_and_print("Turning left\n")
    grabbingLeftWall = False
    print("grabbingLeftWall = " + str(grabbingLeftWall))

    if u[2] > u[4]:
        return ["r0--45", "w0-10", "w0-0"]
    else:
        return ["r0--80", "w0-10", "w0-0"]  # TODO: come on man


def turnRight(u: list):
    # drive command to turnRight
    log_to_file_and_print("Turning right\n")
    if u[1] > u[3]:
        return ["r0-45"]
    else:
        return ["r0-85"]


def nudgeLeft():
    # drive command to nudgeLeft
    return ["w1--0.5"]  # TODO: left and right commonize among nudge and avoid obstacle


def nudgeRight():
    # drive command to nudgeRight
    return ["w1-0.5"]


def decide(u: list, p: str = "") -> list:
    global interrupt
    global grabbingLeftWall
    
    if queuedCommands:
        return []
    
    match interrupt:
        case "forward":  # too close forward
            print("backing up a bit")
            return ["w0--0.4"]

        case "forwardRight":  # too close forward right
            return avoidObstacleRight(u)

        case "forwardLeft":  # too close forward left
            return avoidObstacleLeft(u)

        case "right":  # too close right
            return nudgeLeft()

        case "left":  # too close left
            return nudgeRight()

        case _:  # "" or unknown interrupt
            pass

    # found block
    if u[5] < 3 and u[0] > 7:
        print("We found the gold.")
        return []

    # If you can turn left, turn left
    if u[4] > 13 and grabbingLeftWall:
        return turnLeft(u)

    # If you can't turn left or go straight, turn right
    elif u[0] < 6 and u[4] < 8:
        return turnRight(u)

    # Otherwise, drive straight as far as you can see*
    print("drive")
    amt = int(min(u[0], u[5])) - 4
    if amt > 0:
        return ["w0-" + str(amt)]  # TODO
    else:
        return ["r0--10"]



def sense(senseCommands: list):
    # LAG = 0.1
    u = len(senseCommands) * [0.0].copy()
    for i in range(len(senseCommands)):
        transmit(senseCommands[i])
        u[i] = round(responses[0], 3)

    log_to_file_and_print(
        "\t".join(["u" + str(i) + ": " + "{:06.6}".format(u[i]) for i in range(len(u))])
    )
    return u


def interact():
    global interrupt
    global grabbingLeftWall
    senseCommands = [
        "u0",
        "u1",
        "u2",
        "u3",
        "u4",
        "u5",
    ]
    
    # Store all sensor readings
    u = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    while True:
        # update sensor readings and log em
        u = sense(senseCommands)
        if u[4] < 8:
            if not grabbingLeftWall:
                grabbingLeftWall = True
                print("grabbingLeftWall = " + str(grabbingLeftWall))

        # obstacle avoidance
        conditions = {
            "forward": (u[0] < 3 and interrupt != "forward"),
            "forwardRight": (u[1] < 6 and interrupt != "forwardRight"),
            "forwardLeft": (u[2] < 6 and interrupt != "forwardLeft"),
            "right": (u[3] < 2.6 and interrupt != "right"),
            "left": (u[4] < 2.6 and interrupt != "left"),
            "block": (u[5] < 2.8 and interrupt != "block"),
            "": (u[4] > 15) and grabbingLeftWall,
        }

        breakWhile = False
        for key in conditions:
            if conditions[key]:
                transmit("xx")
                interrupt = key
                log_to_file_and_print("interupt: " + interrupt)
                queuedCommands.clear()
                breakWhile = True
                break

        if breakWhile:
            break

        # check if still running
        transmit("w0-0")
        if responses[0] == math.inf:
            # sense once more just in case robot moved too much while sensing
            u = sense(senseCommands)

            # break out of while loop to decide what to do next
            log_to_file_and_print("ready for next move")

            # no more commands left and ready for commands, clear interrupt flag
            if not queuedCommands and interrupt:
                interrupt = ""
                print("Interrupt Cleared!")
            break

    return u


while RUNNING:
    U = interact()
    b = decide(U)
    queuedCommands[:0] = b
    if not queuedCommands:
        log_to_file_and_print("-----\nstopped\n-------")
        RUNNING = False
        continue
        # TODO: THis is bad

    print(queuedCommands)
    transmit(queuedCommands.pop(0))

    # Clear the interrupt if obstacle avoidance is complete


log_to_file_and_print("Sequence complete!")
