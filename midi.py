import pygame.midi
from serial import Serial
import threading


port_name = "COM3"
baud = 115200
arduino = Serial(port_name, baud, timeout=1)

class arduino_thread(threading.Thread):

    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        while(True):
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
    
    while True:
        if input_device.poll():
            event = input_device.read(1)[0]
            data = event[0] 
            timestamp = event[1]
            note_number = data[1]
            velocity = data[2]
            
            print("a", note_number, velocity)


            bytesWritten = arduino.write((str(note_number) + " " + str(velocity) + "\n").encode())
            print("b", note_number, velocity, bytesWritten)



        



if __name__ == '__main__':
    pygame.midi.init()
    print_devices()

    arduino_thr = arduino_thread(1, "Arduino-Comm", 1)
    arduino_thr.start()
    
    my_input = pygame.midi.Input(1)
    
    readInput(my_input)

