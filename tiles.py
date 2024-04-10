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
rows = 88
row_w = screen_w / rows
row_h = screen_h
tile_w = row_w - 2
half_t_w = tile_w/2
tile_h = tile_w*2
y = 10
fLines = getMidiOutput("TwinkleTwinkle.mid")
class rgb:
    BLACK = (0,0,0)
    WHITE = (255,255,255)
    BLUE = (0,0,255)
    RED = (255,0,0)
    GREEN = (0,255,0)
    YELLOW = (255,255,0)
def number_to_note(number, whole_only):
    if (whole_only):
        notes = ['A','B','C','D','E','F','G']
        return notes[number%len(notes)]
    else:
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return notes[number%12]
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
    global tiles, rows, row_w, r_num
    row = int(fLines[r_num][1])
    r_num += 1
    color = rgb.BLUE
    if color == rgb.BLACK or color == rgb.WHITE:
        color = random.choice([rgb.BLUE,rgb.YELLOW,rgb.GREEN,rgb.RED])
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
    tiles.append([color,2+row_w*row,y])
# def find_length():
    
def start_game():
    global game, tiles
    game = True
    tiles = [[rgb.BLUE, 2, -tile_h*2]]
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
def handle_title_tile_click(select_from):
    global mouse_position, score, tile_w, tile_h, rows
    x, y = mouse_position
    i = 0
    z = 0
    click_on_tile = False
    for t in select_from:
        if rows != 2 or t[0] in [rgb.RED, rgb.GREEN]:
            cur_row = z
            if x > 2+row_w*cur_row and x < 2+row_w*cur_row + tile_w and y > t[1] and y < t[1] + tile_h:
                click_on_tile = True
                return select_from[i]
            z += 1
        i += 1
def screens_click():
    global screens, cur_screen, note_speed, rows, row_w, row_h, screen_w, screen_h, half_t_w, tile_w, tile_h
    selection = handle_title_tile_click(screens[cur_screen])
    selected_long = selection
    if selection == None:
        return None
    selection = selection[0]
    if cur_screen == 0:
        if selection == rgb.RED:
            start_game()
def draw_vertical_lines():
    global rows, screen, row_w, row_h
    for x in range(0,rows+1):
        pygame.draw.line(screen, (0,0,0), (row_w*x, 0), (row_w*x, row_h), 2)
        # label("monospace", 15, number_to_note(x, False) ,rgb.BLACK,(),center=(row_w*x + row_w/2, screen_h-20))
tiles = []
r_num = 0;
title_screen = [[rgb.RED, 200, tile_w, tile_h, "Play!",30]]
screens = [title_screen]
cur_screen = 0
game = False
while True:
    screen.fill((255,255,255))
    draw_vertical_lines()
    if game == True:
        for t in tiles:
            pygame.draw.rect(screen, t[0], [t[1], t[2], tile_w, tile_h], 0)
            if t[2] < row_h and t[2] + tile_h != row_h:
                t[2] = t[2]+note_speed
    else:
        label("monospace",100,"Musik",rgb.BLACK,(),center=(half_w, 100))
        i = 0
        for t in screens[cur_screen]:
            if rows != 2 or t[0] in [rgb.RED, rgb.GREEN]:
                cur_row = i
                pygame.draw.rect(screen, t[0], [2+row_w*cur_row, t[1], tile_w, tile_h], 0)
                label("monospace",tile_w/len(t[4])+5,t[4],rgb.BLACK,(),center=(tile_w*cur_row+half_t_w+cur_row*2.5,t[1]+tile_h/2))
                i += 1
    for event in pygame.event.get():
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_position = pygame.mouse.get_pos()
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game == True:
                click_tile()
            else:
                screens_click()
    pygame.display.flip()
    clock.tick(FPS)