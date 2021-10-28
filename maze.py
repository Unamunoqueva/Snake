import readchar
import os
import random
POS_X = 0
POS_Y = 1
MAP_HEIGHT = 10
MAP_WIDTH = 20
my_position = [3, 1]
item_positions = []
NUM_OF_MAP_OBJECTS = 20
tail_length = 0
tail = []
end_game = False

#Generate random objects



while not end_game:
    while len(item_positions) < NUM_OF_MAP_OBJECTS:
        new_position = [random.randint(
            0, MAP_WIDTH), random.randint(0, MAP_HEIGHT)]

        if new_position not in item_positions and new_position != my_position:
            item_positions.append(new_position)
    # Draw the map
    print("+"+"-"*MAP_WIDTH*3 + "+")

    for coordinate_y in range(MAP_HEIGHT):  # Empieza en el 1
        print("|", end="")
        for coordinate_x in range(MAP_WIDTH):  # Empieza en el 1

            char_to_draw = " "
            object_in_cell = None
            tail_in_cell = None

            for item_position in item_positions:
                if item_position[POS_X] == coordinate_x and item_position[POS_Y] == coordinate_y:
                    char_to_draw = "*"
                    object_in_cell = item_position

            for tail_piece in tail:
                if tail_piece[POS_X] == coordinate_x and tail_piece[POS_Y] == coordinate_y:
                    char_to_draw = "@"
                    tail_in_cell = tail_piece

            if my_position[POS_X] == coordinate_x and my_position[POS_Y] == coordinate_y:
                char_to_draw = "@"

                if object_in_cell:
                    item_positions.remove(object_in_cell)
                    tail_length += 1

                if tail_in_cell:
                    print("Has muerto")
                    end_game = True

            print(" {} ".format(char_to_draw), end="")

        print("|")

    print("+"+"-"*MAP_WIDTH*3 + "+")

    # Ask user where he wants to move
    #direction = input("¿Donde te quieres mover? [AWSD]")
    direction = readchar.readchar().decode()

    if direction == "w":
        tail.insert(0, my_position.copy())
        tail = tail[:tail_length]
        my_position[POS_Y] -= 1
        my_position[POS_Y] %= MAP_HEIGHT
    elif direction == "a":
        tail.insert(0, my_position.copy())
        tail = tail[:tail_length]
        my_position[POS_X] -= 1
        my_position[POS_X] %= MAP_WIDTH
    elif direction == "s":
        tail.insert(0, my_position.copy())
        tail = tail[:tail_length]
        
        my_position[POS_Y] += 1
        my_position[POS_Y] %= MAP_HEIGHT
    elif direction == "d":
        tail.insert(0, my_position.copy())
        tail = tail[:tail_length]
        my_position[POS_X] += 1
        my_position[POS_X] %= MAP_WIDTH
    elif direction == "q":
        end_game = True

    os.system("cls")
