import time
import serial
from threading import Thread

# Set up the serial connection for sending commands to Serial1 on the Arduino
command_port = '/dev/tty.usbmodem14101'  # Replace with the correct port for Serial1 on your system
command_ser = serial.Serial(command_port, 9600, timeout=1)

# Set up the serial connection for receiving sensor data from the default Serial on the Arduino
sensor_port = '/dev/tty.usbmodem14201'  # Replace with the correct port for the default Serial on your system
sensor_ser = serial.Serial(sensor_port, 9600, timeout=1)

def receive_sensor_data():
    while True:
        try:
            if sensor_ser.in_waiting > 0:
                sensor_data_str = sensor_ser.readline().decode('utf-8').strip()
                try:
                    sensor_readings = [float(x) for x in sensor_data_str.split(',')]
                    # Store the latest readings in a global variable
                    global latest_readings
                    latest_readings = sensor_readings
                except ValueError as e:
                    print("Parsing error:", e)
        except serial.SerialException as e:
            print("Serial exception:", e)
            time.sleep(1)  # Brief pause to prevent constant error printing

def print_sensor_readings(readings):
    print("Sensor Readings:")
    print(f"          N: {readings[0]:.3f}")
    print(f"          |")
    print(f"W: {readings[3]:.3f}----E----{readings[1]:.3f}")
    print(f"          |")
    print(f"          S: {readings[2]:.3f}")
    print()  # Blank line for better readability

# Start the thread to receive sensor data
Thread(target=receive_sensor_data, daemon=True).start()

# Initialize the latest readings variable
latest_readings = [0.0, 0.0, 0.0, 0.0]

# Main loop for sending commands and handling user input
while True:
    user_input = input("Enter command: ").strip().lower()
    if user_input == "sensor":
        print_sensor_readings(latest_readings)
    elif user_input in ['w', 's', 'a', 'd']:
        command_ser.write(user_input.encode())  # Send the command to Serial1 on the Arduino