import pygame.midi
from serial import Serial


port_name = "COM3"
baud = 115200
arduino = Serial(port_name, baud, timeout=1)



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


            arduino.write((str(note_number) + "\n").encode())
            print (note_number, velocity)


if __name__ == '__main__':
    pygame.midi.init()
    print_devices()
    my_input = pygame.midi.Input(1)
    readInput(my_input)

