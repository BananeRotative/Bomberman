# Créé par alexis, le 22/03/2021 en Python 3.7
# Made for 1366 x 768 screens

import pygame, sys

path=""


assert path != "", "YOU NEED TO SET THE ABSOLUTE PATH OF THE PARENT OF THIS FILE IN THE path VARIABLE"
pygame.init()
screen = pygame.display.set_mode((1366,768), pygame.FULLSCREEN)

choosed_floor = 0
choosed_map_wall = 0
choosed_map_dimensions = [19,13]        #19x13 tiles (1 tile = 64x64px)

class GameObject:
    def __init__(self, image, type, Xpos, Ypos, tileX = None, tileY = None, object_number = None):
        self.image = image
        self.pos = image.get_rect().move(Xpos,Ypos)
        self.type = type        #type : floor(-2), unbreakable_wall(0), breakable_wall(1), player spawn point(3), bonus(4), other(5)
        self.tileX = tileX
        self.tileY = tileY
        self.object_number = object_number

    def move(self, vectX, vectY):
        self.pos = self.pos.move(vectX,vectY)

    def goto(self,Xpos,Ypos):
        self.pos[0], self.pos[1] = Xpos, Ypos

print("Loading textures...")
#Models = [[floors],[map_wall],[unbreakable_wall],[breakable_wall],[map_dimension_icon],[players spawn points],[green check/back arrow icon], [bonus]]
Models = []
for type_image in [["floor 0-0.png", "floor 1.png", "floor 2.png", "floor 0-1.png"], ["map_wall 0.png", "map_wall 1.png", "map_wall 2.png"], ["unbreakable_wall 0.png", "unbreakable_wall 1.png", "unbreakable_wall 2.png", "unbreakable_wall 3.png"], ["breakable_wall 0.png"], ["map dimensions icon.png"], ["player 1 img 3.png", "player 2 img 3.png", "player 3 img 3.png", "player 4 img 3.png"], ["green check icon.png", "arrow back icon.png"]]:
    Models.append([])
    for image_name in type_image:
        Models[len(Models)-1].append(pygame.image.load(path + "images/" + image_name).convert_alpha())       #Loads textures in Models
Models.append([])
for image_name in ["bonus fire up.png", "bonus full fire.png", "bonus fire down.png", "bonus bomb up.png", "bonus line bomb.png", "bonus bomb down.png", "bonus push.png", "bonus speed up.png", "bonus speed down.png", "bonus bouncing bomb.png", "bonus pierce bomb.png", "bonus skull.png", "bonus p bomb.png", "bonus mine.png", "bonus radioactive.png", "bonus dangerous bomb.png", "bonus remote bomb.png", "bonus devil.png", "bonus power glove.png", "bonus punch.png", "bonus bomb kick.png"]:
    Models[7].append(pygame.image.load(path + "images/" + image_name).convert())
background_map = pygame.image.load(path + "images/background.png")
background = pygame.image.load(path + "images/background.png")
arrows = pygame.image.load(path + "images/arrows.png")
bonus_amount_back = pygame.image.load(path + "images/bonus amount.png")
bonus_amount_back_selected = pygame.image.load(path + "images/bonus amount selected.png")
bonus_descriptions = pygame.image.load(path + "images/bonus descriptions.png")
print("Textures loaded")

objects = [[], [], [], [], []]               #type : unbreakable_wall(0), breakable_wall(1)
object_following_mouse = None
Placed_player_spawn_points = [False, False, False, False]

def set_new_wall(type,wall_number,tileX,tileY,follow_mouse = False):
    global object_following_mouse
    global Placed_player_spawn_points
    if follow_mouse:
        if object_following_mouse == None:
            object_following_mouse = GameObject(Models[type + 2][wall_number], type, 0, 0, object_number = wall_number)
    else:
        for pos_object_type_in_objects, object_type in enumerate(objects):
            for pos_object_in_object_type, object in enumerate(object_type):
                if object.tileX == tileX and object.tileY == tileY:
                    screen.blit(background_map, [0, 0, 1216, 832], [0, - Y_background_shift, 1216, 832])
                    if object.type == 3:
                        Placed_player_spawn_points[object.object_number] = False
                    del objects[pos_object_type_in_objects][pos_object_in_object_type]
        if not type == -2:      #if the new wall is a floor (eraser)
            objects[type].append(GameObject(Models[type + 2][wall_number], type, tileX*64, tileY*64 - Y_background_shift, tileX, tileY))
            if type == 3:
                Placed_player_spawn_points[wall_number] = True
                objects[type][len(objects[type]) -1].object_number = wall_number
                screen.blit(background_map, [object_following_mouse.pos[0], object_following_mouse.pos[1], object_following_mouse.pos[2], object_following_mouse.pos[3]], [object_following_mouse.pos[0], object_following_mouse.pos[1] - Y_background_shift, object_following_mouse.pos[2], object_following_mouse.pos[3]])
                object_following_mouse = None


def new_floor(floor_number):        #set a new floor according to the map dimensions
    if floor_number == 0:
        if choosed_map_dimensions[1] % 2 == 0:
            dark_or_light = 3
        else:
            dark_or_light = 0   #dark
        for X in range(0,64*choosed_map_dimensions[0],64):
            if choosed_map_dimensions[1] % 2 == 0:
                if dark_or_light == 0:
                    dark_or_light = 3   #light
                else:
                    dark_or_light = 0   #dark
            for Y in range(0,64*choosed_map_dimensions[1],64):
                background_map.blit(Models[0][dark_or_light],(X,Y))
                if dark_or_light == 0:
                    dark_or_light = 3
                else:
                    dark_or_light = 0
    else:
        for X in range(0,64*choosed_map_dimensions[0],64):
            for Y in range(0,64*choosed_map_dimensions[1],64):
                background_map.blit(Models[0][floor_number],(X,Y))
    global choosed_floor
    choosed_floor = floor_number
    new_map_wall(choosed_map_wall)

def new_map_wall(map_wall_number):          #sets map walls on outborders tiles
    global choosed_map_wall
    choosed_map_wall = map_wall_number
    for X in range(0,64*choosed_map_dimensions[0],64):
        background_map.blit(Models[1][map_wall_number], (X,0))
        background_map.blit(Models[1][map_wall_number],(X,64*choosed_map_dimensions[1]-64))
    for Y in range(0,64*choosed_map_dimensions[1],64):
        background_map.blit(Models[1][map_wall_number],(0,Y))
        background_map.blit(Models[1][map_wall_number],(64*choosed_map_dimensions[0]-64,Y))
    screen.blit(background_map, [0, Y_background_shift, 1216, 832], [0, 0, 1366, 832])

Y_background_shift = 0

def new_map_dimensions(tilesX,tilesY):
    global choosed_map_dimensions
    global Y_background_shift
    global Menu_shifted
    if tilesX < 3:
        tilesX = 19
    elif tilesX > 19:
        tilesX = 3
    if tilesY < 3:
        tilesY = 13
    elif tilesY > 13:
        tilesY = 3
    choosed_map_dimensions = [tilesX, tilesY]
    if choosed_map_dimensions[1] == 13:
        Y_background_shift = -32
    else:
        Y_background_shift = 0
    background_map.blit(background, [0, 0, 1216, 832], [0, 0, 1216, 832])
    new_floor(choosed_floor)
    screen.blit(background_map,(0,Y_background_shift))

#menu_icons : [[floor type icon](0), [map walls type icon](1), [unbreakable walls icon](2), [breakable walls icon](3), [map dimensions icon](4), [players spawn points icon](5), [green check icon](6)]
menu_icons = []
menu_icons.append(GameObject(Models[0][choosed_floor], 0, 1259, 192, object_number = choosed_floor))            #floor type icon
menu_icons.append(GameObject(Models[1][choosed_map_wall], 1, 1259, 288, object_number = choosed_map_wall))      #map wall type icon
menu_icons.append(GameObject(Models[2][0], 2, 1259, 384, object_number = 0))        #unbreakable walls icon
menu_icons.append(GameObject(Models[3][0], 3, 1259, 480, object_number = 0))        #breakable walls icon
menu_icons.append(GameObject(Models[4][0], 4, 1259, 60, object_number = 0))         #map dimensions icon
menu_icons.append(GameObject(Models[5][0], 5, 1259, 576, object_number = 0))        #players spawn points icon
menu_icons.append(GameObject(Models[6][0], 6, 1259, 672, object_number = 0))        #green check icon

#menu_icons_len = [number of different floors icons, number of different map walls icons, of different unbreakable walls icons, breakable walls icons, map dimension icon, players spawnpoint icon]
menu_icons_len = [2, 2, 3, 0, 0, 3]

def change_menu_icon(icon_number, new_icon_number):     #Changes the image on one of the objects in the menu
    menu_icons[icon_number].object_number = new_icon_number
    if menu_icons[icon_number].object_number < 0:
        menu_icons[icon_number].object_number = menu_icons_len[icon_number]
    if menu_icons[icon_number].object_number > menu_icons_len[icon_number]:
        menu_icons[icon_number].object_number = 0
    menu_icons[icon_number].image = Models[menu_icons[icon_number].type][menu_icons[icon_number].object_number]


def create_bonus_icons():
    bonus = 0
    for y in range(7):
        for x in range(3):
            objects.append(GameObject(Models[7][bonus], 4, x*350 + 64, y*64 + (y+1)*32))
            bonus = bonus + 1

def new_text(Text, color = "#000000"):
    global text
    text.image = font.render(Text, True, pygame.Color(color))

def new_bonus_image_in_description(origin_image, X_finalImage, Y_finalImage):       #This function transforms bonus image (64x64) into bonus image in description (128x128) and pastes it on screen
    final_image = pygame.Surface((128, 128))
    for Y in range(64):
        for X in range(64):
            pixel_color = origin_image.get_at((X, Y))
            final_image.set_at((X*2, Y*2), pixel_color)
            final_image.set_at((X*2 +1, Y*2), pixel_color)
            final_image.set_at((X*2, Y*2 +1), pixel_color)
            final_image.set_at((X*2 +1, Y*2 +1), pixel_color)
    screen.blit(final_image, [X_finalImage, Y_finalImage, 128, 128], [0, 0, 128, 128])



new_map_dimensions(choosed_map_dimensions[0],choosed_map_dimensions[1])
choosed_bonus_amount = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
total_bonus_amount = 0
#bonus_descriptions_texts = [[[title in french(line0), title in french(line 2), ...], [description in french(line0), description in french(line 1), ...]], ...]
bonus_descriptions_texts = []
bonus_descriptions_texts.append([["Flamme jaune"], ["Augmente la portée des bombes"]])
bonus_descriptions_texts.append([["Flamme rouge"], ["Met la portée des bombes", "au maximum"]])
bonus_descriptions_texts.append([["Flamme bleue"], ["Diminue la portée des bombes"]])
bonus_descriptions_texts.append([["Bombe +"], ["Augmente la quantité de", "bombes pouvant être placées", "à la fois par le joueur"]])
bonus_descriptions_texts.append([["Ligne de bombes"], ["Touche Bonus :", "Place toute la réserve de", "bombes du joueur en une ligne"]])
bonus_descriptions_texts.append([["Bombe -"], ["Diminue la quantité de", "bombes pouvant être placées", "à la fois par le joueur"]])
bonus_descriptions_texts.append([["Pousser"], ["Touche Bonus :", "Permet de pousser les autres", "joueurs situés sur la même case", "que le joueur"]])
bonus_descriptions_texts.append([["Vitesse +"], ["Augmente la vitesse du joueur"]])
bonus_descriptions_texts.append([["Vitesse -"], ["Diminue la vitesse du joueur"]])
bonus_descriptions_texts.append([["Bombes gouttes"], ["Les bombes posées par le joueur", "sont des bombes gouttes.", "Lorsqu'elles sont poussées,", "les bombes gouttes rebondissent", "contre les murs qu'elles touchent", "jusqu'à exploser"]])
bonus_descriptions_texts.append([["Bombes perçantes"], ["Les bombes posées par le joueur", "sont des bombes perçantes.", "Lorsqu'une bombe perçante", "explose, sa flamme ne s'arrête", "pas lorsqu'elle rencontre un mur", "cassable mais continue"]])
bonus_descriptions_texts.append([["Crâne"], ["Donne une infection au joueur", "la ramassant. Disparait", "après quelques secondes"]])
bonus_descriptions_texts.append([["Bombe P"], ["La première bombe du sac", "du joueur est une bombe P.", "La bombe P possède la portée", "maximale"]])
bonus_descriptions_texts.append([["Mine"], ["La première bombe du sac", "du joueur est une mine.", "La mine explose lorsqu'un joueur", "marche dessus ou lorsqu'elle", "est touchée par une flamme.", "Une fois posée,", "elle est peu visible"]])
bonus_descriptions_texts.append([["Radioactivité"], ["Donne trois effets d'infection", "au joueur la ramassant.", "Disparait après quelques", "secondes"]])
bonus_descriptions_texts.append([["Bombe", "dangereuse"], ["La première bombe du sac du", "joueur est une bombe", "dangereuse. La bombe", "dangereuse explose dans", "un carré de 5x5 cases"]])
bonus_descriptions_texts.append([["Bombe", "télécommandée"], ["La première bombe du sac", "du joueur est une bombe", "télécommandée. La bombe", "télécommandée explose lorsque", "le joueur la déclenche ou", "lorsqu'elle est touchée", "par une flamme.", "Touche bonus :", "Le joueur peut déclencher la", "bombe télécommandée à", "distance"]])
bonus_descriptions_texts.append([["Démon"], ["Tous les joueurs sont touchés", "par un effet d'infection.", "Disparait après quelques", "secondes"]])
bonus_descriptions_texts.append([["Gant de force"], ["Touche Coup :", "Le joueur peut attrapper", "des bombes en maintenant cette", "touche enfoncée avec la touche", "de lancer de bombes.", "Il peut ensuite lancer cette", "bombe comme une autre bombe", "en relâchant la touche", "Attention : la bombe n'est", "pas désamorcée"]])
bonus_descriptions_texts.append([["Gant de boxe"], ["Touche Coup :", "Le joueur peut donner un coup", "dans une bombe pour la", "pousser plus loin"]])
bonus_descriptions_texts.append([["Coup de pied"], ["Touche Coup :", "Le joueur peut lancer ses", "bombes plus loin si il", "maintient cette touche", "tout en lançant la bombe"]])

def new_text_in_description(num_bonus):     #sets a new title and a new description for the selected object
    global font
    font = pygame.font.Font(None, 54)
    for Line, Text in enumerate(bonus_descriptions_texts[num_bonus][0]):
        new_text(Text)
        screen.blit(text.image, [1006 + (360 - text.image.get_width())/2, 230 + Line*50, 27, 50], [0, 0, text.image.get_width(), text.image.get_height()])

    font = pygame.font.Font(None, 32)
    for Line, Text in enumerate(bonus_descriptions_texts[num_bonus][1]):
        new_text(Text)
        screen.blit(text.image, [1006 + (360 - text.image.get_width())/2, 350 + Line*28, 27, 50], [0, 0, text.image.get_width(), text.image.get_height()])

    font = pygame.font.Font(None, 72)

def new_total_maximal_bonus_amount():       #changes total maximal bonus amount (depends on the number of breakable walls)
    global total_maximal_bonus_amount
    new_text(str(total_maximal_bonus_amount))
    screen.blit(background, [557, 700, text.image.get_width(), 50], [557, 700, text.image.get_width(), 50])     #erases "totalMax" in "Total :   total / totalMax"

    total_maximal_bonus_amount = 0
    for object_type in choosed_map_objects:
        for object in object_type:
            if object.type == 1:
                if object.tileX < choosed_map_dimensions[0] - 1:
                    if object.tileY < choosed_map_dimensions[1] - 1:
                        total_maximal_bonus_amount = total_maximal_bonus_amount + 1

    new_text(str(total_maximal_bonus_amount))
    screen.blit(text.image, [557, 700, text.image.get_width(), 50], [0, 0, text.image.get_width(), 50])     #sets "totalMax" in "Total :   total / totalMax"

def new_total_bonus_amount():
    global total_bonus_amount
    new_text(str(total_bonus_amount))
    screen.blit(background, [543 - text.image.get_width(), 700, text.image.get_width(), 50], [543 - text.image.get_width(), 700, text.image.get_width(), 50])    #erases "total" in "Total :   total / totalMax"

    total_bonus_amount = 0
    for bonus_amount in choosed_bonus_amount:
        total_bonus_amount = total_bonus_amount + bonus_amount

    if total_bonus_amount > total_maximal_bonus_amount:
        new_text(str(total_bonus_amount), color = "#FF0000")    #red
    else:
        new_text(str(total_bonus_amount))   #black
    screen.blit(text.image, [543 - text.image.get_width(), 700, text.image.get_width(), 50], [0, 0, text.image.get_width(), 50])    #sets "total" in "Total :   total / totalMax"

def new_bonus_amount(number_pressed):       #changes a bonus amount
    if not SelectedBonus_amount_back == None:
        global SelectedBonus_amount_newText
        if SelectedBonus_amount_newText == None:
            SelectedBonus_amount_newText = number_pressed
        else:
            SelectedBonus_amount_newText = int(str(SelectedBonus_amount_newText) + str(number_pressed))
        if total_bonus_amount - choosed_bonus_amount[SelectedBonus_amount_back] + SelectedBonus_amount_newText > total_maximal_bonus_amount:    #if selected amount is too much
            SelectedBonus_amount_newText = total_maximal_bonus_amount - (total_bonus_amount - choosed_bonus_amount[SelectedBonus_amount_back])
            if SelectedBonus_amount_newText < 0:
                SelectedBonus_amount_newText = 0       #SelectedBonus_amount_newText can't be negative
        choosed_bonus_amount[SelectedBonus_amount_back] = SelectedBonus_amount_newText
        new_total_bonus_amount()

def unselect_option(num_option):
    if not num_option == None:
        screen.blit(background, [32, num_option*53, 1334, 53], [32, num_option*53, 1334, 53])
        new_text(options_texts[num_option])
        screen.blit(text.image, [options_pos[num_option][0], options_pos[num_option][1], text.image.get_width(), text.image.get_height()], [0, 0, text.image.get_width(), text.image.get_height()])
        option_value_pos = (32 + text.image.get_width(), num_option*53 + 12)
        new_text(str(options_values[num_option]))
        screen.blit(text.image, [option_value_pos[0], option_value_pos[1], text.image.get_width(), text.image.get_height()], [0, 0, text.image.get_width(), text.image.get_height()])

def change_option(num_option, new_value, selected = False):
    global selected_option
    if selected:
        unselect_option(selected_option)
        selected_option = num_option
    screen.blit(background, [32, num_option*53, 1334, 53], [32, num_option*53, 1334, 53])
    new_text(options_texts[num_option])
    screen.blit(text.image, [options_pos[num_option][0], options_pos[num_option][1], text.image.get_width(), text.image.get_height()], [0, 0, text.image.get_width(), text.image.get_height()])
    option_value_pos = (32 + text.image.get_width(), num_option*53 + 12)
    if selected_option == num_option:
        color = "#0000FF"
    else:
        color = "#000000"
    new_text(str(new_value), color)
    screen.blit(text.image, [option_value_pos[0], option_value_pos[1], text.image.get_width(), text.image.get_height()], [0, 0, text.image.get_width(), text.image.get_height()])

def Loop_options_key_pressed(str_key):
    global selected_value, options_values
    selected_value = selected_value + str_key
    if str_key == ".":
        new_value = float(selected_value + "0")
    elif "." in selected_value:
        new_value = float(selected_value)
    else:
        new_value = int(selected_value)
    options_values[selected_option] = new_value
    change_option(selected_option, new_value)

options_texts = ["Vitesse de départ : ", "Taille de la collision des joueurs : ", "Temps d'explosion des bombes : ", "Quantité de bombes au départ : ",
"Portée des bombes au départ : ", "Millisecondes par boucle de jeu : ", "Nombres de boucles de jeu par phase du feu : ", "Température du feu : ",
"Vitesse de glissement des bombes : ", "Temps entre deux utilisations du bonus 'Push' : ", "Temps d'infection : ", "Coefficient de vitesse par l'infection 'Ralenti' : ",
"Coefficient de vitesse par l'infection 'Accéléré' : "]
options_pos = [(32, 12), (32, 65), (32, 118), (32, 171), (32, 224), (32, 277), (32, 330), (32, 383), (32, 436), (32, 489), (32, 542), (32, 595), (32, 648)]
options_values = [5, 40, 4000, 1, 2, 40, 3, 1, 10, 3000, 15000, 0.2, 5]
selected_option = None
selected_value = ""

MainLoop = True     #continue looping
Loop_change_map = True
Loop_change_bonus = False
Loop_change_options = False

#MAINLOOP
while MainLoop:
    #LOOP 1:
    while Loop_change_map:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == 12:        #Close the window
                pygame.quit()
                sys.exit()
            if event.type == 5:
                if mouse_pos[0] < choosed_map_dimensions[0]*64 and mouse_pos[1] < choosed_map_dimensions[1]*64:
                    #If the mouse is not on the outborders tiles (where the map walls are)
                    if mouse_pos[0] > 64 and mouse_pos[0] < choosed_map_dimensions[0]*64 -64 and mouse_pos[1] > 64 + Y_background_shift and mouse_pos[1] < choosed_map_dimensions[1]*64 -64 + Y_background_shift:
                        if not object_following_mouse == None:
                            if Y_background_shift == 0:
                                set_new_wall(object_following_mouse.type, object_following_mouse.object_number, mouse_pos[0] // 64, (mouse_pos[1] + Y_background_shift) // 64)
                            else:       #if Y_background_shift = -32
                                set_new_wall(object_following_mouse.type, object_following_mouse.object_number, mouse_pos[0] // 64, (mouse_pos[1] + 32) // 64)
                            if not object_following_mouse == None:
                                screen.blit(background_map, [object_following_mouse.pos[0], object_following_mouse.pos[1], object_following_mouse.pos[2], object_following_mouse.pos[3]], [object_following_mouse.pos[0], object_following_mouse.pos[1] - Y_background_shift, object_following_mouse.pos[2], object_following_mouse.pos[3]])

                #menu
                if mouse_pos[0] > 1222:                                 #if clicked in the menu
                    if not object_following_mouse == None:
                        screen.blit(background_map, [object_following_mouse.pos[0], object_following_mouse.pos[1], object_following_mouse.pos[2], object_following_mouse.pos[3]], [object_following_mouse.pos[0], object_following_mouse.pos[1] - Y_background_shift, object_following_mouse.pos[2], object_following_mouse.pos[3]])
                        object_following_mouse = None

                    if mouse_pos[0] < 1253:                                 #if clicked on left arrows X
                        if mouse_pos[1] > 60 and mouse_pos[1] < 123:            #if map dimensions left arrow clicked
                            new_map_dimensions(choosed_map_dimensions[0] - 1, choosed_map_dimensions[1])
                        elif mouse_pos[1] > 192 and mouse_pos[1] < 255 :        #else if floor type left arrow clicked
                            change_menu_icon(0, menu_icons[0].object_number - 1)
                            new_floor(menu_icons[0].object_number)
                        elif mouse_pos[1] > 288 and mouse_pos[1] < 351:         #else if map wall type left arrow clicked
                            change_menu_icon(1, menu_icons[1].object_number - 1)
                            new_map_wall(menu_icons[1].object_number)
                        elif mouse_pos[1] > 384 and mouse_pos[1] < 447:         #else if unbreakable wall type left arrow clicked
                            change_menu_icon(2, menu_icons[2].object_number - 1)
                        elif mouse_pos[1] > 480 and mouse_pos[1] < 543:         #else if breakable wall type left arrow clicked
                            change_menu_icon(3, menu_icons[3].object_number - 1)
                        elif mouse_pos[1] > 576 and mouse_pos[1] < 639 :        #else if player spawnpoint left arrow clicked
                            change_menu_icon(5, menu_icons[5].object_number - 1)

                    elif mouse_pos[0] > 1259 and mouse_pos[0] < 1322:       #else if clicked on icons or top/bottom arrow X
                        if mouse_pos[1] > 22 and mouse_pos[1] < 54:             #if map dimensions top arrow clicked
                            new_map_dimensions(choosed_map_dimensions[0], choosed_map_dimensions[1] - 1)
                        elif mouse_pos[1] > 128 and mouse_pos[1] < 159 :        #else if map dimensions bottom arrow clicked
                            new_map_dimensions(choosed_map_dimensions[0], choosed_map_dimensions[1] + 1)
                        elif mouse_pos[1] > 192 and mouse_pos[1] < 255:         #else if floor type icon clicked
                            set_new_wall(-2, menu_icons[0].object_number, 0, 0, follow_mouse = True)
                        elif mouse_pos[1] > 384 and mouse_pos[1] < 447:         #else if unbreakable wall icon clicked
                            set_new_wall(0, menu_icons[2].object_number, 0, 0, follow_mouse = True)
                        elif mouse_pos[1] > 480 and mouse_pos[1] < 543:         #else if breakable wall icon clicked
                            set_new_wall(1, menu_icons[3].object_number, 0, 0, follow_mouse = True)
                        elif mouse_pos[1] > 576 and mouse_pos[1] < 639:         #else if player spawn points icon clicked
                            if Placed_player_spawn_points[menu_icons[5].object_number] == False:
                                set_new_wall(3, menu_icons[5].object_number, 0, 0, follow_mouse = True)
                        elif mouse_pos[1] > 672 and mouse_pos[1] < 735:         #else if green check icon clicked
                            Loop_change_map = False
                            Loop_change_bonus = True
                            choosed_map_objects = objects

                    elif mouse_pos[0] > 1328 and mouse_pos[0] < 1359:       #else if clicked on right arrows X
                        if mouse_pos[1] > 60 and mouse_pos[1] < 123 :           #if map dimensions right arrow clicked
                            new_map_dimensions(choosed_map_dimensions[0] + 1, choosed_map_dimensions[1])
                        elif mouse_pos[1] > 192 and mouse_pos[1] < 255 :        #else if floor type right arrow clicked
                            change_menu_icon(0, menu_icons[0].object_number - 1)
                            new_floor(menu_icons[0].object_number)
                        elif mouse_pos[1] > 288 and mouse_pos[1] < 351:         #else if map wall type right arrow clicked
                            change_menu_icon(1, menu_icons[1].object_number + 1)
                            new_map_wall(menu_icons[1].object_number)
                        elif mouse_pos[1] > 384 and mouse_pos[1] < 447:         #else if unbreakable wall type right arrow clicked
                            change_menu_icon(2, menu_icons[2].object_number + 1)
                        elif mouse_pos[1] > 480 and mouse_pos[1] < 543:         #else if breakable wall type right arrow clicked
                            change_menu_icon(3, menu_icons[3].object_number + 1)
                        elif mouse_pos[1] > 576 and mouse_pos[1] < 639:         #else if player spawn points right arrow clicked
                            change_menu_icon(5, menu_icons[5].object_number + 1)


        #remove object_following_mouse from screen :
        if not object_following_mouse == None:
            screen.blit(background_map, [object_following_mouse.pos[0], object_following_mouse.pos[1], object_following_mouse.pos[2], object_following_mouse.pos[3]], [object_following_mouse.pos[0], object_following_mouse.pos[1] - Y_background_shift, object_following_mouse.pos[2], object_following_mouse.pos[3]])

        for object_type in objects:
            for object in object_type:
                a = 1
                screen.blit(background_map, [object.pos[0], object.pos[1], object.pos[2], object.pos[3]], [object.pos[0], object.pos[1] - Y_background_shift, object.pos[2], object.pos[3]])

        for object_type in objects:
            for object in object_type:
                if object.tileX < choosed_map_dimensions[0] -1 and object.tileY < choosed_map_dimensions[1] -1:
                    screen.blit(object.image, [object.tileX *64, object.tileY*64 + Y_background_shift, object.pos[2], object.pos[3]], [0, 0, 64, 64])

        screen.blit(arrows, [1217, -32, 149, 832], [0, 0, 149, 832])

        if not object_following_mouse == None:
            if mouse_pos[0] > choosed_map_dimensions[0]*64 -32:
                object_following_mouse.goto(choosed_map_dimensions[0]*64 - 64,mouse_pos[1] -32)
            else:
                object_following_mouse.goto(mouse_pos[0] - 32,mouse_pos[1] -32)
            screen.blit(object_following_mouse.image, (object_following_mouse.pos[0], object_following_mouse.pos[1]))

        for icon in menu_icons:     #refer to menu_icons formation for more information
            screen.blit(background, [icon.pos[0], icon.pos[1], 64, 64], [icon.pos[0], icon.pos[1] - Y_background_shift, 64, 64])
            screen.blit(icon.image, icon.pos, [0, 0, 64, 64])

        pygame.display.update()
        pygame.time.delay(50)

    #LOOP 2:
    if Loop_change_bonus:
        objects = []
        screen.blit(background, [0, 0, 1366, 768], [0, 0, 1366, 768])   #replace background
        create_bonus_icons()
        font = pygame.font.Font(None, 72)
        text = GameObject(font.render("0", True, pygame.Color("#000000")), 5, 0, 0)
        SelectedBonus_amount_back = None
        total_maximal_bonus_amount = None
        new_total_maximal_bonus_amount()
        screen.blit(Models[6][0], [904, 690, 64, 64], [0, 0, 64, 64])   #green check icon
        screen.blit(Models[6][1], [32, 690, 64, 64], [0, 0, 64, 64])    #arrow back icon
        new_text("Total :")
        screen.blit(text.image, [250, 700, 146, 50], [0, 0, 146, 50])   #sets "Total :" in "Total :   total / totalMax"
        new_text("/")
        screen.blit(text.image, [543, 700, 14, 50], [0, 0, 14, 50])     #sets "/" in "Total :   total / totalMax"
        if total_bonus_amount > total_maximal_bonus_amount:
            new_text(str(total_bonus_amount), color = "#FF0000")
        else:
            new_text(str(total_bonus_amount))
        screen.blit(text.image, [543 - text.image.get_width(), 700, text.image.get_width(), 50], [0, 0, text.image.get_width(), 50])    #sets "total" in "Total :   total / totalMax"
        new_text(str(total_maximal_bonus_amount))
        screen.blit(text.image, [557, 700, text.image.get_width(), 50], [0, 0, text.image.get_width(), 50])     #sets "totalMax" in "Total :   total / totalMax"
    while Loop_change_bonus:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == 12:
                pygame.quit()
                sys.exit()
            elif event.type == 5:
                SelectedBonus_amount_back = None
                SelectedBonus_amount_newText = None
                for num_objects, object in enumerate(objects):
                    if mouse_pos[0] > object.pos[0] + 95 and mouse_pos[0] < object.pos[0] + 191:
                        if mouse_pos[1] > object.pos[1] and mouse_pos[1] < object.pos[1] + 64:      #if bonus amount selector clicked
                            SelectedBonus_amount_back = num_objects
                            SelectedBonus = num_objects
                            screen.blit(bonus_descriptions, [1000, 0, 366, 768], [0, 0, 366, 768])
                            new_bonus_image_in_description(object.image, 1122, 70)
                            new_text_in_description(num_objects)
                    if mouse_pos[0] > object.pos[0] and mouse_pos[0] < object.pos[0] + 64:
                        if mouse_pos[1] > object.pos[1] and mouse_pos[1] < object.pos[1] + 64:      #if an object is clicked
                            SelectedBonus = num_objects
                            screen.blit(bonus_descriptions, [1000, 0, 366, 768], [0, 0, 366, 768])
                            new_bonus_image_in_description(object.image, 1122, 70)
                            new_text_in_description(num_objects)
                if mouse_pos[1] > 690 and mouse_pos[1] < 754:       #if clicked on back arrow / green check Y
                    if mouse_pos[0] > 32 and mouse_pos[0] < 96:         #if clicked on back arrow
                        Loop_change_bonus = False
                        Loop_change_map = True
                    elif mouse_pos[0] > 904 and mouse_pos[0] < 968:     #else if clicked on green check
                        Loop_change_bonus = False
                        Loop_change_options = True
            elif event.type == 2:
                if event.key == 256:        #NUMPAD 0
                    new_bonus_amount(0)
                elif event.key == 257:      #NUMPAD 1
                    new_bonus_amount(1)
                elif event.key == 258:      #NUMPAD 2
                    new_bonus_amount(2)
                elif event.key == 259:      #NUMPAD 3
                    new_bonus_amount(3)
                elif event.key == 260:      #NUMPAD 4
                    new_bonus_amount(4)
                elif event.key == 261:      #NUMPAD 5
                    new_bonus_amount(5)
                elif event.key == 262:      #NUMPAD 6
                    new_bonus_amount(6)
                elif event.key == 263:      #NUMPAD 7
                    new_bonus_amount(7)
                elif event.key == 264:      #NUMPAD 8
                    new_bonus_amount(8)
                elif event.key == 265:      #NUMPAD 9
                    new_bonus_amount(9)

        for object in objects:
            screen.blit(background, [object.pos[0], object.pos[1], object.pos[2], object.pos[3]], [object.pos[0], object.pos[1], object.pos[2], object.pos[3]])
            screen.blit(background, [object.pos[0] + 95, object.pos[1], 96, 64], [0, 0, 96, 64])


        for num_objects, object in enumerate(objects):
            screen.blit(object.image, [object.pos[0], object.pos[1], object.pos[2], object.pos[3]], [0, 0, 64, 64])
            if SelectedBonus_amount_back == num_objects:
                screen.blit(bonus_amount_back_selected, [object.pos[0] + 95, object.pos[1], 96, 64], [0, 0, 96, 64])
            else:
                screen.blit(bonus_amount_back, [object.pos[0] + 95, object.pos[1], 96, 64], [0, 0, 96, 64])
            new_text(str(choosed_bonus_amount[num_objects]))
            if choosed_bonus_amount[num_objects] > 9:
                text.goto(object.pos[0] + 95 + (96 - text.pos[2]*2)/2, object.pos[1] + (64 - text.pos[3])/2)
                screen.blit(text.image, text.pos, [0, 0, 60, 50])
            else:
                text.goto(object.pos[0] + 95 + (96 - text.pos[2])/2, object.pos[1] + (64 - text.pos[3])/2)
                screen.blit(text.image, text.pos, [0, 0, text.pos[2], text.pos[3]])

        pygame.display.update()
        pygame.time.delay(50)
    if Loop_change_map:
        objects = choosed_map_objects
        screen.blit(background_map, [0, 0, 1366, 768], [0, - Y_background_shift, 1366, 768])
    else:
        if total_bonus_amount > total_maximal_bonus_amount:
            font = pygame.font.Font(None, 92)
            new_text("Trop de bonus !", color = "#800000")
            screen.blit(text.image, [440, 352, 486, 65], [0, 0, 486, 65])
            pygame.display.update()
            pygame.time.delay(1000)
            Loop_change_bonus = True
            Loop_change_options = False

    if Loop_change_options:
        screen.blit(background, [0, 0, 1366, 768], [0, 0, 1366, 768])
        font = pygame.font.Font(None, 40)
        for num_option in range(13):
            change_option(num_option, options_values[num_option])
        screen.blit(Models[6][0], [1259, 672, 64, 64], [0, 0, 64, 64])    #green check icon
        screen.blit(Models[6][1], [32, 690, 64, 64], [0, 0, 64, 64])    #arrow back icon
    while Loop_change_options:
        for event in pygame.event.get():
            if event.type == 12:    #quit
                pygame.quit()
                sys.exit()
            elif event.type == 5:   #mouse click
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] < 800:
                    if mouse_pos[1] < 53:   #num option 0
                        change_option(0, options_values[0], True)
                        selected_value = ""
                    elif mouse_pos[1] < 106:    #num option 1
                        change_option(1, options_values[1], True)
                        selected_value = ""
                    elif mouse_pos[1] < 159:    #num option 2
                        change_option(2, options_values[2], True)
                        selected_value = ""
                    elif mouse_pos[1] < 212:    #num option 3
                        change_option(3, options_values[3], True)
                        selected_value = ""
                    elif mouse_pos[1] < 265:    #num option 4
                        change_option(4, options_values[4], True)
                        selected_value = ""
                    elif mouse_pos[1] < 318:    #num option 5
                        change_option(5, options_values[5], True)
                        selected_value = ""
                    elif mouse_pos[1] < 371:    #num option 6
                        change_option(6, options_values[6], True)
                        selected_value = ""
                    elif mouse_pos[1] < 424:    #num option 7
                        change_option(7, options_values[7], True)
                        selected_value = ""
                    elif mouse_pos[1] < 477:    #num option 8
                        change_option(8, options_values[8], True)
                        selected_value = ""
                    elif mouse_pos[1] < 530:    #num option 9
                        change_option(9, options_values[9], True)
                        selected_value = ""
                    elif mouse_pos[1] < 583:    #num option 10
                        change_option(10, options_values[10], True)
                        selected_value = ""
                    elif mouse_pos[1] < 636:    #num option 11
                        change_option(11, options_values[11], True)
                        selected_value = ""
                    elif mouse_pos[1] < 689:    #num option 12
                        change_option(12, options_values[12], True)
                        selected_value = ""
                    else:
                        unselect_option(selected_option)
                        selected_option = None
                        if mouse_pos[0] > 32 and mouse_pos[0] < 96:         #back arrow
                            if mouse_pos[1] > 690 and mouse_pos[1] < 754:
                                Loop_change_options = False
                                Loop_change_bonus = True
                else:
                    unselect_option(selected_option)
                    selected_option = None
                    if mouse_pos[0] > 1259 and mouse_pos[0] < 1323:         #green check
                        if mouse_pos[1] > 672 and mouse_pos[1] < 736:
                            Loop_change_options = False
                            MainLoop = False
            elif event.type == 2:   #key pressing
                if event.key == 256 or event.key == 48:     #key 0
                    Loop_options_key_pressed("0")
                elif event.key == 257 or event.key == 49:   #key 1
                    Loop_options_key_pressed("1")
                elif event.key == 258 or event.key == 50:   #key 2
                    Loop_options_key_pressed("2")
                elif event.key == 259 or event.key == 51:   #key 3
                    Loop_options_key_pressed("3")
                elif event.key == 260 or event.key == 52:   #key 4
                    Loop_options_key_pressed("4")
                elif event.key == 261 or event.key == 53:   #key 5
                    Loop_options_key_pressed("5")
                elif event.key == 262 or event.key == 54:   #key 6
                    Loop_options_key_pressed("6")
                elif event.key == 263 or event.key == 55:   #key 7
                    Loop_options_key_pressed("7")
                elif event.key == 264 or event.key == 56:   #key 8
                    Loop_options_key_pressed("8")
                elif event.key == 265 or event.key == 57:   #key 9
                    Loop_options_key_pressed("9")
                elif event.key == 266 or event.key == 44:   #key .
                    Loop_options_key_pressed(".")

        pygame.display.update()
        pygame.time.delay(50)

pygame.quit()

Correct_answer = False
while not Correct_answer:
    map_number = input("Choix du numéro de la carte (entre 1 et 9)\n")
    try:
        number = int(map_number)
        if number >= 1 and number <=9:
            Correct_answer = True
        else:
            print("Erreur : le numéro de fichier doit être compris entre 1 et 9")
    except ValueError:
        print("Erreur : le numéro de fichier doit être un chiffre entre 1 et 9")

print("Generating Save file...")
str_choosed_map_dimensions = str(choosed_map_dimensions[0]) + "/" + str(choosed_map_dimensions[1])
GameCode = str_choosed_map_dimensions + "///"
GameCode = GameCode + str(choosed_floor) + "///" + str(choosed_map_wall)
map_objects = []
for object_type in choosed_map_objects:
    for object in object_type:
        if object.tileX < choosed_map_dimensions[0] - 1 and object.tileY < choosed_map_dimensions[1] - 1:
            for num_model, model in enumerate(Models[object.type + 2]):
                if model == object.image:
                    if object.type == 0:    #unbreakable wall
                        object.type = 7
                    if object.type == 1:    #breakable wall
                        object.type = 0
                    if object.type == 3:    #player spawn point
                        object.type = 4
                    map_objects.append(str(object.type) + "/" + str(num_model) + "/" + str(object.tileX) + "/" + str(object.tileY))
str_map_objects = ""
for num_object, object in enumerate(map_objects):
    if num_object == len(map_objects) - 1:
        str_map_objects = str_map_objects + object
    else:
        str_map_objects = str_map_objects + object + "//"
GameCode = GameCode + "///" + str_map_objects
str_choosed_bonus_amount = ""
for num_bonus, bonus_amount in enumerate(choosed_bonus_amount):
    str_choosed_bonus_amount = str_choosed_bonus_amount + str(bonus_amount)
    if not num_bonus == len(choosed_bonus_amount) - 1:
        str_choosed_bonus_amount = str_choosed_bonus_amount + "/"
GameCode = GameCode + "///" + str_choosed_bonus_amount
str_choosed_options = ""
for num_option, option in enumerate(options_values):
    if num_option == len(options_values) - 1:
        str_choosed_options = str_choosed_options + str(option)
    else:
        str_choosed_options = str_choosed_options + str(option) + "/"
GameCode = GameCode + "///" + str_choosed_options
with open("saves/SAVE " + map_number + ".txt", 'w') as new_map:
    new_map.write(GameCode)
print("Save file generated\n")