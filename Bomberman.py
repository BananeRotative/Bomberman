# Créé par alexi, le 22/03/2021 en Python 3.7
# Made for 1366x768 screens
import pygame, sys, random
from math import *

#SETTINGS

# Required field
path=""

Use_map_settings = True
#If true : use map defined settings; if false : use settings below

global_player_speed = 5
players_size_collides = 40
exploding_time = 4000   #ms
starting_bomb_amount = 1
starting_bomb_max_range = 2
ms_per_tick = 40
fire_time = 3       #real fire time = fire_time * 6 * ms_per_tick  (ms)
flame_heat = 1      #between 1 and 3
bombs_sliding_speed = 10
push_cooldown = 3000    #ms
infections_time = 15000
speed_infection_slowed = 0.2
speed_infection_boosted = 5

#DEFAULT VALUES
COMMANDES_J1 = [17, 30, 31, 32, 46, 16, 18]
COMMANDES_J2 = [22, 35, 36, 37, 51, 21, 23]
COMMANDES_J3 = [72, 75, 76, 77, 28, 71, 73]
COMMANDES_J4 = ["MOUSE", "MOUSE", "MOUSE", "MOUSE", "MOUSE", "MOUSE", "MOUSE"]
Commands_names = [["z", "q", "s", "d", "c", "a", "e"], ["u", "h", "j", "k", ";", "y", "i"], ["8", "4", "5", "6", "enter", "7", "9"], ["Mouse move", "Mouse move", "Mouse move", "Mouse move", "Left click", "Mouse wheel", "Right click"]]
Player_using_mouse = 3
Player_color = ["#FF0000", "#3F48CC", "#FFF200", "#791BB8"]
Player_number = 4

dev_mode = False


#Game Code

assert path != "", "YOU NEED TO SET THE ABSOLUTE PATH OF THE PARENT OF THIS FILE IN THE path VARIABLE"

Commands = [COMMANDES_J1, COMMANDES_J2, COMMANDES_J3, COMMANDES_J4]
players_collides_grip = 48 - players_size_collides          #48 is player images sizes
Foreground = []   #Things that must appear in foreground : Foreground = [[image0, (Ximage0,Yimage0)], [image1, (Ximage1, Yimage1)], ...]

pygame.init()
screen = pygame.display.set_mode((1366, 768), pygame.FULLSCREEN)

class GameObject:
    def __init__(self, image, tileX, tileY, type, number, solid = False, left_time = None, sliding = False, sliding_direction = None):
        self.image = image
        self.type = type        #type : bomb(1), bonus(3) : corresponds to Models
        self.number = number                                    #number : if type is bomb : number is bomb type (Models order)
        self.tileX = tileX                                      #number : if type is bonus : number is bonus number
        self.tileY = tileY
        self.pos = image.get_rect().move(tileX*64 +X_map_shift, tileY*64 +Y_map_shift)
        self.solid = solid
        self.sliding = sliding
        self.sliding_direction = sliding_direction
        self.lifted = False
        self.lifted_by = None
        if solid:
            player_collide[tileX][tileY] = True
        self.left_time = left_time

    def despawn(self, num_player, num_object):
        if self.solid:
            player_collide[self.tileX][self.tileY] = False
        screen.blit(mapImg, self.pos, [self.pos[0] - X_map_shift, self.pos[1] - Y_map_shift, self.pos[2], self.pos[3]])
        if self.type == 1:
            Bombs_to_del[num_player].append(num_object)
            if self.sliding:
                self.tileX = round((self.pos[0] + 32 - X_map_shift) //64)
                self.tileY = round((self.pos[1] + 32 - Y_map_shift) //64)
            if self.lifted:
                self.tileX = round((Players[self.lifted_by].pos[0] + 32 - Players[self.lifted_by].image_shift[0] - X_map_shift) //64)
                self.tileY = round((Players[self.lifted_by].pos[1] + 32 - Players[self.lifted_by].image_shift[1] - Y_map_shift) //64)
            Is_a_bomb[self.tileX][self.tileY] = False

class Player:
    def __init__(self, image, Player_number, XstartTile, YstartTile):
        self.image = image
        self.player_number = Player_number
        self.image_shift = ((64 - self.image.get_width()) /2, (64 - self.image.get_height()) /2)
        self.pos = image.get_rect().move(XstartTile*64 + X_map_shift + self.image_shift[0], YstartTile*64 + Y_map_shift + self.image_shift[1])
        self.pos = (self.pos[0], self.pos[1], self.image.get_height(), self.image.get_width())
        self.speed_multiplier = 0          #coef. from total speed
        self.bonus_speed = 1.0
        self.direction = 0      #0 : top, 1 : bottom, 2 : left, 3 : right
        self.animation = 3      #0, 1, 2 or 3 : these are steps in the animation (0: img 0; 1: img 2; 2: img 1; 3: img 2)
        self.time_before_next_animation = 0
        self.play_animation = False
        self.key_pressing = [False, False, False, False, False, False, False]

        self.MaxBomb_amount = starting_bomb_amount
        self.first_bomb = 0         #basic bomb
        self.bomb_type = 0          #basic bomb
        self.bomb_stock = [self.first_bomb]
        for bomb in range(self.MaxBomb_amount - 1):
            self.bomb_stock.append(self.bomb_type)
        self.bombs_placed = []
        self.bombs_max_range = starting_bomb_max_range
        self.lifting_bomb = False
        self.bonus = None
        self.punch = None
        self.alive = True
        self.pushed = False
        self.pushed_left_distance = 0
        self.push_cooldown = 0
        #infections
        self.can_place_bombs = True
        self.must_place_bombs = False
        self.time_before_place_bomb = 0
        self.slowed = False
        self.boosted = False
        self.inversed_controls = False
        self.must_walk = False
        self.infections_left_time = 0

    def move(self, With_Bonus_speed = True):
        if With_Bonus_speed:
            bonus_speed = self.bonus_speed
        else:
            bonus_speed = 1
        infections_speed = 1
        if self.slowed:
            infections_speed = speed_infection_slowed
        if self.boosted:
            infections_speed = speed_infection_boosted
        if self.must_walk:
            speed_multiplier = 1
        else:
            speed_multiplier = self.speed_multiplier
        if self.alive:
            shift_collides_corner1 = (0, 0)
            if self.direction == 0:         #looking at top
                movingVect = (0, - (global_player_speed * speed_multiplier * bonus_speed * infections_speed))
                shift_collides_corner1 = (players_collides_grip, players_collides_grip)
                shift_collides_corner2 = (self.image.get_width() - players_collides_grip, players_collides_grip)    #must test top right and top left corners
            elif self.direction == 1:       #looking at bottom
                movingVect = (0, global_player_speed * speed_multiplier * bonus_speed * infections_speed)
                shift_collides_corner1 = (players_collides_grip, self.image.get_height() - players_collides_grip)        #must test bottom right and bottom left corners
                shift_collides_corner2 = (self.image.get_width() - players_collides_grip, self.image.get_height() - players_collides_grip)
            elif self.direction == 2:       #looking at left
                movingVect = (-(global_player_speed * speed_multiplier * bonus_speed * infections_speed), 0)
                shift_collides_corner1 = (players_collides_grip, players_collides_grip)                             #must test top left and bottom left corners
                shift_collides_corner2 = (players_collides_grip, self.image.get_height() - players_collides_grip)
            else:   #if movingVect == 3:    #looking at right
                movingVect = (global_player_speed * speed_multiplier * bonus_speed * infections_speed, 0)
                shift_collides_corner1 = (self.image.get_width() - players_collides_grip, players_collides_grip)         #must test top right and bottom right
                shift_collides_corner2 = (self.image.get_width() - players_collides_grip, self.image.get_height() - players_collides_grip)

            #if there is not a wall, then go forward
            if not player_collide[int((self.pos[0] - X_map_shift + shift_collides_corner1[0]) + movingVect[0]) //64][int((self.pos[1] - Y_map_shift + shift_collides_corner1[1]) + movingVect[1]) //64]:
                if not player_collide[int((self.pos[0] - X_map_shift + shift_collides_corner2[0]) + movingVect[0]) //64][int((self.pos[1] - Y_map_shift + shift_collides_corner2[1]) + movingVect[1]) //64]:
                    self.pos = (self.pos[0] + movingVect[0], self.pos[1] + movingVect[1], self.pos[2], self.pos[3])

    def move_pushed(self):
        self.speed_multiplier = 2
        self.move(False)
        self.speed_multiplier = 0
        self.pushed_left_distance = self.pushed_left_distance - 2* global_player_speed
        if self.pushed_left_distance < 0:
            self.pushed_left_distance = 0
            self.pushed = False

    def set_bomb(self, tileX, tileY, left_time = exploding_time, free_bomb = False):
        if self.alive:
            if self.can_place_bombs:
                if len(self.bomb_stock) > 0 or free_bomb:        #if player has at least 1 bomb left in stock
                    if not Is_a_bomb[tileX][tileY]:
                        if not player_collide[tileX][tileY]:
                            for player in Players:
                                if not player.player_number == self.player_number:
                                    if player.alive:
                                        if round((player.pos[0] + 32 - player.image_shift[0] - X_map_shift) //64) == tileX and round((player.pos[1] + 32 - player.image_shift[1] - Y_map_shift) //64) == tileY:
                                            break
                            solid = False
                            if self.punch == 20 and self.key_pressing[6]:
                                self.bombs_placed.append(GameObject(Models[1][self.bomb_stock[0]], tileX, tileY, 1, self.bomb_stock[0], solid, left_time, True, self.direction))
                            else:
                                self.bombs_placed.append(GameObject(Models[1][self.bomb_stock[0]], tileX, tileY, 1, self.bomb_stock[0], solid, left_time))
                                Is_a_bomb[tileX][tileY] = True
                            if not free_bomb:
                                del self.bomb_stock[0]

    def Use_bonus(self):
        if self.alive:
            if self.bonus == 4:         #line bomb
                directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
                direction = directions[self.direction]
                for range_bomb in range(1, len(self.bomb_stock)):
                    tileX = round((self.pos[0] + 32 - self.image_shift[0] - X_map_shift) //64) + direction[0]*range_bomb
                    tileY = round((self.pos[1] + 32 - self.image_shift[1] - Y_map_shift) //64) + direction[1]*range_bomb
                    if tileX < 1:
                        tileX = 1
                    elif tileX > choosed_map_dimensions[0] - 2:
                        tileX = choosed_map_dimensions[0] - 2
                    if tileY < 1:
                        tileY = 1
                    elif tileY > choosed_map_dimensions[1] - 2:
                        tileY = choosed_map_dimensions[1] - 2
                    self.set_bomb(tileX, tileY)
            elif self.bonus == 6:         #push
                if self.push_cooldown == 0:
                    directions = [(0, -32), (0, 32), (-32, 0), (32, 0)]
                    direction = directions[self.direction]
                    checking_center = [self.pos[0] + direction[0], self.pos[1] + direction[1]]
                    Push_is_successfull = False
                    for player in Players:
                        if not player.player_number == self.player_number:
                            if player.alive:
                                if player.pos[0] > checking_center[0] - 32 and player.pos[1] < checking_center[0] + 32:
                                    if player.pos[1] > checking_center[1] - 32 and player.pos[1] < checking_center[1] + 32:
                                        Players[player.player_number].pushed = True
                                        Players[player.player_number].pushed_left_distance = 64
                                        Players[player.player_number].direction = self.direction
                                        self.push_cooldown = push_cooldown
                                        Push_is_successfull = True
                    if not Push_is_successfull:
                        self.push_cooldown = 300
            elif self.bonus == 16:      #remote bomb
                for num_bomb, bomb in enumerate(self.bombs_placed):
                    if bomb.number == 6:
                        bomb.despawn(self.player_number, num_bomb)
                        bomb_explode(self, bomb)

    def Use_punch(self):
        if self.alive:
            if self.punch == 18:      #power glove
                directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
                direction = directions[self.direction]
                tileX = round((self.pos[0] + 32 - self.image_shift[0] - X_map_shift) //64) + direction[0]
                tileY = round((self.pos[1] + 32 - self.image_shift[1] - Y_map_shift) //64) + direction[1]
                if not self.lifting_bomb:
                    if Is_a_bomb[tileX][tileY]:
                        for player in Players:
                            for num_bomb, bomb in enumerate(player.bombs_placed):
                                if bomb.tileX == tileX and bomb.tileY == tileY:
                                    screen.blit(mapImg, bomb.pos, [bomb.pos[0] - X_map_shift, bomb.pos[1] - Y_map_shift, bomb.pos[2], bomb.pos[3]])
                                    Is_a_bomb[tileX][tileY] = False
                                    player_collide[tileX][tileY] = False
                                    self.lifting_bomb = True
                                    Players[player.player_number].bombs_placed[num_bomb].sliding = False
                                    Players[player.player_number].bombs_placed[num_bomb].lifted = True
                                    Players[player.player_number].bombs_placed[num_bomb].lifted_by = self.player_number
                                    break
            elif self.punch == 19:      #bonus punch
                directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
                direction = directions[self.direction]
                tileX = round((self.pos[0] + 32 - self.image_shift[0] - X_map_shift) //64) + direction[0]
                tileY = round((self.pos[1] + 32 - self.image_shift[1] - Y_map_shift) //64) + direction[1]
                if Is_a_bomb[tileX][tileY]:
                    for player in Players:
                        for num_bomb, bomb in enumerate(player.bombs_placed):
                            if bomb.tileX == tileX and bomb.tileY == tileY:
                                Players[player.player_number].bombs_placed[num_bomb].sliding = True
                                Players[player.player_number].bombs_placed[num_bomb].sliding_direction = self.direction
                                Is_a_bomb[tileX][tileY] = False
                                player_collide[tileX][tileY] = False
                                break

    def Infected(self, infection):
        if infection == 0:
            self.can_place_bombs = False
        elif infection == 1:
            self.must_place_bombs = True
            self.time_before_place_bomb = random.randint(0, infections_time)
        elif infection == 2:    #Teleport the player to another player
            player_teleport_to = random.randint(1, len(Players) -1)
            if player_teleport_to == self.player_number:
                player_teleport_to = 0
            self.pos = Players[player_teleport_to].pos
        elif infection == 3:
            self.slowed = True
        elif infection == 4:
            self.boosted = True
        elif infection == 5:
            self.inversed_controls = True
        elif infection == 6:
            self.must_walk = True
        self.infections_left_time = infections_time

class text:
    def __init__(self, font_size, text, text_color):
        self.font_size = font_size
        self.text = text
        self.textColor = text_color
        self.textFont = pygame.font.Font(None, self.font_size)
        self.image = self.textFont.render(self.text, True, pygame.Color(self.textColor))

    def new_text(self, Text, color = None):
        if not color == None:
            self.textColor = color
        self.text = Text
        self.image = self.textFont.render(self.text, True, pygame.Color(self.textColor))

    def new_font(self, font_size = None):
        if not font_size == None:
            self.font_size = font_size
        self.textFont = pygame.font.Font(None, self.font_size)
        self.new_text(self.text)

    def Write_text(self, Text, Xpos, Ypos, color = "#000000", font_size = None, BlitSurface = screen):
        self.text = Text
        self.textColor = color
        self.new_font(font_size)
        if Xpos == None:    #set text in center
            Xpos = BlitSurface.get_width()/2 - self.image.get_width()/2
        if Ypos == None:    #set text in center
            Ypos = BlitSurface.get_height()/2 - self.image.get_height()/2
        BlitSurface.blit(self.image, [Xpos, Ypos, self.image.get_width(), self.image.get_height()], [0, 0, self.image.get_width(), self.image.get_height()])

class fire:
    def __init__(self, tileX, tileY):
        self.tileX = tileX
        self.tileY = tileY
        self.pos = [tileX*64 + X_map_shift, tileY*64 + Y_map_shift, 64, 64]
        self.fire_lvl = 0
        self.fire_step = 0      #fire_step / fire_time : from 0 to 5 : fire lvl : 0, 1, 2, 2, 1, 0

    def burn(self, num_flame):
        self.fire_step = self.fire_step + 1
        fire_life_time = int(self.fire_step / fire_time)
        if fire_life_time == 6:
            Fires_to_del.append(num_flame)
            Is_a_bomb[self.tileX][self.tileY] = False
        else:
            if fire_life_time < 3:
                self.fire_lvl = fire_life_time
            else:
                self.fire_lvl = -(fire_life_time -3) +2
            if fire_life_time > 3 - flame_heat and fire_life_time < 4 + flame_heat:
                flame_kills_players(self.tileX, self.tileY, self)

#Load Textures into Models
Models = [[], [], [], [], [], [], [], [], []]
#image_type :[[breakable walls(0)], [bombs(1)], [fire(2)], [bonus(3)], [players(4)], [floors(5)], [map walls(6)], [unbreakable walls(7)], [mouse moves(8)]
images_names_list = [["breakable_wall 0.png"],      #breakable walls(0)
["basic bomb.png", "pierce bomb.png", "bouncing bomb.png", "p bomb.png", "dangerous bomb.png", "mine.png", "remote bomb.png", "hiden_mine.png"],    #bombs(1)
["fire 0.png", "fire 1.png", "fire 2.png"],         #fire(2)
["bonus fire up.png", "bonus full fire.png", "bonus fire down.png", "bonus bomb up.png", "bonus line bomb.png", "bonus bomb down.png", "bonus push.png",    #bonus(3)
"bonus speed up.png", "bonus speed down.png", "bonus bouncing bomb.png", "bonus pierce bomb.png", "bonus skull.png", "bonus p bomb.png", "bonus mine.png",
"bonus radioactive.png", "bonus dangerous bomb.png", "bonus remote bomb.png", "bonus devil.png", "bonus power glove.png", "bonus punch.png", "bonus bomb kick.png"],
#["player 1.png", "player 2.png", "player 3.png", "player 4.png"],   #players(4)
[["player 1 img 1.png", "player 1 img 2.png", "player 1 img 3.png"], ["player 2 img 1.png", "player 2 img 2.png", "player 2 img 3.png"],    #player(4)
["player 3 img 1.png", "player 3 img 2.png", "player 3 img 3.png"], ["player 4 img 1.png", "player 4 img 2.png", "player 4 img 3.png"]],
["floor 0-0.png", "floor 1.png", "floor 2.png", "floor 0-1.png"],   #floors(5)
["map_wall 0.png", "map_wall 1.png", "map_wall 2.png"],             #map walls(6)
["unbreakable_wall 0.png", "unbreakable_wall 1.png", "unbreakable_wall 2.png", "unbreakable_wall 3.png"]]   #unbreakable walls(7)
for image_type_number, image_type in enumerate(images_names_list):
    for num_image, image_name in enumerate(image_type):
        if image_type_number == 4:      #players
            Models[image_type_number].append([])
            for player_image_name in image_name:
                Models[image_type_number][num_image].append(pygame.image.load(path + "images/" + player_image_name).convert_alpha())
        else:
            Models[image_type_number].append(pygame.image.load(path + "images/" + image_name).convert_alpha())
for image_name in ["mouse moves0.png", "mouse moves1.png", "mouse moves2.png", "mouse moves3.png"]:
    Models[8].append(pygame.image.load(path + "images/" + image_name).convert())
for image_name in ["mouse moves0_selected.png", "mouse moves1_selected.png", "mouse moves2_selected.png", "mouse moves3_selected.png"]:
    Models[8].append(pygame.image.load(path + "images/" + image_name).convert_alpha())

background_menu = pygame.image.load(path + "images/background.png").convert()
arrow_right = pygame.image.load(path +"images/arrow_right.png").convert_alpha()
arrow_left = pygame.image.load(path +"images/arrow_left.png").convert_alpha()
back_arrow = pygame.image.load(path + "images/arrow back icon.png").convert_alpha()
green_check = pygame.image.load(path + "images/green check icon.png").convert_alpha()
mouse_cursor = pygame.image.load(path +"images/mouse cursor_test.png").convert()
replay = pygame.image.load(path + "images/replay icon.png").convert_alpha()
mouse_cursor.set_colorkey((255, 0, 0))
Text = text(72, "", "#000000")

Saves = []
for num_save in range(1, 10):
    try:
        Save = open("saves/SAVE " + str(num_save) + ".txt", 'r')
        Saves.append(Save.read())
    except FileNotFoundError:
        Saves.append(None)

def Set_map_settings(options):
    global global_player_speed, players_size_collides, exploding_time, starting_bomb_amount, starting_bomb_max_range, ms_per_tick
    global fire_time, flame_heat, bombs_sliding_speed, push_cooldown, infections_time, speed_infection_slowed, speed_infection_boosted
    (global_player_speed, players_size_collides, exploding_time, starting_bomb_amount, starting_bomb_max_range, ms_per_tick, fire_time, flame_heat, bombs_sliding_speed,
    push_cooldown, infections_time, speed_infection_slowed, speed_infection_boosted) = options

def Uncompress_Save(Save, UncompressBonus = True, UncompressOptions = True):
    str_choosed_map_dimensions, choosed_floor, choosed_map_wall, str_map_objects, choosed_bonus_amount, options = Save.split("///")
    #creating lists and integers from strings
    choosed_map_dimensions = ["", ""]       #transforms "[Xmap, Ymap]" into [Xmap, Ymap]
    choosed_map_dimensions[0], choosed_map_dimensions[1] = str_choosed_map_dimensions.split("/")
    for axis in [0, 1]:
        choosed_map_dimensions[axis] = int(choosed_map_dimensions[axis])

    choosed_floor = int(choosed_floor)      #transforms "choosed_floor" into choosed_floor
    choosed_map_wall = int(choosed_map_wall)        #transforms "choosed_map_wall" into choosed_map_wall

    map_objects = list(str_map_objects.split("//"))     #transforms str_map_objects into map_objects
    for num_object in range(len(map_objects)):
        map_objects[num_object] = list(map_objects[num_object].split("/"))
        for num_object_info in range(len(map_objects[num_object])):
            map_objects[num_object][num_object_info] = int(map_objects[num_object][num_object_info])
    if UncompressBonus:     #Don't need to transform choosed_bonus_amount for the map icon
        choosed_bonus_amount = list(choosed_bonus_amount.split("/"))
        for num_bonus_amount in range(len(choosed_bonus_amount)):
            choosed_bonus_amount[num_bonus_amount] = int(choosed_bonus_amount[num_bonus_amount])
    if UncompressOptions:
        options = list(options.split("/"))
        for num_option in range(len(options)):
            if "." in options[num_option]:
                options[num_option] = float(options[num_option])
            else:
                options[num_option] = int(options[num_option])
    return choosed_map_dimensions, choosed_floor, choosed_map_wall, map_objects, choosed_bonus_amount, options

map_icons = [None, None, None, None, None, None, None, None, None]
def generate_maps_icons():
    for num_map_icons, Save in enumerate(Saves):
        if Save == None:
            map_icon = pygame.Surface((152, 104))
            Text.Write_text("Sauvegarde", 12, 20, "#FF0000", 32, map_icon)
            Text.Write_text("vide", 54, 61, "#FF0000", 32, map_icon)
        else:
            choosed_map_dimensions, choosed_floor, choosed_map_wall, map_objects, choosed_bonus_amount, options = Uncompress_Save(Save, False, False)

            #creating map icon
            map_icon = pygame.Surface((choosed_map_dimensions[0]*8, choosed_map_dimensions[1]*8))

              #floor
            reduced_floor = reduce_image(Models[5][choosed_floor])
            for Y in range(choosed_map_dimensions[1]):
                for X in range(choosed_map_dimensions[0]):
                    map_icon.blit(reduced_floor, [X*8, Y*8, 8, 8], [0, 0, 8, 8])

              #map_walls
            reduced_map_wall = reduce_image(Models[6][choosed_map_wall])
            for Y in range(choosed_map_dimensions[1]):
                for X in range(choosed_map_dimensions[0]):
                    if X == 0 or Y == 0 or X == choosed_map_dimensions[0] - 1 or Y == choosed_map_dimensions[1] - 1:
                        map_icon.blit(reduced_map_wall, [X*8, Y*8, 8, 8], [0, 0, 8, 8])

              #objects
            for object in map_objects:      #object : [type(0), num model(1), tileX(2), tileY(3)]
                if object[0] == 4:  #player
                    reduced_image = reduce_image(Models[object[0]][object[1]][2])
                else:
                    reduced_image = reduce_image(Models[object[0]][object[1]])
                map_icon.blit(reduced_image, [object[2]*8 + int((8 - reduced_image.get_width()) /2), object[3]*8 + int((8 - reduced_image.get_height()) /2), 8, 8], [0, 0, 8, 8])
        centered_map_icon = pygame.Surface((152, 104))
        centered_map_icon.blit(map_icon, [76 - map_icon.get_width()/2, 52 - map_icon.get_height()/2, map_icon.get_width(), map_icon.get_height()], [0, 0, map_icon.get_width(), map_icon.get_height()])
        map_icons[num_map_icons] = centered_map_icon

def map_average_8px8p(image, startingX, startingY):        #calculate RGBA value average in a 8x8 px square in an image
    pixels = []
    for Y in range(startingY, startingY + 8):
        for X in range(startingX, startingX + 8):
            pixels.append(image.get_at((X, Y)))
    average = [0, 0, 0, 0]
    for RGBA in range(4):
        for pixel in pixels:
            average[RGBA] = average[RGBA] + pixel[RGBA]
        average[RGBA] = round(average[RGBA] / 64)
    return average

def reduce_image(image):    #reduce 64x64 px image (1:8)
    reduced_image = pygame.Surface((int(image.get_width() /8), int(image.get_height() /8)))
    for Y in range(int(image.get_height() /8)):
        for X in range(int(image.get_width()/8)):
            reduced_image.set_at((X, Y), map_average_8px8p(image, X*8, Y*8))
    return reduced_image

def LpM2_Change_Player(new_player):    #Used in Loop_Menu2 : Change controls for next/previous Player   new_player can be 0, 1, 2 or 3 (Player 1, 2, 3 or 4)
    screen.blit(background_menu, [613, 170, 140, 34], [613, 170, 140, 34])      #Erase "Player X"
    Player_number = str(Player_controls + 1)
    Text_to_write = "Joueur " + Player_number
    color = Player_color[Player_controls]
    Text.Write_text(Text_to_write, 613, 170, color, 48)
    LpM2_Refresh_Key_Buttons_Look()

Selected_button = None
def LpM2_Refresh_Key_Buttons_Look():        #Used in Loop_Menu2 : Refresh key buttons looks
    for key_num in range(7):
        key_surface = pygame.Surface((100, 70))
        if Selected_button == key_num:
            key_surface.fill((76, 24, 230, 255), [5, 5, 90, 60])
            color = "#000000"
        else:
            color = Player_color[Player_controls]
        lines = Commands_names[Player_controls][key_num].split(" ")
        if len(lines) == 1:
            Text.Write_text(lines[0], None, 23, color, 32, key_surface)
            if Text.image.get_width() > 90:
                key_surface = pygame.Surface((100, 70))
                if Selected_button == key_num:
                    key_surface.fill((76, 24, 230, 255), [5, 5, 90, 60])
                Text.Write_text(lines[0], None, 23, color, 26, key_surface)
        else:
            Text.Write_text(lines[0], None, 11, color, 32, key_surface)
            Text.Write_text(lines[1], None, 35, color, 32, key_surface)
        screen.blit(key_surface, [195*key_num + 47, 350, 100, 100], [0, 0, 100, 100])

def LpWfS_key_pressed(player):
    global Loop_Waiting_for_Start, Starting_and_animation
    screen.fill((200, 200, 200, 255), [LpWfS_Text_coordinates[player][0][0], LpWfS_Text_coordinates[player][0][1], 159, 50])    #Erase "En attente du joueur X
    Text.Write_text("Joueur " + str(player + 1), LpWfS_Text_coordinates[player][2][0], LpWfS_Text_coordinates[player][0][1], Player_color[player], 36)
    Text.Write_text("prêt !", LpWfS_Text_coordinates[player][3][0], LpWfS_Text_coordinates[player][1][1], Player_color[player], 36)
    Players_ready[player] = True    #player is ready
    Loop_Waiting_for_Start = False      #Tests if all players are ready
    for ready in Players_ready:
        if not ready:
            Loop_Waiting_for_Start = True
            Starting_and_animation = True

choosed_map_dimensions, choosed_floor, choosed_map_wall, map_objects, choosed_bonus_amount = None, None, None, None, None
breakable = []
player_collide = []
def generate_collisions_maps():
    #Uncompress Save
    global choosed_map_dimensions, choosed_floor, choosed_map_wall, map_objects, choosed_bonus_amount
    choosed_map_dimensions, choosed_floor, choosed_map_wall, map_objects, choosed_bonus_amount, options = Uncompress_Save(Saves[Map])
    if Use_map_settings:
        Set_map_settings(options)
    #Generating collide for players and destructible test
    #collision map (collide list) : map walls       breakable : full empty (False)
    global player_collide, breakable       #collides : True if there is a wall, else False
    for X in range(choosed_map_dimensions[0]):
        player_collide.append([])
        breakable.append([])
        for Y in range(choosed_map_dimensions[1]):
            if X == 0 or X == choosed_map_dimensions[0] - 1 or Y == 0 or Y==choosed_map_dimensions[1] - 1:
                player_collide[X].append(True)
            else:
                player_collide[X].append(False)
            breakable[X].append(False)
    #Add objects
    for object in map_objects:
        if object[0] == 7:      #unbreakable wall
            player_collide[object[2]][object[3]] = True       #breakable is already False
        elif object[0] == 0:    #breakable wall
            player_collide[object[2]][object[3]] = True
            breakable[object[2]][object[3]] = True
    #it is now possible to call player_collide[X][Y] to know if there is a wall
    #it is now possible to call breakable[X][Y] to know if a case can be breaked
        #Note : X and Y are tiles and not coordinates

Y_map_shift = 0
X_map_shift = 0
def generate_map_texture():    #generates floor, map_walls, and unbreakable walls
    mapImg = pygame.Surface((64*choosed_map_dimensions[0], 64*choosed_map_dimensions[1]))
    #generating floor
    if choosed_floor == 0:  #alternate floor 0-0 and 0-1
        if choosed_map_dimensions[1] % 2 == 0:
            floor_num = 3
        else:
            floor_num = 0
        for X in range(0, 64*choosed_map_dimensions[0], 64):
            if choosed_map_dimensions[1] % 2 == 0:
                if floor_num == 0:
                    floor_num = 3
                else:
                    floor_num = 0
            for Y in range(0, 64*choosed_map_dimensions[1], 64):
                mapImg.blit(Models[5][floor_num], (X, Y))
                if floor_num == 0:
                    floor_num = 3
                else:
                    floor_num = 0
    else:
        for X in range(0,64*choosed_map_dimensions[0],64):
            for Y in range(0,64*choosed_map_dimensions[1],64):
                mapImg.blit(Models[5][choosed_floor],(X,Y))
    #generating map_walls
    for X in range(0, 64*choosed_map_dimensions[0], 64):
        for Y in range(0, 64*choosed_map_dimensions[1], 64):
            if X == 0 or X == (choosed_map_dimensions[0] -1)*64 or Y == 0 or Y == (choosed_map_dimensions[1] -1)*64:
                mapImg.blit(Models[6][choosed_map_wall], (X, Y))
    #generating unbreakable walls
    for object in map_objects:
        if object[0] == 7:  #unbreakable wall
            mapImg.blit(Models[7][object[1]], [object[2]*64, object[3]*64, 64, 64], [0, 0, 64, 64])
    screen.blit(mapImg, [0, 0, mapImg.get_width(), mapImg.get_height()], [0, 0, mapImg.get_width(), mapImg.get_height()])
    #generating breakable walls
    breakable_walls = []
    for object in map_objects:
        if object[0] == 0:  #breakable wall
            breakable_walls.append(object)
    #changing Y_map_shift
    global X_map_shift, Y_map_shift
    X_map_shift = 0
    Y_map_shift = 0
    if Player_using_mouse == None or not Player_using_mouse < Player_number + 1:
        X_map_shift = round((1366 - 64*choosed_map_dimensions[0]) /2)
    else:
        X_map_shift = (1366 - 64*choosed_map_dimensions[0] - 138) /2    #138 is mouse moves image is width (128) + distance betwin it and mapImg
    if choosed_map_dimensions[1] == 13:
        Y_map_shift = -32

    return mapImg, breakable_walls

def create_mouse_moves(mousePos = None):    #creates mouse_moves image
    if mousePos == None:
        num_mouse_move_selected = None
    else:
        vectMousePos = (mouse_pos[0] - pos_mouse_moves[0] - 64, mouse_pos[1] - pos_mouse_moves[1] - Y_map_shift - 64)     #Vector : mouse moves image middle --> mouse position
        vectMousePosNorm = sqrt(vectMousePos[0]**2 + vectMousePos[1]**2)
        if vectMousePosNorm < 13:
            num_mouse_move_selected = None
        else:
            if vectMousePos[0] > vectMousePos[1]:   #direction is top or right
                if vectMousePos[0] > - vectMousePos[1]:     #direction is right
                    if Players[Player_using_mouse].inversed_controls:
                        num_mouse_move_selected = 2
                    else:
                        num_mouse_move_selected = 3
                    mouse_cursor_shift = (64, 0)
                else:                                       #direction is top
                    if Players[Player_using_mouse].inversed_controls:
                        num_mouse_move_selected = 1
                    else:
                        num_mouse_move_selected = 0
                    mouse_cursor_shift = (0, 0)
            else:                                   #direction is bottom or left
                if vectMousePos[1] > - vectMousePos[0]:     #direction is bottom
                    if Players[Player_using_mouse].inversed_controls:
                        num_mouse_move_selected = 0
                    else:
                        num_mouse_move_selected = 1
                    mouse_cursor_shift = (0, 64)
                else:                                       #direction is left
                    if Players[Player_using_mouse].inversed_controls:
                        num_mouse_move_selected = 3
                    else:
                        num_mouse_move_selected = 2
                    mouse_cursor_shift = (0, 0)
            Players[Player_using_mouse].direction = num_mouse_move_selected

    mouse_moves = pygame.Surface((128, 128))
    mouse_moves.fill((255, 0, 0))       #make mouse_moves fully transparent
    mouse_moves.set_colorkey((255, 0, 0))
    for num_mouse_move in range(4):
        next_mouse_move_image = pygame.Surface((Models[8][num_mouse_move].get_width(), Models[8][num_mouse_move].get_height()))
        if num_mouse_move_selected == num_mouse_move:
            next_mouse_move_image.blit(mouse_cursor, (mousePos[0] - pos_mouse_moves[0] - mouse_cursor_shift[0] - 86, mousePos[1] - pos_mouse_moves[1] - mouse_cursor_shift[1] - Y_map_shift - 86))
            next_mouse_move_image.blit(Models[8][num_mouse_move + 4], [0, 0, next_mouse_move_image.get_width(), next_mouse_move_image.get_height()], [0, 0, next_mouse_move_image.get_width(), next_mouse_move_image.get_height()])
        else:
            next_mouse_move_image = Models[8][num_mouse_move].copy()
        next_mouse_move_image.set_colorkey((255, 0, 0))
        if num_mouse_move == 0 or num_mouse_move == 1:
            mouse_moves.blit(next_mouse_move_image, [0, num_mouse_move*64, 128, 64], [0, 0, 128, 64])
        else:
            mouse_moves.blit(next_mouse_move_image, [(num_mouse_move - 2)*64, 0, 64, 128], [0, 0, 64, 128])
    return mouse_moves

def move_mouse_cursor_on_mouse_moves():     #if mouse cursor is not on mouse moves circle, function moves it on mouse moves circle
    if not Player_using_mouse == None:
        if Player_using_mouse < Player_number:
            global mouse_pos
            vectMousePos = (mouse_pos[0] - pos_mouse_moves[0] - 64, mouse_pos[1] - pos_mouse_moves[1] - Y_map_shift - 64)     #Vector : mouse moves image middle --> mouse position
            vectMousePosNorm = sqrt(vectMousePos[0]**2 + vectMousePos[1]**2)
            if vectMousePosNorm > 64:
                newVectMousePos = (vectMousePos[0] /(vectMousePosNorm /64), vectMousePos[1] /(vectMousePosNorm /64))
                newMousePos = (newVectMousePos[0] + (pos_mouse_moves[0] + 64), newVectMousePos[1] + (pos_mouse_moves[1] + Y_map_shift + 64))
                pygame.mouse.set_pos(newMousePos)
                Players[Player_using_mouse].speed_multiplier = 1
                set_playing_Animation(Player_using_mouse, True)
            else:
                newMousePos = mouse_pos
                if vectMousePosNorm > 43:
                    Players[Player_using_mouse].speed_multiplier = 1
                    set_playing_Animation(Player_using_mouse, True)
                elif vectMousePosNorm > 32:
                    Players[Player_using_mouse].speed_multiplier = 0.5
                    set_playing_Animation(Player_using_mouse, True)
                else:
                    set_playing_Animation(Player_using_mouse, False)
                    Players[Player_using_mouse].speed_multiplier = 0
            mouse_pos = newMousePos
            screen.blit(create_mouse_moves(mouse_pos), [pos_mouse_moves[0], pos_mouse_moves[1] + Y_map_shift, 128, 128], [0, 0, 128, 128])

wall_breaked = False
break_flame_loop = False
def bomb_explode(player, bomb):         #bomb_explode(player using bomb, bomb exploding)
    global wall_breaked, break_flame_loop
    if bomb.number == 4:      #dangerous bomb (5x5 square explosion)
        Default_range_explosion_dangerous_bomb = [[bomb.tileX - 2, bomb.tileX + 3], [bomb.tileY - 2, bomb.tileY + 3]]    #((Xmin, Xmax), (Ymin, Ymax))
        range_explosion = Default_range_explosion_dangerous_bomb
        for num_XorY, XorYrange_explosion in enumerate(Default_range_explosion_dangerous_bomb):
            if XorYrange_explosion[0] < 0:
                range_explosion[num_XorY][0] = 0
            if XorYrange_explosion[1] > choosed_map_dimensions[num_XorY]:
                range_explosion[num_XorY][1] = choosed_map_dimensions[num_XorY]
        for fire_tileX in range(range_explosion[0][0], range_explosion[0][1]):
            for fire_tileY in range(range_explosion[1][0], range_explosion[1][1]):
                flame_effect(fire_tileX, fire_tileY, bomb)
    else:
        if bomb.number == 3:      #p bomb
            fire_max_range = 19
        else:
            fire_max_range = Players[player.player_number].bombs_max_range
        for direction in [(0, -1), (0, 1), (-1, 0), (1, 0)]:          #top, bottom, left, right
            break_flame_loop = False
            for flame_range in range(fire_max_range):
                if break_flame_loop:
                    break_flame_loop = False
                    break
                else:
                    fire_tileX = bomb.tileX + (direction[0]*flame_range)
                    fire_tileY = bomb.tileY + (direction[1]*flame_range)
                    flame_effect(fire_tileX, fire_tileY, bomb)
    if wall_breaked:
        wall_breaked = False
        global mapImg
        mapImg = mapImg_unbreakable.copy()
        for object in breakable_walls:
            mapImg.blit(Models[0][object[1]], [object[2]*64, object[3]*64, 64, 64], [0, 0, 64, 64])
        screen.blit(mapImg, [X_map_shift, Y_map_shift, mapImg_unbreakableWidth, mapImg_unbreakableHeight], [0, 0, mapImg_unbreakableWidth, mapImg_unbreakableHeight])

def flame_effect(fire_tileX, fire_tileY, bomb):     #place a flame at X and Y tiles
    global wall_breaked, break_flame_loop
    Can_destroy_bonus = True
    if In_fire[fire_tileX][fire_tileY]:         #if there is already a flame, delete this flame to avoid flame superposition. It also avoids to destroy bonus where another bomb just exploded
        for num_flame, flame in enumerate(Fire):
            if flame.tileX == fire_tileX and flame.tileY == fire_tileY:
                Can_destroy_bonus = False
                In_fire[flame.tileX][flame.tileY] = False
                del Fire[num_flame]
                break
    if Is_a_bomb[fire_tileX][fire_tileY]:       #if there is a bomb, activate this bomb
        for num_player in range(len(Players)):
            for num_bomb, bomb in enumerate(Players[num_player].bombs_placed):
                if bomb.tileX == fire_tileX and bomb.tileY == fire_tileY:
                    bomb.despawn(num_player, num_bomb)
                    bomb_explode(Players[num_player], bomb)
    if Can_destroy_bonus:
        if Is_a_bonus[fire_tileX][fire_tileY]:
            for num_bonus, bonus in enumerate(Showing_bonus):
                if bonus.tileX == fire_tileX and bonus.tileY == fire_tileY:
                    Bonus_to_del.append(num_bonus)
            Is_a_bonus[fire_tileX][fire_tileY] = False
    if player_collide[fire_tileX][fire_tileY]:      #if there is a wall, break this wall if it is breakable and stop the fire
        if breakable[fire_tileX][fire_tileY]:
            Fire.append(fire(fire_tileX, fire_tileY))
            In_fire[fire_tileX][fire_tileY] = True
            break_breakable_wall(fire_tileX, fire_tileY)
            wall_breaked = True
            if not bomb.number == 1:
                break_flame_loop = True
        else:
            break_flame_loop = True
    else:
        Fire.append(fire(fire_tileX, fire_tileY))
        In_fire[fire_tileX][fire_tileY] = True

Winner = None
def flame_kills_players(tileX, tileY, fire):
    if not dev_mode:
        for player in Players:
            player_tileX = round((player.pos[0] + 32 - player.image_shift[0] - X_map_shift) //64)
            player_tileY = round((player.pos[1] + 32 - player.image_shift[1] - Y_map_shift) //64)
            if tileX == player_tileX and tileY == player_tileY:
                Players[player.player_number].alive = False
                players_alive = 0
                for player in Players:
                    if player.alive:
                        players_alive = players_alive + 1
                        winner = player.player_number
                if players_alive == 1:
                    global Winner, EndedGameLoop, GameLoop
                    Winner = winner
                    EndedGameLoop = True
                    GameLoop = False

def break_breakable_wall(tileX, tileY):
    #update breakable walls
    for num_object, object in enumerate(breakable_walls):
        if object[2] == tileX and object[3] == tileY:       #Object : type(0), number(1), tileX(2), tileY,(3)
            breakable_walls_to_del = num_object
            if len(Next_bonus) > 0:     #avoid bug
                if not Next_bonus[0] == None:
                    Showing_bonus.append(GameObject(Models[3][Next_bonus[0]], object[2], object[3], 3, Next_bonus[0]))
                    Is_a_bonus[object[2]][object[3]] = True
            del Next_bonus[0]
            break
    del breakable_walls[breakable_walls_to_del]
    #update player_collide and breakable
    player_collide[tileX][tileY] = False
    breakable[tileX][tileY] = False

def reload_player_bomb_stock(num_player):
    bomb_type = Players[num_player].bomb_type
    new_bomb_stock = []
    len_bomb_stock = Players[num_player].MaxBomb_amount - len(Players[num_player].bombs_placed)
    if len_bomb_stock > 0:
        first_bomb_Found = False
        for bomb in Players[num_player].bombs_placed:
            if Players[num_player].first_bomb == bomb.number:
                new_bomb_stock = [Players[num_player].bomb_type]
                first_bomb_Found = True
                break
        if not first_bomb_Found:
            new_bomb_stock = [Players[num_player].first_bomb]
        for bomb in range(len_bomb_stock - 1):
            new_bomb_stock.append(Players[num_player].bomb_type)
    Players[num_player].bomb_stock = new_bomb_stock

def players_take_bonus():
    for player in Players:
        #Calculate a round of player tile coordinates
        player_TileXY = (round((player.pos[0] + 32 - player.image_shift[0] - X_map_shift) //64), round((player.pos[1] + 32 - player.image_shift[1] - Y_map_shift) //64))
        for num_bonus, bonus in enumerate(Showing_bonus):
            if bonus.tileX == player_TileXY[0] and bonus.tileY == player_TileXY[1]:
                Bonus_to_del.append(num_bonus)
                Is_a_bonus[bonus.tileX][bonus.tileY] = False
                if bonus.number == 0:       #bonus fire up
                    if not player.bombs_max_range > 7:  #maximum fire range
                        Players[player.player_number].bombs_max_range = Players[player.player_number].bombs_max_range + 1
                elif bonus.number == 1:     #bonus full fire
                    Players[player.player_number].bombs_max_range = 15
                elif bonus.number == 2:     #bonus fire down
                    if not player.bombs_max_range == 2:
                        Players[player.player_number].bombs_max_range = Players[player.player_number].bombs_max_range - 1
                elif bonus.number == 3:     #bonus bomb up
                    if not player.MaxBomb_amount > 7:
                        Players[player.player_number].MaxBomb_amount = Players[player.player_number].MaxBomb_amount + 1
                        reload_player_bomb_stock(player.player_number)
                elif bonus.number == 4:     #bonus line bomb
                    Players[player.player_number].bonus = 4
                elif bonus.number == 5:
                    if not player.MaxBomb_amount == 1:
                        Players[player.player_number].MaxBomb_amount = Players[player.player_number].MaxBomb_amount - 1
                        reload_player_bomb_stock(player.player_number)
                elif bonus.number == 6:     #bonus push
                    Players[player.player_number].bonus = 6
                elif bonus.number == 7:     #bonus speed up
                    Players[player.player_number].bonus_speed = player.bonus_speed + 0.1
                elif bonus.number == 8:     #bonus speed down
                    Players[player.player_number].bonus_speed = player.bonus_speed - 0.1
                elif bonus.number == 9:     #bonus bouncing bomb
                    Players[player.player_number].bomb_type = 2
                    Players[player.player_number].first_bomb = 2
                    reload_player_bomb_stock(player.player_number)
                elif bonus.number == 10:    #bonus pierce bomb
                    Players[player.player_number].bomb_type = 1
                    Players[player.player_number].first_bomb = 1
                    reload_player_bomb_stock(player.player_number)
                elif bonus.number == 11:    #bonus skull
                    Players[player.player_number].Infected(random.randint(0, 6))
                elif bonus.number == 12:    #bonus p bomb
                    Players[player.player_number].first_bomb = 3
                    reload_player_bomb_stock(player.player_number)
                elif bonus.number == 13:    #bonus mine
                    Players[player.player_number].first_bomb = 5
                    reload_player_bomb_stock(player.player_number)
                elif bonus.number == 14:    #bonus radioactive
                    infections = [0, 1, 2, 3, 4, 5, 6]      #give 3 DIFFERENT infections
                    for inf in range(3):
                        new_infection_number = random.randint(0, len(infections) - 1)
                        new_infection = infections[new_infection_number]
                        Players[player.player_number].Infected(new_infection)
                        del infections[new_infection_number]
                elif bonus.number == 15:    #bonus dangerous bomb
                    Players[player.player_number].first_bomb = 4
                    reload_player_bomb_stock(player.player_number)
                elif bonus.number == 16:    #remote bomb
                    Players[player.player_number].first_bomb = 6
                    reload_player_bomb_stock(player.player_number)
                    Players[player.player_number].bonus = 16
                elif bonus.number == 17:    #bonus devil
                    for player_number in range(len(Players)):
                        Players[player_number].Infected(random.randint(0, 6))
                elif bonus.number == 18:    #bonus power glove
                    Players[player.player_number].punch = 18
                elif bonus.number == 19:    #bonus punch
                    Players[player.player_number].punch = 19
                elif bonus.number == 20:    #bonus bomb kick
                    Players[player.player_number].punch = 20

def get_num_ImgAnimation(step_in_animation):
    if step_in_animation == 0:
        num_ImgAnimation = 0
    elif step_in_animation == 1:
        num_ImgAnimation = 2
    elif step_in_animation == 2:
        num_ImgAnimation = 1
    else:   #if step_in_animation == 3:
        num_ImgAnimation = 2
    return num_ImgAnimation

def set_playing_Animation(player_number, play):
    global Players
    Players[player_number].play_animation = play
    if not play:
        if Players[player_number].animation == 0:
            Players[player_number].animation = 1
        elif Players[player_number].animation == 2:
            Players[player_number].animation = 3

generate_maps_icons()

Loop_Menu1 = True
Loop_Menu2 = False
Loop_Waiting_for_Start = False
Starting_and_animation = False
GameLoop = False
EndedGameLoop = False
Replaying_loop = False
Playing = True
while Playing:
    #Before Loop_Menu1:
    if Loop_Menu1:  #Loop_Menu1 : Map choice
        screen.blit(background_menu, [0, 0, 1366, 768], [0, 0, 1366, 768])
        Text.Write_text("Choix de la carte", 479, 80, "#000000", 72)
        for num_map_icon, map_icon in enumerate(map_icons):
            if num_map_icon < 3:    #First save line
                screen.blit(map_icon, [303 + 303*num_map_icon, 184, map_icon.get_width(), map_icon.get_height()], [0, 0, map_icon.get_width(), map_icon.get_height()])
            elif num_map_icon < 6:  #Second save line
                screen.blit(map_icon, [303 + 303*(num_map_icon - 3), 396, map_icon.get_width(), map_icon.get_height()], [0, 0, map_icon.get_width(), map_icon.get_height()])
            else:                   #Third save line
                screen.blit(map_icon, [303 + 303*(num_map_icon - 6), 608, map_icon.get_width(), map_icon.get_height()], [0, 0, map_icon.get_width(), map_icon.get_height()])
        Map = None
    while Loop_Menu1:
        for event in pygame.event.get():
            if event.type == 12:
                pygame.quit()
                sys.exit()
            if event.type == 5:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[1] > 184 and mouse_pos[1] < 288:       #if clicked on save line 1
                    if mouse_pos[0] > 303 and mouse_pos[0] < 455:       #if clicked on SAVE_1
                        Map = 0
                    elif mouse_pos[0] > 606 and mouse_pos[0] < 758:     #else if clicked on SAVE_2
                        Map = 1
                    elif mouse_pos[0] > 909 and mouse_pos[0] < 1061:    #else if clicked on SAVE_3
                        Map = 2
                elif mouse_pos[1] > 396 and mouse_pos[1] < 500:     #else if clicked on save line 2
                    if mouse_pos[0] > 303 and mouse_pos[0] < 455:       #if clicked on SAVE_4
                        Map = 3
                    elif mouse_pos[0] > 606 and mouse_pos[0] < 758:     #else if clicked on SAVE_5
                        Map = 4
                    elif mouse_pos[0] > 909 and mouse_pos[0] < 1061:    #else if clicked on SAVE_6
                        Map = 5
                elif mouse_pos[1] > 608 and mouse_pos[1] < 712:     #else if clicked on save line 3
                    if mouse_pos[0] > 303 and mouse_pos[0] < 455:       #if clicked on SAVE_7
                        Map = 6
                    elif mouse_pos[0] > 606 and mouse_pos[0] < 758:     #else if clicked on SAVE_8
                        Map = 7
                    elif mouse_pos[0] > 909 and mouse_pos[0] < 1061:    #else if clicked on SAVE_9
                        Map = 8
                if not Map == None:     #if save choosed:
                    if not Saves[Map] == None:
                        Loop_Menu1 = False          #Boucle suivante
                        Loop_Menu2 = True

        pygame.display.update()
        pygame.time.delay(ms_per_tick)

    #Before Loop_Menu2
    if Loop_Menu2:
        screen.blit(background_menu, [0, 0, 1366, 768], [0, 0, 1366, 768])
        Text.Write_text("Choix des contrôles", 439, 80, "#000000", 72)
        Player_controls = 0         #Corresponds to list Commands : [Player 1(0), Player 2(1), Player 3(2), Player 4(3)]
        LpM2_Change_Player(Player_controls)
        screen.blit(arrow_left, [571, 155, 32, 64], [0, 0, 32, 64])
        screen.blit(arrow_right, [763, 155, 32, 64], [0, 0, 32, 64])
        Text.Write_text(str(Player_number) + " joueurs", 1170, 180, "#00FF00", 36)
        Text.Write_text("Monter", 48, 430, "#000000", 40)
        Text.Write_text("Aller à", 246, 430, "#000000", 40)
        Text.Write_text("gauche", 243, 458, "#000000", 40)
        Text.Write_text("Reculer", 442, 430, "#000000", 36)
        Text.Write_text("Aller à", 636, 430, "#000000", 40)
        Text.Write_text("droite", 642, 458, "#000000", 40)
        Text.Write_text("Placer", 834, 430, "#000000", 40)
        Text.Write_text("une", 852, 458, "#000000", 40)
        Text.Write_text("bombe", 832, 486, "#000000", 40)
        Text.Write_text("Touche", 1023, 430, "#000000", 40)
        Text.Write_text("bonus", 1029, 458, "#000000", 40)
        Text.Write_text("Touche", 1218, 430, "#000000", 40)
        Text.Write_text("coup", 1234, 458, "#000000", 40)
        screen.blit(pygame.Surface((186, 70)), [590, 650, 186, 70], [0, 0, 186, 70])        #Use mouse button
        Text.Write_text("Utiliser la souris", 595, 674, "#00FFFF", 32)
        screen.blit(back_arrow, [51, 653, 64, 64], [0, 0, 64, 64])
        screen.blit(green_check, [1251, 653, 64, 64], [0, 0, 64, 64])
    while Loop_Menu2:   #Loop_Menu2 : Controls choice
        for event in pygame.event.get():
            if event.type == 12:
                pygame.quit()
                sys.exit()
            if event.type == 5:
                mouse_pos = pygame.mouse.get_pos()
                Selected_button = None
                if mouse_pos[1] > 155 and mouse_pos[1] < 219:       #if clicked on Player changes arrows Y
                    if mouse_pos[0] > 571 and mouse_pos[0] < 601:       #if clicked on Player change left arrow
                        Player_controls = Player_controls - 1
                        if Player_controls == -1:   # 0 <= Player_controls < Player_number
                            Player_controls = Player_number - 1
                        LpM2_Change_Player(Player_controls)
                    elif mouse_pos[0] > 763 and mouse_pos[0] < 795:     #else if clicked on Player change right arrow
                        Player_controls = Player_controls + 1
                        if Player_controls == Player_number:    # 0 <= Player_controls < Player_number
                            Player_controls = 0
                        LpM2_Change_Player(Player_controls)
                    elif mouse_pos[1] > 180 and mouse_pos[1] < 205:     #else if clicked on player number button Y (X joueurs)
                        if mouse_pos[0] > 1170 and mouse_pos[0] < 1279:     #if player number button clicked
                            Player_number = Player_number + 1
                            if Player_number == 5:
                                Player_number = 2
                            screen.blit(background_menu, [1170, 180, 109, 25], [1170, 180, 109, 25])        #Erase "X joueurs" from screen
                            Text.Write_text(str(Player_number) + " joueurs", 1170, 180, "#00FF00", 36)
                            if Player_controls + 1 > Player_number:
                                Player_controls = 0
                                LpM2_Change_Player(Player_controls)

                elif mouse_pos[1] > 350 and mouse_pos[1] < 420:     #else if clicked on game keys buttons Y
                    if mouse_pos[0] > 47 and mouse_pos[0] < 147:        #if button key go forward pressed (Monter)
                        Selected_button = 0
                        LpM2_Refresh_Key_Buttons_Look()
                    elif mouse_pos[0] > 242 and mouse_pos[0] < 342:     #else if button key go left pressed (Aller à gauche)
                        Selected_button = 1
                        LpM2_Refresh_Key_Buttons_Look()
                    elif mouse_pos[0] > 437 and mouse_pos[0] < 537:     #else if button key go backward pressed (Descendre)
                        Selected_button = 2
                        LpM2_Refresh_Key_Buttons_Look()
                    elif mouse_pos[0] > 632 and mouse_pos[0] < 732:     #else if button key go right pressed (Aller à droite)
                        Selected_button = 3
                        LpM2_Refresh_Key_Buttons_Look()
                    elif mouse_pos[0] > 827 and mouse_pos[0] < 927:     #else if button key place bomb pressed (Placer une bombe)
                        Selected_button = 4
                        LpM2_Refresh_Key_Buttons_Look()
                    elif mouse_pos[0] > 1022 and mouse_pos[0] < 1122:   #else if button key use bonus pressed (Touche bonus)
                        Selected_button = 5
                        LpM2_Refresh_Key_Buttons_Look()
                    elif mouse_pos[0] > 1217 and mouse_pos[0] < 1317:   #else if button key catch pressed (Touche coup)
                        Selected_button = 6
                        LpM2_Refresh_Key_Buttons_Look()

                elif mouse_pos[1] > 650 and mouse_pos[1] < 720:     #else if clicked on button mouse controls Y
                    if mouse_pos[0] > 590 and mouse_pos[0] < 776:       #if button mouse controls clicked (Utiliser la souris)
                        if not Player_using_mouse == None:
                            Commands[Player_using_mouse] = ["", "", "", "", "", "", ""]
                            Commands_names[Player_using_mouse] = ["", "", "", "", "", "", ""]
                        Commands[Player_controls] = ["MOUSE", "MOUSE", "MOUSE", "MOUSE", "MOUSE", "MOUSE", "MOUSE"]
                        Commands_names[Player_controls] = ["Mouse move", "Mouse move", "Mouse move", "Mouse move", "Left click", "Mouse wheel", "Right click"]
                        Player_using_mouse = Player_controls
                        LpM2_Refresh_Key_Buttons_Look()
                    elif mouse_pos[1] > 653 and mouse_pos[1] < 717:     #else if clicked on back arrow/green check Y
                        if mouse_pos[0] > 51 and mouse_pos[0] < 115:        #if back arrow clicked
                            Loop_Menu2 = False
                            Loop_Menu1 = True
                        elif mouse_pos[0] > 1251 and mouse_pos[0] < 1315:   #else if green check clicked
                            LpM2_can_continue = True
                            for player in range(Player_number):
                                for command_number, command in enumerate(Commands[player]):
                                    if command == "":
                                        LpM2_can_continue = False
                                        LpM2_non_ready_player = player
                                    elif command == "MOUSE":
                                        if not player == Player_using_mouse:
                                            LpM2_can_continue = False
                                            LpM2_non_ready_player = player
                                            Commands[player][command_number] = ""
                                            Commands_names[player][command_number] = ""
                            if LpM2_can_continue:
                                Loop_Menu2 = False
                                Loop_Waiting_for_Start = True
                            else:
                                Player_controls = LpM2_non_ready_player
                                LpM2_Change_Player(Player_controls)

            elif event.type == 2:       #key pressed
                if not Selected_button == None:
                    if Player_controls == Player_using_mouse:   #Blocks mouse controls and clavier controls for the same player
                        Player_using_mouse = None
                        for key_num in range(7):
                            Commands[Player_controls][key_num] = ""
                            Commands_names[Player_controls][key_num] = ""

                    Commands[Player_controls][Selected_button] = event.scancode
                    if event.unicode == "" or str.isspace(event.unicode) or event.unicode == "":
                        Commands_names[Player_controls][Selected_button] = pygame.key.name(event.key)
                    else:
                        Commands_names[Player_controls][Selected_button] = event.unicode
                    LpM2_Refresh_Key_Buttons_Look()

        pygame.display.update()
        pygame.time.delay(ms_per_tick)

    #Before Loop_waiting_for_start
    if Loop_Waiting_for_Start:
        screen.fill((200, 200, 200, 255))
        if Player_number == 2:
            LpWfS_Text_coordinates = [[(262, 276), (283, 301), (290, 276), (311, 276)], [(945, 276), (966, 301), (973, 276), (994, 301)]]          #LpWfS_Text_coordinates = [[text player 1], [text player 2]...]
            Players_ready = [False, False]
        elif Player_number == 3:                                                                                                                    #text player 1 : [coordinates "En attente du", coordinates "joueur X", coordinates "Joueur X", coordinates "prêt !"]
            LpWfS_Text_coordinates = [[(262, 138), (283, 163), (290, 138), (311, 163)], [(945, 138), (966, 163), (973, 138), (994, 163)], [(604, 490), (635, 515), (632, 490), (653, 515)]]
            Players_ready = [False, False, False]
        elif Player_number == 4:
            LpWfS_Text_coordinates = [[(262, 138), (283, 163), (290, 138), (311, 163)], [(945, 138), (966, 163), (973, 138), (994, 163)], [(262, 490), (283, 515), (290, 490), (311, 515)], [(945, 490), (966, 515), (973, 490), (994, 515)]]
            Players_ready = [False, False, False, False]

        Text.Write_text("En attente du", LpWfS_Text_coordinates[0][0][0], LpWfS_Text_coordinates[0][0][1], Player_color[0], 36)
        Text.Write_text("joueur 1...", LpWfS_Text_coordinates[0][1][0], LpWfS_Text_coordinates[0][1][1], Player_color[0], 36)
        Text.Write_text("En attente du", LpWfS_Text_coordinates[1][0][0], LpWfS_Text_coordinates[1][0][1], Player_color[1], 36)
        Text.Write_text("joueur 2...", LpWfS_Text_coordinates[1][1][0], LpWfS_Text_coordinates[1][1][1], Player_color[1], 36)
        if Player_number > 2:
            Text.Write_text("En attente du", LpWfS_Text_coordinates[2][0][0], LpWfS_Text_coordinates[2][0][1], Player_color[2], 36)
            Text.Write_text("joueur 3...", LpWfS_Text_coordinates[2][1][0], LpWfS_Text_coordinates[2][1][1], Player_color[2], 36)
            if Player_number == 4:
                Text.Write_text("En attente du", LpWfS_Text_coordinates[3][0][0], LpWfS_Text_coordinates[3][0][1], Player_color[3], 36)
                Text.Write_text("joueur 4...", LpWfS_Text_coordinates[3][1][0], LpWfS_Text_coordinates[3][1][1], Player_color[3], 36)

        screen.blit(back_arrow, [51, 653, 64, 64], [0, 0, 64, 64])
    while Loop_Waiting_for_Start:   #Wait for everyone to be ready
        for event in pygame.event.get():
            if event.type == 12:
                pygame.quit()
                sys.exit()
            elif event.type == 2:
                for player in range(Player_number):
                    for key in Commands[player]:
                        if key == event.scancode:
                            if Loop_Waiting_for_Start:
                                LpWfS_key_pressed(player)

            elif event.type == 5:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] > 51 and mouse_pos[0] < 115:
                    if mouse_pos[1] > 653 and mouse_pos[1] < 717:   #if back arrow clicked
                        Loop_Waiting_for_Start = False
                        Loop_Menu2 = True
                        Starting_and_animation = False
                if not Player_using_mouse == None:
                    if Player_using_mouse < Player_number + 1:
                        if Loop_Waiting_for_Start:
                            LpWfS_key_pressed(Player_using_mouse)

        pygame.display.update()
        pygame.time.delay(ms_per_tick)

    if Starting_and_animation:
        #Make screen full of white
        white_screen = pygame.Surface((1366, 768))
        white_screen.fill((255, 255, 255))
        previous_screen = screen.copy()
        for alpha in range(25):
            screen.blit(previous_screen, [0, 0, 1366, 768], [0, 0, 1366, 768])
            white_screen.set_alpha(10*alpha)
            screen.blit(white_screen, [0, 0, 1366, 768], [0, 0, 1366, 768])
            pygame.display.update()
            pygame.time.delay(40)
        white_screen.set_alpha(255)
        screen.blit(white_screen, [0, 0, 1366, 768], [0, 0, 1366, 768])
        pygame.display.update()

        #Genarating images and collision map
        generate_collisions_maps()
        mapImg_unbreakable, breakable_walls = generate_map_texture()        #mapImg_unbreakable : only objects that can't be breaked (floor, map walls, unbreakable walls)
        mapImg_unbreakableWidth = mapImg_unbreakable.get_width()
        mapImg_unbreakableHeight = mapImg_unbreakable.get_height()
        mapImg = mapImg_unbreakable.copy()      #mapImg contains also breakable walls
        for object in breakable_walls:
            mapImg.blit(Models[0][object[1]], [object[2]*64, object[3]*64, 64, 64], [0, 0, 64, 64])

        #generating bonus list
        Next_bonus = []         #bonus type : 0-20 (corresponds to position in Models)
        Showing_bonus = []      #bonus which are on the screen (must show those bonus)
        Bonus_to_del = []
        for bonus_type, bonus_amount in enumerate(choosed_bonus_amount):
            for bonus in range(bonus_amount):
                Next_bonus.append(bonus_type)
        for NoBonus in range(len(breakable_walls) - len(Next_bonus)):   #create empty breakable walls
            Next_bonus.append(None)
        random.shuffle(Next_bonus)

        #generating Fire and Bombs and Is_a_bonus lists
        In_fire = []        #In_fire[X][Y] returns True or False
        Fire = []
        Fires_to_del = []
        Is_a_bomb = []
        Is_a_bonus = []
        Bombs_to_del = [[], [], [], []]
        for X in range(choosed_map_dimensions[0]):
            In_fire.append([])
            Is_a_bomb.append([])
            Is_a_bonus.append([])
            for Y in range(choosed_map_dimensions[1]):
                In_fire[X].append(False)
                Is_a_bomb[X].append(False)
                Is_a_bonus[X].append(False)
          #it is now possible to call In_fire[X][Y] to know if a tile is on fire

        #Screen become the map
        mapImg_animation = pygame.Surface((1366, choosed_map_dimensions[1]*64))
        mapImg_animation.blit(mapImg, [X_map_shift, 0, mapImg_unbreakableWidth, mapImg_unbreakableHeight], [0, 0, mapImg_unbreakableWidth, mapImg_unbreakableHeight])
        Players_spawnpoints = [None, None, None, None]
        for object in map_objects:
            if object[0] == 4:     #player spawn point
                if object[1] < Player_number:   #object[1] : number of the player spawn point
                    mapImg_animation.blit(Models[4][object[1]][2], [object[2]*64 + X_map_shift + int((64 - Models[4][object[1]][2].get_width()) /2), object[3]*64 + int((64 - Models[4][object[1]][2].get_height()) /2), 64, 64], [0, 0, 64, 64])
                    Players_spawnpoints[object[1]] = (object[2], object[3])
        if Players_spawnpoints[0] == None:
            Players_spawnpoints[0] = (1, 1)
        if Players_spawnpoints[1] == None:
            Players_spawnpoints[1] = (choosed_map_dimensions[0] - 1, 1)
        if Players_spawnpoints[2] == None:
            Players_spawnpoints[2] = (1, choosed_map_dimensions[1] - 1)
        if Players_spawnpoints[3] == None:
            Players_spawnpoints[3] = (choosed_map_dimensions[0] - 1, choosed_map_dimensions[1] - 1)

        Players = []
        for num_player in range(Player_number):
            Players.append(Player(Models[4][num_player][2], num_player, Players_spawnpoints[num_player][0], Players_spawnpoints[num_player][1]))

        if not Player_using_mouse == None:      #mouse moves
            if Player_using_mouse < Player_number + 1:
                pos_mouse_moves = [X_map_shift + choosed_map_dimensions[0]*64 + 10, choosed_map_dimensions[1]*64 + Y_map_shift - 138]
                mapImg_animation.blit(create_mouse_moves(), [pos_mouse_moves[0], pos_mouse_moves[1], 128, 128], [0, 0, 128, 128])

        for alpha in range(25):
            screen.blit(white_screen, [0, 0, 1366, 768], [0, 0, 1366, 768])
            mapImg_animation.set_alpha(alpha*10)
            screen.blit(mapImg_animation, [0, Y_map_shift, 1366, mapImg_unbreakableHeight + Y_map_shift], [0, 0, 1366, mapImg_unbreakableHeight + Y_map_shift])
            pygame.display.update()
            pygame.time.delay(40)
        mapImg_animation.set_alpha(255)
        screen.blit(mapImg_animation, [0, Y_map_shift, 1366, mapImg_unbreakableHeight + Y_map_shift], [0, 0, 1366, mapImg_unbreakableHeight + Y_map_shift])
        pygame.display.update()

        if not Player_using_mouse == None:
            if Player_using_mouse < Player_number + 1:
                pygame.mouse.set_pos((pos_mouse_moves[0], pos_mouse_moves[1] +64))
        pygame.mouse.set_visible(False)
        Starting_and_animation = False
        GameLoop = True

    while GameLoop:
        for event in pygame.event.get():
            if event.type == 12:
                pygame.quit()
                sys.exit()
            elif event.type == 4:   #mouse move
                if Player_using_mouse < len(Players):
                    if not Players[Player_using_mouse].pushed:
                        mouse_pos = pygame.mouse.get_pos()
                        move_mouse_cursor_on_mouse_moves()
            elif event.type == 5:   #mouse button click
                if Player_using_mouse < len(Players):
                    if not Players[Player_using_mouse].pushed:
                        if event.button == 1:               #left click
                            Players[Player_using_mouse].set_bomb(round((Players[Player_using_mouse].pos[0] + 32 - Players[Player_using_mouse].image_shift[0] - X_map_shift) //64), round((Players[Player_using_mouse].pos[1] + 32 - Players[Player_using_mouse].image_shift[1] - Y_map_shift) //64))
                        elif event.button == 3:             #right click
                            Players[Player_using_mouse].Use_punch()
                            Players[Player_using_mouse].key_pressing[6] = True
                        elif event.button == 2 or event.button == 4 or event.button == 5:   #mouse wheel
                            Players[Player_using_mouse].Use_bonus()
                            Players[Player_using_mouse].key_pressing[5] = True
            elif event.type == 6:
                if Player_using_mouse < Player_number + 1:
                    if event.button == 3:
                        Players[Player_using_mouse].key_pressing[6] = False
                    elif event.button == 2 or event.button == 4 or event.button == 5:
                        Players[Player_using_mouse].key_pressing[5] = False
            elif event.type == 2:
                for player_number, player_commands in enumerate(Commands):
                    if player_number < len(Players):
                        for command_number, command in enumerate(Commands[player_number]):
                            if command == event.scancode:
                                if not Players[player_number].pushed:
                                    Players[player_number].key_pressing[command_number] = True
                                    if event.scancode == Commands[player_number][0]:            #if button go forward pressed (Monter)
                                        Players[player_number].speed_multiplier = 1
                                        if Players[player_number].inversed_controls:
                                            Players[player_number].direction = 1
                                        else:
                                            Players[player_number].direction = 0
                                        set_playing_Animation(player_number, True)
                                    elif event.scancode == Commands[player_number][1]:          #if button go left pressed (Aller à gauche)
                                        Players[player_number].speed_multiplier = 1
                                        if Players[player_number].inversed_controls:
                                            Players[player_number].direction = 3
                                        else:
                                            Players[player_number].direction = 2
                                        set_playing_Animation(player_number, True)
                                    elif event.scancode == Commands[player_number][2]:          #if button go backward pressed (Descendre)
                                        Players[player_number].speed_multiplier = 1
                                        if Players[player_number].inversed_controls:
                                            Players[player_number].direction = 0
                                        else:
                                            Players[player_number].direction = 1
                                        set_playing_Animation(player_number, True)
                                    elif event.scancode == Commands[player_number][3]:          #if button go right pressed (Aller à droite)
                                        Players[player_number].speed_multiplier = 1
                                        if Players[player_number].inversed_controls:
                                            Players[player_number].direction = 2
                                        else:
                                            Players[player_number].direction = 3
                                        set_playing_Animation(player_number, True)
                                    elif event.scancode == Commands[player_number][4]:            #if button place bomb pressed
                                        Players[player_number].set_bomb(round((Players[player_number].pos[0] + 32 - Players[player_number].image_shift[0] - X_map_shift) //64), round((Players[player_number].pos[1] + 32 - Players[player_number].image_shift[1] - Y_map_shift) //64))
                                    elif event.scancode == Commands[player_number][5]:          #Bonus key
                                        Players[player_number].Use_bonus()
                                    elif event.scancode == Commands[player_number][6]:          #Punch key
                                        Players[player_number].Use_punch()

            elif event.type == 3:
                for player_number, player_commands in enumerate(Commands):
                    if player_number < Player_number:
                        for command_number, command in enumerate(Commands[player_number]):
                            if command == event.scancode:
                                Players[player_number].key_pressing[command_number] = False
                                Players[player_number].speed_multiplier = 0             #if no any moving key is pressed then stop moving
                                for key_num in range(4):
                                    if Players[player_number].key_pressing[key_num]:    #if a moving key is pressed then continue moving in this direction
                                        if key_num == 0 or key_num == 3:
                                            Players[player_number].direction = key_num
                                        elif key_num == 1:
                                            Players[player_number].direction = 2
                                        elif key_num == 2:
                                            Players[player_number].direction = 1
                                        Players[player_number].speed_multiplier = 1
                                        set_playing_Animation(player_number, True)
                                        break
                                else:
                                    set_playing_Animation(player_number, False)

        #Erase foreground objects
        for object in Foreground:
            screen.blit(mapImg, object[1], [object[1][0] - X_map_shift, object[1][1] - Y_map_shift, object[1][2], object[1][3]])
        Foreground = []

        #Infections
        for player in Players:
            if player.alive:
                if player.infections_left_time > 0:
                    Players[player.player_number].infections_left_time = Players[player.player_number].infections_left_time - ms_per_tick
                    if Players[player.player_number].infections_left_time <= 0:
                        Players[player.player_number].infections_left_time = 0
                        Players[player.player_number].can_place_bombs = True
                        Players[player.player_number].must_place_bombs = False
                        Players[player.player_number].slowed = False
                        Players[player.player_number].boosted = False
                        Players[player.player_number].inversed_controls = False
                        Players[player.player_number].must_walk = False
                    elif player.must_place_bombs:
                        Players[player.player_number].time_before_place_bomb = Players[player.player_number].time_before_place_bomb - ms_per_tick
                        if Players[player.player_number].time_before_place_bomb <= 0:
                            Players[player.player_number].time_before_place_bomb = 0
                            Players[player.player_number].must_place_bombs = False
                            Players[player.player_number].set_bomb(round((player.pos[0] + 32 - player.image_shift[0] - X_map_shift) //64), round((player.pos[1] + 32 - player.image_shift[1] - Y_map_shift) //64))

        for player in Players:
            screen.blit(mapImg, player.pos, [player.pos[0] - X_map_shift, player.pos[1] - Y_map_shift, player.pos[2], player.pos[3]])       #Erase players
            for bomb in player.bombs_placed:
                screen.blit(mapImg, bomb.pos, [bomb.pos[0] - X_map_shift, bomb.pos[1] - Y_map_shift, bomb.pos[2], bomb.pos[3]])     #Erase bombs

        for bonus in Showing_bonus:
            screen.blit(mapImg, bonus.pos, [bonus.pos[0] - X_map_shift, bonus.pos[1] - Y_map_shift, bonus.pos[2], bonus.pos[3]])
        players_take_bonus()
        Bonus_to_del.sort(reverse = True)
        for num_bonus in Bonus_to_del:
            del Showing_bonus[num_bonus]
        Bonus_to_del = []
        for bonus in Showing_bonus:
            screen.blit(Models[3][bonus.number], bonus.pos, [0, 0, 64, 64])

        #Bombs
        for player in Players:
            for num_bomb, bomb in enumerate(player.bombs_placed):
                if bomb.left_time > 0:
                    bomb.left_time = bomb.left_time - ms_per_tick
                     #bombs slide:
                    if bomb.sliding:
                        Is_a_bomb[bomb.tileX][bomb.tileY] = False
                        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
                        images_distances = [(0, 64), (0, 0), (64, 0), (0, 0)]
                        direction = directions[bomb.sliding_direction]
                        image_distance = images_distances[bomb.sliding_direction]
                        if player_collide[round((bomb.pos[0] + image_distance[0] - X_map_shift) //64) + direction[0]][round((bomb.pos[1] + image_distance[1] - Y_map_shift) //64) + direction[1]]:
                            stop = True
                        elif Is_a_bomb[round((bomb.pos[0] + image_distance[0] - X_map_shift) //64) + direction[0]][round((bomb.pos[1] + image_distance[1] - Y_map_shift) //64) + direction[1]]:
                            stop = True
                        else:
                            for player in Players:
                                if round((player.pos[0] + 32 - player.image_shift[0] - X_map_shift) //64) == bomb.tileX + direction[0] and round((player.pos[1] + 32 - player.image_shift[1] - Y_map_shift) //64) == bomb.tileY + direction[1]:
                                    if player.alive:
                                        stop = True
                                        break
                            else:
                                stop = False
                        if stop:
                            if bomb.number == 2:    #bouncing bomb
                                new_direction = [1, 0, 3, 2]
                                bomb.sliding_direction = new_direction[bomb.sliding_direction]
                            else:
                                bomb.pos[0], bomb.pos[1] = bomb.tileX*64 + X_map_shift, bomb.tileY*64 + Y_map_shift
                                bomb.sliding = False
                                Is_a_bomb[bomb.tileX][bomb.tileY] = True
                        else:
                            movingVect = [None, None]
                            movingVect[0], movingVect[1] = direction[0] * bombs_sliding_speed, direction[1] * bombs_sliding_speed
                            bomb.pos[0] = bomb.pos[0] + movingVect[0]
                            bomb.pos[1] = bomb.pos[1] + movingVect[1]
                            bomb.tileX = round((bomb.pos[0] + 32 - X_map_shift) //64)
                            bomb.tileY = round((bomb.pos[1] + 32 - Y_map_shift) //64)
                            Is_a_bomb[bomb.tileX][bomb.tileY] = True
                        screen.blit(bomb.image, bomb.pos, [0, 0, bomb.pos[2], bomb.pos[3]])

                      #bombs are throwed
                    elif bomb.lifted:
                        if Players[bomb.lifted_by].key_pressing[6]:     #if pressing punch key
                            bomb.tileX = round((Players[bomb.lifted_by].pos[0] + 32 - Players[bomb.lifted_by].image_shift[0] - X_map_shift) //64)
                            bomb.tileY = round((Players[bomb.lifted_by].pos[1] + 32 - Players[bomb.lifted_by].image_shift[1] - Y_map_shift) //64)
                            bomb.pos[0], bomb.pos[1] = Players[bomb.lifted_by].pos[0] - Players[bomb.lifted_by].image_shift[0], Players[bomb.lifted_by].pos[1] - Players[bomb.lifted_by].image_shift[1] - 20
                            Foreground.append([bomb.image, bomb.pos])
                        else:
                            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
                            direction = directions[Players[bomb.lifted_by].direction]
                            bomb.tileX = round((Players[bomb.lifted_by].pos[0] + 32 - Players[bomb.lifted_by].image_shift[0] - X_map_shift) //64) + direction[0]
                            bomb.tileY = round((Players[bomb.lifted_by].pos[1] + 32 - Players[bomb.lifted_by].image_shift[1] - Y_map_shift) //64) + direction[1]
                            if player_collide[bomb.tileX][bomb.tileY]:
                                bomb.tileX = bomb.tileX - direction[0]
                                bomb.tileY = bomb.tileY - direction[1]
                            bomb.pos[0], bomb.pos[1] = bomb.tileX*64 + X_map_shift, bomb.tileY*64 + Y_map_shift
                            bomb.lifted = False
                            bomb.sliding = True
                            bomb.sliding_direction = Players[bomb.lifted_by].direction
                            Players[bomb.lifted_by].lifting_bomb = False
                            Is_a_bomb[bomb.tileX][bomb.tileY] = True

                     #bombs become solid when there is nobody in the bomb:
                    elif not bomb.solid:
                        if not bomb.number == 5:      #mine
                            for player_alive in Players:
                                if player_alive.alive:
                                    pos_player = [player_alive.pos[0] - players_collides_grip, player_alive.pos[1] - players_collides_grip]
                                    dist_from_bomb = [abs(pos_player[0] - bomb.pos[0]), abs(pos_player[1] - bomb.pos[1] + 32)]
                                    if dist_from_bomb[0] < 64 and dist_from_bomb[1] < 64:
                                        PLAYER_dbg = player_alive
                                        break
                            else:
                                bomb.solid = True
                                player_collide[bomb.tileX][bomb.tileY] = True
                        screen.blit(bomb.image, bomb.pos, [0, 0, bomb.pos[2], bomb.pos[3]])
                    else:
                        screen.blit(bomb.image, bomb.pos, [0, 0, bomb.pos[2], bomb.pos[3]])

                else:   #if not bomb.left_time > 0
                    if bomb.number == 5:    #mine
                        if bomb.lifted:
                            Players[bomb.lifted_by].lifting_bomb = False
                            bomb.lifted = False
                            bomb.lifted_by = None
                            bomb.pos[1] = bomb.pos[1] + 28
                        for playerPos in Players:
                            player_middle = (playerPos.pos[0] + (32 - playerPos.image_shift[0]), playerPos.pos[1] + (32 - playerPos.image_shift[1]))
                            if player_middle[0] > bomb.tileX*64 + X_map_shift and player_middle[0] < (bomb.tileX +1)*64 + X_map_shift:
                                if player_middle[1] > bomb.tileY*64 + Y_map_shift and player_middle[1] < (bomb.tileY +1)*64 + Y_map_shift:
                                    bomb.despawn(player.player_number, num_bomb)
                                    bomb_explode(player, bomb)
                                    break
                        else:   #if not player in bomb:
                            screen.blit(Models[1][7], bomb.pos, [0, 0, bomb.pos[2], bomb.pos[3]])   #hiden mine
                    elif bomb.number == 6:
                        bomb.left_time = 4000
                    else:
                        bomb.despawn(player.player_number, num_bomb)
                        bomb_explode(player, bomb)
        for num_flame, flame in enumerate(Fire):    #place fire
            screen.blit(mapImg, flame.pos, [flame.pos[0] - X_map_shift, flame.pos[1] - Y_map_shift, 64, 64])
            screen.blit(Models[2][flame.fire_lvl], flame.pos, [0, 0, 64, 64])
            Fire[num_flame].burn(num_flame)

        #Delete fire extinguished
        Fires_to_del.sort(reverse = True)
        for num_flame in Fires_to_del:
            screen.blit(mapImg, Fire[num_flame].pos, [Fire[num_flame].pos[0] - X_map_shift, Fire[num_flame].pos[1] - Y_map_shift, 64, 64])
            del Fire[num_flame]
        Fires_to_del = []
        #Delete bombs
        for num_player in range(4):
            Bombs_to_del[num_player].sort(reverse = True)
            for num_bomb in Bombs_to_del[num_player]:
                if num_bomb < len(Players[num_player].bombs_placed):
                    del Players[num_player].bombs_placed[num_bomb]
                reload_player_bomb_stock(num_player)
        Bombs_to_del = [[], [], [], []]

        #Place players
        for player_number, player in enumerate(Players):
            if player.alive:
                if player.pushed:
                    player.move_pushed()
                elif not player.speed_multiplier == 0:
                    player.move()
                elif player.must_walk:
                    player.move()
                #players animation
                if Players[player_number].play_animation:
                    Players[player_number].time_before_next_animation = Players[player_number].time_before_next_animation - ms_per_tick
                    if Players[player_number].time_before_next_animation < 0:
                        Players[player_number].animation = Players[player_number].animation + 1
                        if Players[player_number].animation == 4:
                            Players[player_number].animation = 0
                        Players[player_number].time_before_next_animation = round(60/Players[player_number].bonus_speed)
                angles = (0, 180, 90, 270)
                angle = angles[player.direction]
                screen.blit(pygame.transform.rotate(Models[4][player_number][get_num_ImgAnimation(Players[player_number].animation)], angle), player.pos, [0, 0, player.pos[2], player.pos[3]])
                #reload bonus push
                if player.punch == 6:   #push
                    Players[player_number].push_cooldown = Players[player_number].push_cooldown - ms_per_tick
                    if player.push_cooldown < 0:
                        Players[player_number].push_cooldown = 0

        #Place foreground
        for object in Foreground:
            screen.blit(object[0], object[1], [0, 0, object[1][2], object[1][3]])

        pygame.display.update()         #Update screen
        pygame.time.delay(ms_per_tick)  #Wait some ms

    if EndedGameLoop:
        Previous_MapImg = pygame.Surface((1366, 768))
        Previous_MapImg.blit(screen, [0, 0, 1366, 768], [0, 0, 1366, 768])
        EndImage = pygame.Surface((1366, 768))
        Text_to_write = "Le joueur " + str(Winner + 1)
        Text.Write_text(Text_to_write, None, 353, Player_color[Winner], 36, EndImage)
        Text.Write_text("gagne !", None, 384, Player_color[Winner], 36, EndImage)
        EndImage.blit(replay, [651, 500, 64, 64], [0, 0, 64, 64])
        pygame.mouse.set_visible(True)
        for alpha in range(25):
            screen.blit(Previous_MapImg, [0, 0, 1366, 768], [0, 0, 1366, 768])
            EndImage.set_alpha(alpha*10)
            screen.blit(EndImage, [0, 0, 1366, 768], [0, 0, 1366, 768])
            pygame.display.update()
            pygame.time.delay(40)
        EndImage.set_alpha(255)
        screen.blit(EndImage, [0, 0, 1366, 768], [0, 0, 1366, 768])
    while EndedGameLoop:
        for event in pygame.event.get():
            if event.type == 12:    #Game quit
                pygame.quit()
                sys.exit()
            elif event.type == 5:   #Mouse click
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] > 651 and mouse_pos[0] < 715:
                    if mouse_pos[1] > 500 and mouse_pos[1] < 564:  #Replay button
                        EndedGameLoop = False
                        Replaying_loop = True
        pygame.display.update()
        pygame.time.delay(ms_per_tick)

    if Replaying_loop:
        Previous_screen = pygame.Surface((1366, 768))
        Previous_screen.blit(screen, [0, 0, 1366, 768], [0, 0, 1366, 768])
        New_screen = pygame.Surface((1366, 768))
        New_screen.blit(background_menu, [0, 0, 1366, 768], [0, 0, 1366, 768])
        Text.Write_text("Choix de la carte", 479, 80, "#000000", 72, New_screen)
        for num_map_icon, map_icon in enumerate(map_icons):
            if num_map_icon < 3:    #First save line
                New_screen.blit(map_icon, [303 + 303*num_map_icon, 184, map_icon.get_width(), map_icon.get_height()], [0, 0, map_icon.get_width(), map_icon.get_height()])
            elif num_map_icon < 6:  #Second save line
                New_screen.blit(map_icon, [303 + 303*(num_map_icon - 3), 396, map_icon.get_width(), map_icon.get_height()], [0, 0, map_icon.get_width(), map_icon.get_height()])
            else:                   #Third save line
                New_screen.blit(map_icon, [303 + 303*(num_map_icon - 6), 608, map_icon.get_width(), map_icon.get_height()], [0, 0, map_icon.get_width(), map_icon.get_height()])

        for alpha in range(25):
            screen.blit(Previous_screen, [0, 0, 136, 768], [0, 0, 1366, 768])
            New_screen.set_alpha(alpha*10)
            screen.blit(New_screen, [0, 0, 1366, 768], [0, 0, 1366, 768])
            pygame.display.update()
            pygame.time.delay(40)
        New_screen.set_alpha(255)
        screen.blit(New_screen, [0, 0, 1366, 768], [0, 0, 1366, 768])
        Replaying_loop = False
        Loop_Menu1 = True

        choosed_map_dimensions, choosed_floor, choosed_map_wall, map_objects, choosed_bonus_amount = None, None, None, None, None
        breakable = []
        player_collide = []