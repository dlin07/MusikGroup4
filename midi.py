import pygame.midi
from serial import Serial
import threading
from time import sleep


port_name = "COM3"
baud = 115200
arduino = Serial(port_name, baud, timeout=0)

noteRange = []

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
    
    while True:
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
            
            if(event == 189 or event == 190 or event == 191):
                # pedal event
                specifier = event << 8
                   
            modifier = velocity
            packet = specifier + modifier
            # arduino reads this as modifier + specifier?
            
            # Convert packet to 2 bytes and send over serial
            arduino.write(packet.to_bytes(2, byteorder='big'))
            sleep(0.01)
            print(str(specifier >> 8) + " " + str(modifier))

def sendNoteRange(input_device):
    global noteRange
    
    while True:
        if input_device.poll():
            event = input_device.read(1)[0]

            data = event[0]

            event_type = data[0]
            note_number = data[1]

            if(event_type == 159):
                noteRange.append(note_number)
            elif(event_type == 143):
                # print(noteRange)
                noteRange.remove(note_number)

            # if(len(noteRange) == 2):
            #     noteRange = noteRange.sort()
            if(len(noteRange) == 2):
                noteRange.sort()
                print(noteRange)
                packet = (noteRange[0] << 8) + noteRange[1]

                arduino.write(packet.to_bytes(2, byteorder='big'))
                sleep(0.01)
                return




        
        



if __name__ == '__main__':
    pygame.midi.init()
    print_devices()

    arduino_thr = arduino_thread(1, "Arduino-Comm", 1)
    arduino_thr.start()
    
    my_input = pygame.midi.Input(1)
    # sendNoteRange(my_input)
    # print(noteRange)

    readInput(my_input)

