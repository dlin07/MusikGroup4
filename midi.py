import pygame.midi
from serial import Serial
import threading
from time import sleep
import time
import random
import numpy as np

port_name = "COM3"
baud = 115200
arduino = Serial(port_name, baud, timeout=0)

noteState = np.zeros(120)

class arduino_thread(threading.Thread):

    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        while(True):
            if(arduino.in_waiting):
                message = arduino.readline()
                message = str(message)
                print("arduino message: ", message)


    

def print_devices():
    for n in range(pygame.midi.get_count()):
        print (n,pygame.midi.get_device_info(n))

def number_to_note(number):
    notes = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']
    return notes[number%12]

def readInput(input_device):
    moodChanger = time.time()
    emotions = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 255, 255)]

    while True:
        # if(time.time() - moodChanger >= 1):
        #     choice = random.choice(emotions)
        #     print(choice)
        #     setMood(choice[0], choice[1], choice[2])
        #     moodChanger = time.time()
        #     print("mood set")


        if input_device.poll():
            data = input_device.read(1)[0]
            action = data[0] 
            # timestamp = event[1]

            event = action[0]
            note_number = action[1]
            velocity = action[2]

            if(event == 159 or event == 143):
                # note pressed or released
                specifier = note_number << 8
                
                global noteState
                if (event == 159):
                    noteState[note_number] = 1
                elif (event == 143):
                    noteState[note_number] = 0
                # print(noteState)

            
            if(event == 189 or event == 190 or event == 191):
                # pedal event
                specifier = event << 8
                   
            modifier = velocity
            packet = specifier + modifier
            # arduino reads this as modifier + specifier?
            
            # Convert packet to 2 bytes and send over serial
            arduino.write(packet.to_bytes(2, byteorder='big'))
            sleep(0.01)
            # print(str(specifier >> 8) + " " + str(modifier))

def setMood(red, green, blue):
    rgb = [red, green, blue]

    for index, color in enumerate(rgb):
        specifier = index + 1 << 8
        modifier = color

        packet = specifier + modifier
        # arduino reads this as modifier + specifier?
        
        # Convert packet to 2 bytes and send over serial
        arduino.write(packet.to_bytes(2, byteorder='big'))
        sleep(0.01)
        # print(str(specifier >> 8) + " " + str(modifier))



if __name__ == '__main__':
    pygame.midi.init()
    print_devices()

    arduino_thr = arduino_thread(1, "Arduino-Comm", 1)
    arduino_thr.start()
    
    my_input = pygame.midi.Input(1)
    
    readInput(my_input)

