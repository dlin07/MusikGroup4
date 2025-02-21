import sys, random, os, time
import pygame
from mido import MidiFile
from midi2Tiles import *

pygame.init()
pygame.mixer.init()
FPS = 60
size=width, height=1500, 650
screen_w = width
screen_h = height
half_w = screen_w/2
pygame.display.set_caption("Musik")
note_speed = 5
score = 0
cols = 52
row_w = screen_w / cols
row_h = screen_h
tile_w = row_w - 2
half_t_w = tile_w/2
tile_h = tile_w*2
y = 10
fLines = getMidiOutput("ChromaticScale.mid")
class rgb:
    BLACK = (0,0,0)
    WHITE = (255,255,255)
    BLUE = (0,0,255)
    RED = (255,0,0)
    GREEN = (0,255,0)
    YELLOW = (255,255,0)
def number_to_note(number, white_only):
    if (white_only):
        notes = ['C','D','E','F','G','A','B']
        return notes[number%len(notes)]
    else:
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return notes[number%12]
def twelve_to_octave_key(number):
    sw = {
        0: 0, #A
        1: 0.5, #A-sharp
        2: 1, #B
        3: 2, #C
        4: 2.5, #C-sharp
        5: 3, #D
        6: 3.5, #D-sharp
        7: 4, #E
        8: 5, #F
        9: 5.5, #F-sharp
        10: 6, #G
        11: 6.5 #G-sharp
    }
    return sw.get(number, -1);
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
print(time.time())
def font(font_name,size):
    return pygame.font.SysFont(font_name, int(size))
def label(font_name,size,text,rgb,pos,center=False):
    global screen
    lbl = font(font_name,size).render(text, 1, rgb)
    if center == False:
        screen.blit(lbl, pos)
    else:
        screen.blit(lbl, lbl.get_rect(center=center))
def add_tile():
    global tiles, cols, row_w, r_num
    c = int(fLines[r_num][1])
    # lst = [0, 2, 4, 5, 7, 9, 11]
    # if c % 12 in lst:
    col = ((c - 21) // 12) * 7 + twelve_to_octave_key((c - 21) % 12)
    # else:
        # col = 0
    color = rgb.BLUE
    def getY():
        global tile_h
        n = -random.randint(int(tile_h),int(1000))
        for t in tiles:
            if n == t[2]-tile_h-1 and n != t[2]:
                return n
        try:
            return getY()
        except:
            return t[2]-tile_h-1
    y = getY()
    if (fLines[r_num][0] == 'note_on'):
        tiles.append([color,2+row_w*col, fLines[r_num][2]*-300])
    r_num += 1
# def find_length():
    
def start_game():
    global game, tiles
    game = True
    tiles = [[rgb.BLUE, 2, -tile_h*2, 0]]
    [add_tile() for x in range(0, len(fLines))]
def click_tile():
    global mouse_position, tiles, score, tile_w, tile_h
    x, y = mouse_position
    i = 0
    click_on_tile = False
    for t in tiles:
        if x > t[1] and x < t[1] + tile_w and y > t[2] and y < t[2] + tile_h: # Coordinate tracking
            click_on_tile = True
            del tiles[i]
        i += 1
    print(time.time())
def handle_title_tile_click():
    global mouse_position
    x, y = mouse_position
    if x > 500 and x < 1000 and y > 350 and y < 550:
        start_game()
def draw_vertical_lines():
    global cols, screen, row_w, row_h
    for x in range(0,cols+1):
        pygame.draw.line(screen, (0,0,0), (row_w*x, 0), (row_w*x, row_h), 2)
        label("monospace", 15, number_to_note(x + 5, True) ,rgb.BLACK,(),center=(row_w*x + row_w/2, screen_h-20))
tiles = []
r_num = 0;
cur_screen = 0
game = False
bg = pygame.image.load("background.png")
bg = pygame.transform.scale(bg, (width, height))
while True:
    screen.fill((255,255,255))
    screen.blit(bg, (0, 0))
    # draw_vertical_lines()
    if game == True:
        for t in tiles:
            pygame.draw.rect(screen, t[0], [t[1], t[2], tile_w, tile_h], 0)
            # label("monospace", 15, number_to_note(t[3], True), rgb.BLACK,(),center=(t[1],t[2]))
            if t[2] < row_h and t[2] + tile_h != row_h:
                t[2] = t[2]+note_speed
    else:
        pygame.draw.rect(screen, (255,0,0), (500, 350, 500, 200))
        label("monospace",100,"Musik",rgb.BLACK,(),center=(half_w, 100))
        label("monospace",50,"Play",rgb.BLACK,(),center=(half_w, 450))
    for event in pygame.event.get():
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_position = pygame.mouse.get_pos()
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game == True:
                click_tile()
            else:
                if cur_screen == 0:
                    handle_title_tile_click()
    pygame.display.flip()
    clock.tick(FPS)