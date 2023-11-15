import serial
import time
import matplotlib.pyplot as plt

ser = serial.Serial('COM5', 9600, timeout=0)  # initialize COM port
ser = ' '
start = time.time()
vals = []
t = []
while (end-start) < 20:  # run for 20s
    
    s = input('enter chr: ')
    ser.write(s.encode())    # writes letter to arduino
    time.sleep(0.1)    # pause for 0.1 seconds
    data = ser.readline().strip().decode('ascii')
    print(data)    # read from arduinno
    end = time.time()
    t.append(end)
    vals.append(data)

plt.plot(t, vals)




ser.close()  # close connection