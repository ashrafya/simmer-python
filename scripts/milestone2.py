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
PORT_TX = 61200     # The port used by the CLIENT to receive
PORT_RX = 61201     # The port used by the CLIENT to send data

# Received responses
responses = [False]
time_rx = 'Never'

# Create tx and rx threads
Thread(target = receive, daemon = True).start()

# Run the sequence of commands
RUNNING = True
LOCAL_NO_TURN = False
LOAD = False

#cmd_sequence = ['w0-36', 'r0-90', 'w0-36', 'r0-90', 'w0-12', 'r0--90', 'w0-24', 'r0--90', 'w0-6', 'r0-720']

responses = [math.inf, math.inf, math.inf, math.inf]

ct = 0
# Main loop logic
while RUNNING:
    if ct < 100:
        # Check front sensor
        transmit('u2')
        time.sleep(0.05)
        sensor_reading_front = responses[0]
        print(f"Front sensor reading: {round(responses[0], 3)}")

        # Check left sensor
        transmit('u1')
        time.sleep(0.05)
        sensor_reading_left = responses[0]
        print(f"Left sensor reading: {round(responses[0], 3)}")
        
        transmit('u0')
        time.sleep(0.05)
        sensor_reading_right = responses[0]
        print(f"Right sensor reading: {round(responses[0], 3)}")
        
        transmit('u4')
        time.sleep(0.05)
        sensor_reading_right_45 = responses[0]
        print(f"Right 45 sensor reading: {round(responses[0], 3)}")
        
        transmit('u5')
        time.sleep(0.05)
        sensor_reading_left_45 = responses[0]
        print(f"Left 45 sensor reading: {round(responses[0], 3)}")
        
        transmit('u3')
        time.sleep(0.05)
        sensor_reading_back = responses[0]
        print(f"Back sensor reading: {round(responses[0], 3)}")
        
        transmit('u6')
        time.sleep(0.05)
        sensor_reading_back_right_45 = responses[0]
        print(f"Back right sensor reading: {round(responses[0], 3)}")
        
        transmit('u7')
        time.sleep(0.05)
        sensor_reading_back_left_45 = responses[0]
        print(f"Back left sensor reading: {round(responses[0], 3)}")
        
        # If an obstacle is detected in front, turn right
        if sensor_reading_right_45 < 3:
            transmit('r0--20')
            time.sleep(0.05)
        
        if sensor_reading_left_45 < 3:
            transmit('r0-20')
            time.sleep(0.05)
        
        #if sensor_reading_front <20 and sensor_reading_right <12 and sensor_reading_back> 23 and sensor_reading_left>35:
            #position = True
        #else:
            #position = False
        
        
        if sensor_reading_front < 5 or (sensor_reading_left >= 25 and sensor_reading_back > 26 ): #or position:

        # If no obstacle is detected on the left, turn left
            if sensor_reading_left >= 10:
                transmit('r0--90')
                time.sleep(0.05)
            elif sensor_reading_right >= 10:
                transmit('r0-90')
                time.sleep(0.05)
            else:
                if sensor_reading_right>sensor_reading_left:
                    transmit('r0-180')
                    time.sleep(0.05)
                elif sensor_reading_left>sensor_reading_right:
                    transmit('r0--180')
                    time.sleep(0.05)
        # If no obstacles in front and left is blocked, move forward
        count_main_4 = sum([v > 13 for v in [sensor_reading_front, sensor_reading_back, sensor_reading_left, sensor_reading_right]])
        count_45s = sum([v > 13 for v in [sensor_reading_back_left_45, sensor_reading_back_right_45, sensor_reading_left_45, sensor_reading_right_45]])

        # Conditional statement to check if three or more variables are greater than 100
        if count_main_4 >= 4 or count_45s>=4:
            LOCAL_NO_TURN= True
            RUNNING = False
            print("Localized No Direction")
        
        else:
            transmit('w0-1')
            time.sleep(0.05)

        # Check for infinite response
        if responses[0] == math.inf:
            ct = ct

        time.sleep(0.05)
    else:
        RUNNING = False
        print("Sequence complete!")

"""
while LOCAL_NO_TURN:
    time.sleep(0.5)
    
    if not ((40 < sensor_reading_front + sensor_reading_back < 48) and sensor_reading_front < sensor_reading_back and sensor_reading_front < 14):
                transmit('u2')
                time.sleep(0.05)
                sensor_reading_front = responses[0]
                print(f"Front sensor reading: {round(responses[0], 3)}")
                
                transmit('u3')
                time.sleep(0.05)
                sensor_reading_back = responses[0]
                print(f"Back sensor reading: {round(responses[0], 3)}")
                
                transmit('r0--10')
                time.sleep(0.05)
                
    elif ( >sensor_reading_front > ) and ( > sensor_reading_back > ) and (> sensor_reading_left >) and (> sensor_reading_right > )
        LOCALIZATION = True
        LOCAL_NO_TURN = False
        print("Localized with direction")
        """