import serial
import time
from midi2Tiles import *
import threading

arduino_port = 'COM4'  # Replace with the actual serial port of your Arduino
baud_rate = 115200

hits = 0
misses = 0
threshold = 0.2

try:
    arduino = serial.Serial(arduino_port, baud_rate, timeout=1)
    time.sleep(2)  # Allow time for the connection to establish

    arduino.write("start".encode('utf-8') + b'\n')
    time.sleep(0.1)  # Give the Arduino time to process
    
    if arduino.in_waiting > 0:
        received_data = arduino.readline().decode('utf-8').strip()
        print("Received from Arduino:", received_data)
    else:
        print("No data received from Arduino")

    start_time = time.time()

    while True:
        data_to_send = input("Enter data to send to Arduino (or 'exit' to quit): ")
        if data_to_send.lower() == 'exit':
            break

        arduino.write(data_to_send.encode('utf-8') + b'\n')
        time.sleep(0.1)  # Give the Arduino time to process
        
        if arduino.in_waiting > 0:
            received_data = arduino.readline().decode('utf-8').strip()
            print("Received from Arduino:", received_data)
            if received_data == "game over":
                break
        # else:
        #     print("No data received from Arduino")
    
    time.sleep(0.1) # Give the Arduino time to process
    arduino.write((hits + "," + misses).encode('utf-8') + b'\n')
    time.sleep(0.1)  # Give the Arduino time to process
    
    if arduino.in_waiting > 0:
        received_data = arduino.readline().decode('utf-8').strip()
        print("Received from Arduino:", received_data)
    else:
        print("No data received from Arduino")
    
    arduino.close()

except serial.SerialException as e:
    print(f"Error: {e}")