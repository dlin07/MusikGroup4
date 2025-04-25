import serial
import threading
import queue
import time
from midi2Tiles import *
import pygame.midi

arduino_port = 'COM4'  # Replace with the actual serial port of your Arduino
baud_rate = 115200

perfect = 0
early = 0
late = 0
miss = 0

gameover_received = False

def print_devices():
    for n in range(pygame.midi.get_count()):
        print (n,pygame.midi.get_device_info(n))

def read_kbd_input(inputQueue, input_device):
    print('Ready for keyboard input:')
    while (True):
        if input_device.poll():
            data = input_device.read(1)[0]
            action = data[0]
            event = action[0]
            note_number = action[1]
            if (event == 159): # User pressed note (if this doesn't work try 143)
                input_str = str(note_number) # If this doesn't work, try bit shifting (<< 8)
                # input_str = input()
                inputQueue.put(input_str)

def user_accuracy(button_pressed_name, button_pressed_time, example_pressed_name, example_pressed_time, threshold):
    if(button_pressed_name == example_pressed_name):
        if(button_pressed_time < example_pressed_time - threshold):
            global early
            early += 1
            return 'Early'
        elif (button_pressed_time > example_pressed_time + threshold):
            global late
            late += 1
            return 'Late'
        else:
            global perfect
            perfect += 1
            return 'Perfect'
    else:
        global miss
        miss += 1
        return 'Miss'

def main():
    try:
        example_song = getMidiOutput('ChromaticScale.mid')
        # example_song = [['note_on', 60, 4, 0], ['note_on', 61, 6, 0], ['note_on', 62, 8, 0], ['note_on', 63, 10, 0], ['note_on', 64, 12, 0], ['note_on', 65, 14, 0], ['note_on', 66, 16, 0], ['note_on', 67, 18, 0], ['note_on', 68, 20, 0], ['note_on', 69, 22, 0], ['note_on', 70, 24, 0], ['note_on', 71, 26, 0], ['note_on', 72, 28, 0]]
        inputQueue = queue.Queue()

        pos = 0
        arduino = serial.Serial(arduino_port, baud_rate, timeout=1)
        time.sleep(2)  # Allow time for the connection to establish

        # Replace this with lines 148-152 of midi.py for setup, followed by lines 160-164 to start reading
        try:
            pygame.midi.init()
            print_devices()
        except:
            print("unable to open device")
        
        try:
            my_input = pygame.midi.Input(1)
            inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,my_input), daemon=True)
            inputThread.start()
        except:
            print("unable to read input")

        arduino.write("start".encode('utf-8') + b'\n')
        time.sleep(0.1)  # Give the Arduino time to process
        
        if arduino.in_waiting > 0:
            received_data = arduino.readline().decode('utf-8').strip()
            print("Received from Arduino:", received_data)
        else:
            print("No data received from Arduino")
        
        start_time = time.time() + 1

        while pos < len(example_song):
            currTime = time.time() - start_time
            if (currTime - example_song[pos][2] > 1.5):
                pos += 1
                if (pos >= len(example_song)):
                    break
                print(example_song[pos][1])
            if (inputQueue.qsize() > 0):
                input_str = inputQueue.get()
                if input_str.lower() == 'exit':
                    break
                print("input_str = {} {}".format(input_str, currTime))
                
                button_pressed_time = time.time() - start_time
                result = user_accuracy(input_str, button_pressed_time, str(example_song[pos][1]), example_song[pos][2], 0.2)
                arduino.write(result.encode('utf-8') + b'\n')
                time.sleep(0.1)  # Give the Arduino time to process

                print(result)
                if (currTime - example_song[pos][2] >= -1.5):
                    pos += 1
                    if (pos >= len(example_song)):
                        break
                    print(example_song[pos][1])
            if arduino.in_waiting > 0:
                received_data = arduino.readline().decode('utf-8').strip()
                print("Received from Arduino:", received_data)
                if received_data == "game over":
                    global gameover_received
                    gameover_received = True
                    break
        # while not gameover_received:
        #     if arduino.in_waiting > 0:
        #         received_data = arduino.readline().decode('utf-8').strip()
        #         print("Received from Arduino:", received_data)
        #         if received_data == "game over":
        #             gameover_received = True
        #             break
            # else:
            #     print("No data received from Arduino")
        
        
        time.sleep(0.1) # Give the Arduino time to process
        arduino.write((str(perfect) + "," + str(early + late + miss)).encode('utf-8') + b'\n')
        time.sleep(0.1)  # Give the Arduino time to process
        
        if arduino.in_waiting > 0:
            received_data = arduino.readline().decode('utf-8').strip()
            print("Received from Arduino:", received_data)
        else:
            print("No data received from Arduino")
        
        arduino.close()

    except serial.SerialException as e:
        print(f"Error: {e}")

        # The rest of your program goes here.
        # print(time.time() - start_time, example_song[pos][1])
        # time.sleep(0.2)
    print("{},{}".format(perfect, early + late + miss))
    print("End.")

if (__name__ == '__main__'): 
    main()
