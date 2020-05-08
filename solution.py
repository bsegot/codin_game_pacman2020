



# https://www.python-course.eu/finite_state_machine.php



class StateMachine:
    def __init__(self, pac_type, special_pallet=False, special_pallet_location=[]):
        # todo add constants that define the pac
        # todo add trigger that define movement_print
        # todo add method that update at each turn and run the new elements that can trigger a state change
        self.x = -1
        self.y = -1
        self.pac_type = pac_type
        self.special_pallet = special_pallet
        self.special_pallet_location = special_pallet_location
        self.handlers = {}
        self.startState = None
        self.endStates = []

    def get_closest(self, visible_normal_pellet):
        """get the closest pallet there is on the board from current pac"""

    def special_pallet_still_exist(self):
        """check if we still chase the big pallet"""


    def add_state(self, name, handler, end_state=0):
        name = name.upper()
        self.handlers[name] = handler
        if end_state:
            self.endStates.append(name)

    def set_start(self, name):
        self.startState = name.upper()

    def run(self, cargo):
        try:
            handler = self.handlers[self.startState]
        except:
            raise Exception("must call .set_start() before .run()")
        if not self.endStates:
            raise Exception("at least one state must be an end_state")

        while True:
            (newState, cargo) = handler(cargo)
            if newState.upper() in self.endStates:
                print("reached ", newState)
                break
            else:
                handler = self.handlers[newState.upper()]

positive_adjectives = ["great","super", "fun", "entertaining", "easy"]
negative_adjectives = ["boring", "difficult", "ugly", "bad"]

# todo define the states the pac can be in (exemple search for the biggest// no biggest in sight)
# todo or search the closest dfs, etc
# todo add a is_stuck_method that run every turn // easy by checking new params with old attributes

def start_transitions(txt):
    splitted_txt = txt.split(None,1)
    word, txt = splitted_txt if len(splitted_txt) > 1 else (txt,"")
    if word == "Python":
        newState = "Python_state"
    else:
        newState = "error_state"
    return (newState, txt)

def python_state_transitions(txt):
    splitted_txt = txt.split(None,1)
    word, txt = splitted_txt if len(splitted_txt) > 1 else (txt,"")
    if word == "is":
        newState = "is_state"
    else:
        newState = "error_state"
    return (newState, txt)

def is_state_transitions(txt):
    splitted_txt = txt.split(None,1)
    word, txt = splitted_txt if len(splitted_txt) > 1 else (txt,"")
    if word == "not":
        newState = "not_state"
    elif word in positive_adjectives:
        newState = "pos_state"
    elif word in negative_adjectives:
        newState = "neg_state"
    else:
        newState = "error_state"
    return (newState, txt)

def not_state_transitions(txt):
    splitted_txt = txt.split(None,1)
    word, txt = splitted_txt if len(splitted_txt) > 1 else (txt,"")
    if word in positive_adjectives:
        newState = "neg_state"
    elif word in negative_adjectives:
        newState = "pos_state"
    else:
        newState = "error_state"
    return (newState, txt)

def neg_state(txt):
    print("Hallo")
    return ("neg_state", "")

if __name__== "__main__":
    m = StateMachine()
    m.add_state("Start", start_transitions)
    m.add_state("Python_state", python_state_transitions)
    m.add_state("is_state", is_state_transitions)
    m.add_state("not_state", not_state_transitions)
    m.add_state("neg_state", None, end_state=1)
    m.add_state("pos_state", None, end_state=1)
    m.add_state("error_state", None, end_state=1)
    m.set_start("Start")
    m.run("Python is great")
    m.run("Python is difficult")
    m.run("Perl is ugly")

    m = StateMachine()
    m.add_state("Start", start_transitions)
    m.add_state("chase_special_pellet", chase_special_state_transitions)
    m.add_state("chase_normal_pellet", chase_normal_state_transitions)
    m.set_start("Start")

    m.run("Python is great")
    m.run("Python is difficult")
    m.run("Perl is ugly")

# ####################################################################################
# ####################################################################################

my_pac_list = [{'pac_id': 0, 'mine': True, 'x': 17, 'y': 5, 'type_id': 'NEUTRAL', 'speed_turns_left': 0, 'ability_cooldown': 0}, {'pac_id': 1, 'mine': True, 'x': 27, 'y': 7, 'type_id': 'NEUTRAL', 'speed_turns_left': 0, 'ability_cooldown': 0}]
pac_object_list = []
for pac in my_pac_list:

    pac_object = StateMachine()
    pac_object.add_state("Start", start_transitions)

    pac_object_list.append(pac_object)

import numpy as np


def closest_node(node, nodes):
    """find the closest point (euclidian) from (x,y) given a list of candidates points (nodes)"""
    nodes = np.asarray(nodes)
    dist_2 = np.sum((nodes - node) ** 2, axis=1)
    return list(nodes[np.argmin(dist_2)]), np.argmin(dist_2)


# my_pac_list = [{'pac_id': 0, 'mine': True, 'x': 17, 'y': 5, 'type_id': 'NEUTRAL', 'speed_turns_left': 0, 'ability_cooldown': 0}, {'pac_id': 1, 'mine': True, 'x': 27, 'y': 7, 'type_id': 'NEUTRAL', 'speed_turns_left': 0, 'ability_cooldown': 0}]
# visible_special_pellet = [[15, 7], [19, 7], [8, 13]]

def allocate_pacs(visible_special_pellet, pac_list):
    """allocate pacs according to the closest to special pallets"""

    allocation_list = []
    for pellet in visible_special_pellet:

        if len(pac_list) == 0:
            break
        node = [pellet[0], pellet[1]]
        nodes = [[x['x'], x['y']] for x in pac_list]

        best_pac_coordonate, pac_index = closest_node(node, nodes)
        allocation_list.append(
            {'pac_coordonate': best_pac_coordonate, 'pac_id': pac_list[pac_index]['pac_id'], 'special_pellet': node})

        del pac_list[pac_index]

    return allocation_list


import sys
import math

# Grab the pellets as fast as you can!

# width: size of the grid
# height: top left corner is (x=0, y=0)
width, height = [int(i) for i in input().split()]
for i in range(height):
    row = input()  # one line of the grid: space " " is floor, pound "#" is wall

# game loop
while True:
    my_score, opponent_score = [int(i) for i in input().split()]
    visible_pac_count = int(input())  # all your pacs and enemy pacs in sight
    my_pac_list = []
    opponent_pac_list = []
    for i in range(visible_pac_count):
        # pac_id: pac number (unique within a team)
        # mine: true if this pac is yours
        # x: position in the grid
        # y: position in the grid
        # type_id: unused in wood leagues
        # speed_turns_left: unused in wood leagues
        # ability_cooldown: unused in wood leagues
        pac_id, mine, x, y, type_id, speed_turns_left, ability_cooldown = input().split()
        pac_id = int(pac_id)
        mine = mine != "0"
        x = int(x)
        y = int(y)
        speed_turns_left = int(speed_turns_left)
        ability_cooldown = int(ability_cooldown)
        if mine == True:
            my_pac_list.append({'pac_id': pac_id, 'mine': mine, 'x': x, 'y': y, 'type_id': type_id,
                                'speed_turns_left': speed_turns_left, 'ability_cooldown': ability_cooldown})
        elif mine == False:
            opponent_pac_list.append({'pac_id': pac_id, 'mine': mine, 'x': x, 'y': y, 'type_id': type_id,
                                      'speed_turns_left': speed_turns_left, 'ability_cooldown': ability_cooldown})

            # print(my_pac_list, file=sys.stderr)

    visible_pellet_count = int(input())  # all pellets in sight
    visible_normal_pellet = []
    visible_special_pellet = []
    for i in range(visible_pellet_count):
        # value: amount of points this pellet is worth
        x, y, value = [int(j) for j in input().split()]
        if value == 1:
            visible_normal_pellet.append([x, y])
        elif value == 10:
            visible_special_pellet.append([x, y])

    # print(visible_special_pellet, file=sys.stderr)

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    # MOVE <pacId> <x> <y>
    test = allocate_pacs(visible_special_pellet, my_pac_list)

    char_print = ''
    for orders in test:
        if char_print == '':
            char_print = f"MOVE {orders['pac_id']} {orders['special_pellet'][0]} {orders['special_pellet'][1]}"
        else:
            char_print += f" | MOVE {orders['pac_id']} {orders['special_pellet'][0]} {orders['special_pellet'][1]}"

    print(char_print)