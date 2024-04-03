import sys, random, os, time
import pygame
pygame.init()
pygame.mixer.init()
FPS = 120
size=width, height=1500, 650
screen_w = width
screen_h = height
half_w = screen_w/2
pygame.display.set_caption("Musik")
note_speed = 2
score = 0
hscore = 0
rows = 88
row_w = screen_w / rows
row_h = screen_h
tile_w = row_w - 2
half_t_w = tile_w/2
tile_h = tile_w*2
y = 10
fLines = open("MIDI_sample_output.txt", "r").read().splitlines()
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
    # row = random.randint(int(0),int(rows-1)) # Random addition of tile
    row = int(fLines[r_num])
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
def play(filename_with_sound):
    pygame.mixer.music.load(open("sounds/%s"%(filename_with_sound),"rb"))
    pygame.mixer.music.play()
def start_game():
    global game, hscore_msg, tiles
    game = True
    play("begin.ogg")
    hscore_msg = False
    tiles = [[rgb.BLUE, 2, -tile_h*2],[rgb.GREEN, 2+row_w*1, -tile_h*2]]
    [add_tile() for x in range(0,7)]
def end_game():
    global game, score, hscore, hscore_msg, tiles
    play("end.ogg")
    game = False
    highscore("SAVE")
    score = 0
def highscore(method):
    global score, hscore, hscore_msg
    if method == "SAVE":
        if score > hscore:
            hscore = score
            hscore_msg = True
            open('.hs','w').write(str(score))
    elif method == "BGCOLOR":
        # if score < hscore or score == 0:
            return rgb.WHITE
        # else:
            # return rgb.BLACK
    elif method == "FGCOLOR":
        # if score < hscore or score == 0:
            return rgb.BLACK
        # else:
            # return rgb.WHITE
def click_tile():
    global mouse_position, tiles, score, tile_w, tile_h
    x, y = mouse_position
    i = 0
    click_on_tile = False
    for t in tiles:
        if x > t[1] and x < t[1] + tile_w and y > t[2] and y < t[2] + tile_h: # Coordinate tracking
            click_on_tile = True
            del tiles[i]
            play("click.ogg")
            add_tile()
            score += 1
        i += 1
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
                play("click.ogg")
                return select_from[i]
            z += 1
        i += 1
    if click_on_tile == False:
        play("end.ogg")
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
        elif selection == rgb.YELLOW:
            cur_screen += 1
        elif selection == rgb.GREEN:
            cur_screen += 2
        elif selection == rgb.BLUE:
            cur_screen += 3
def draw_vertical_lines():
    global rows, screen, row_w, row_h
    for x in range(0,rows+1):
        pygame.draw.line(screen, highscore("FGCOLOR"), (row_w*x, 0), (row_w*x, row_h), 2)
        label("monospace", 15, number_to_note(x, False) ,rgb.BLACK,(),center=(row_w*x + row_w/2, screen_h-20))
tiles = []
r_num = 0;
title_screen = [[rgb.RED, 200, tile_w, tile_h, "Play!",30]]
screens = [title_screen]
cur_screen = 0
game = False
hscore_msg = False
while True:
    screen.fill(highscore("BGCOLOR"))
    draw_vertical_lines()
    if game == True:
        for t in tiles:
            pygame.draw.rect(screen, t[0], [t[1], t[2], tile_w, tile_h], 0)
            if t[2] < row_h and t[2] + tile_h != row_h:
                t[2] = t[2]+note_speed
            # else:
              #  end_game()
        label("monospace",100,str(score),highscore("FGCOLOR"),(row_w/3.25, screen_h-100))
    else:
        i = 0
        for t in screens[cur_screen]:
            if rows != 2 or t[0] in [rgb.RED, rgb.GREEN]:
                cur_row = i
                pygame.draw.rect(screen, t[0], [2+row_w*cur_row, t[1], tile_w, tile_h], 0)
                label("monospace",tile_w/len(t[4])+5,t[4],rgb.BLACK,(),center=(tile_w*cur_row+half_t_w+cur_row*2.5,t[1]+tile_h/2))
                i += 1
        if hscore_msg == False:
            label("monospace",100,"Musik",rgb.BLACK,(),center=(half_w, 100))
            # label("monospace", 26,"A B C D E F G A B C D E F G A B C D E F G A B C D E F G A B C D E F G A B C D E F G A B C D E F G",rgb.BLACK,(),center=(half_w, screen_h-20))
        else:
            label("monospace",65,"High Score!",rgb.BLACK,(),center=(half_w, 100))
            label("monospace",100,str(hscore),rgb.BLACK,(),center=(half_w, 200))
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