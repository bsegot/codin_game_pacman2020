
class State(object):
    """
    We define a state object which provides some utility functions for the
    individual states within the state machine.
    """

    def __init__(self):
        print('Processing current state:', str(self), file=sys.stderr)

    def on_event(self, event):
        """
        Handle events that are delegated to this State.
        """
        pass

    def __repr__(self):
        """
        Leverages the __str__ method to describe the State.
        """
        return self.__str__()

    def __str__(self):
        """
        Returns the name of the State.
        """
        return self.__class__.__name__


# Start of our states
class ChaseClosestSpecialPallet(State):
    """
    The state which indicates that there are limited device capabilities.
    """

    def on_event(self, event):
        if event == 'normal_chase':
            return ChaseClosestNormalPallet()

        return self


# class UnlockedState(State):
class ChaseClosestNormalPallet(State):
    """
    The state which indicates that there are no limitations on device
    capabilities.
    """

    def on_event(self, event):
        if event == 'device_locked':
            return ChaseClosestSpecialPallet()

        return self
# End of our states.


class SimpleDevice(object):
    """
    A simple state machine that mimics the functionality of a device from a
    high level.
    """

    def __init__(self, x, y, x_special_pallet, y_special_pallet, pac_id, speed_turns_left, ability_cooldown,
                 width, height, type_id,
                 special_pallet=False, special_pallet_location=[]):
        """ Initialize the components. """
        self.x = x
        self.y = y
        self.x_special_pallet = x_special_pallet
        self.y_special_pallet = y_special_pallet
        self.pac_id = pac_id
        self.speed_turns_left = speed_turns_left
        self.ability_cooldown = ability_cooldown
        self.special_pallet = special_pallet
        self.special_pallet_location = special_pallet_location
        self.x_closest_normal_pallet = -1
        self.y_closest_normal_pallet = -1
        self.width = width
        self.height = height
        self.type_id = type_id

        # Start with a default state.
        if special_pallet:
            self.state = ChaseClosestSpecialPallet()
        else:
            self.state = ChaseClosestNormalPallet()

    def update_turn(self, my_pac_list):
        """ update info of the position of our pacs """
        for pac in my_pac_list:
            if pac['pac_id'] == self.pac_id:
                self.x = pac['x']
                self.y = pac['y']
                self.speed_turns_left = pac['speed_turns_left']
                self.ability_cooldown = pac['ability_cooldown']
                break

    def defensive_mecanism(self, opponent_pac_list):

        # if there is no enemy in sight
        if opponent_pac_list == []:
            return 0, ''

        for opponent in opponent_pac_list:

            if self.type_id == 'PAPER' and opponent['type_id'] == 'SCISSORS':
                if less_than_2_tiles(self.x, self.y, opponent['x'], opponent['y']):
                    return 1, 'ROCK'
            elif self.type_id == 'SCISSORS' and opponent['type_id'] == 'ROCK':
                if less_than_2_tiles(self.x, self.y, opponent['x'], opponent['y']):
                    return 1, 'PAPER'
            elif self.type_id == 'ROCK' and opponent['type_id'] == 'PAPER':
                if less_than_2_tiles(self.x, self.y, opponent['x'], opponent['y']):
                    return 1, 'SCISSORS'

        return 0, ''

    def get_defensive_move(self, pac_type):
        return f'SWITCH {self.pac_id} {pac_type}'


    def speed_boost(self):
        # test, will implement more complex speed management later
        if self.ability_cooldown == 0:
            return 1, f'SPEED {self.pac_id}'
        else:
            return 0, ''

    def refresh_closest_normal_pallet(self, visible_normal_pellet, initial_pallets_list):

        node = [self.x, self.y]
        best_pac_coordonate, pac_index = closest_node(node, visible_normal_pellet, self.width, self.height, initial_pallets_list)

        self.x_closest_normal_pallet = best_pac_coordonate[0]
        self.y_closest_normal_pallet = best_pac_coordonate[1]

    def special_pallet_exist(self, visible_special_pellet):
        # if the special pellet we target has already been eaten we return 0
        for special_pellet in visible_special_pellet:
            if self.x_special_pallet == special_pellet[0] and self.y_special_pallet == special_pellet[1]:
                return 1

        return 0

    def get_normal_pallet_move(self):

        return f'MOVE {self.pac_id} {self.x_closest_normal_pallet} {self.y_closest_normal_pallet}'

    def get_special_pallet_move(self):

        return f'MOVE {self.pac_id} {self.x_special_pallet} {self.y_special_pallet}'

    def on_event(self, event):
        """
        This is the bread and butter of the state machine. Incoming events are
        delegated to the given states which then handle the event. The result is
        then assigned as the new state.
        """

        # The next state will be the result of the on_event function.
        self.state = self.state.on_event(event)



import numpy as np
import random

def print_order_list(order_list):
    char_print = ''
    for orders in order_list:
        if char_print == '':
            char_print = orders
        else:
            char_print = char_print + "| " + orders
    return char_print


def closest_node(node, nodes, width, height, initial_pallets_list):
    """find the closest point (euclidian) from (x,y) given a list of candidates points (nodes)"""
    #   print(f'nodes {nodes}', file=sys.stderr)

    if not nodes:
        nodes = initial_pallets_list
    nodes = np.asarray(nodes)
    dist_2 = np.sum((nodes - node) ** 2, axis=1)
    return list(nodes[np.argmin(dist_2)]), np.argmin(dist_2)

def less_than_2_tiles(x1, y1, x2, y2):

    node = [x1, y1]
    nodes = np.asarray([[x2 ,y2]])
    dist_2 = np.sum((nodes - node) ** 2, axis=1)

    if dist_2 < 2:
        return 1
    else:
        return 0

# my_pac_list = [{'pac_id': 0, 'mine': True, 'x': 17, 'y': 5, 'type_id': 'NEUTRAL', 'speed_turns_left': 0, 'ability_cooldown': 0}, {'pac_id': 1, 'mine': True, 'x': 27, 'y': 7, 'type_id': 'NEUTRAL', 'speed_turns_left': 0, 'ability_cooldown': 0}]
# visible_special_pellet = [[15, 7], [19, 7], [8, 13]]

def allocate_pacs(visible_special_pellet, visible_normal_pellet, pac_list, width, height, initial_pallets_list):
    """allocate pacs according to the closest to special pallets"""

    allocation_list = []

    for pellet in visible_special_pellet:

        if len(pac_list) == 0:
            break
        node = [pellet[0], pellet[1]]
        nodes = [[x['x'], x['y']] for x in pac_list]

        best_pac_coordonate, pac_index = closest_node(node, nodes, width, height, initial_pallets_list)
        allocation_list.append(
            {'pac_coordonate': best_pac_coordonate, 'pac_id': pac_list[pac_index]['pac_id'], 'special_pellet': node, 'type_id': pac_list[pac_index]['type_id']})

        del pac_list[pac_index]

    # there are not enough special pallet,
    if len(pac_list) > 0:
        for remaining_pac in pac_list:
            node = [remaining_pac['x'], remaining_pac['y']]

            best_pac_coordonate, pac_index = closest_node(node, visible_normal_pellet, width, height, initial_pallets_list)
            allocation_list.append(
                {'pac_coordonate': [remaining_pac['x'], remaining_pac['y']], 'pac_id': remaining_pac['pac_id'], 'special_pellet': best_pac_coordonate, 'type_id' : remaining_pac['type_id']})

    return allocation_list



def pac_is_dead(pac_object, my_pac_list):

    pac_id_list = [x['pac_id'] for x in my_pac_list]
    if pac_object.pac_id not in pac_id_list:
        return 1
    else:
        return 0



import sys
import math



# Grab the pellets as fast as you can!

# width: size of the grid
# height: top left corner is (x=0, y=0)
width, height = [int(i) for i in input().split()]
for i in range(height):
    row = input()  # one line of the grid: space " " is floor, pound "#" is wall

# game loop
turn = 1
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

    print(my_pac_list, file=sys.stderr)

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
    if turn == 1:
        # assignement of the pacs (first round)
        initial_pallets = {(x[0], x[1]) for x in visible_normal_pellet}
        initial_pallets_list = [[x[0], x[1]] for x in visible_normal_pellet]
        # print(f'initial pellets {initial_pallets}', file=sys.stderr)
        allocated_pacs = allocate_pacs(visible_special_pellet, visible_normal_pellet, my_pac_list, width, height, initial_pallets_list)

        pac_object_list = []
        order_list = []
        for pac in allocated_pacs:
            x = pac['pac_coordonate'][0]
            y = pac['pac_coordonate'][1]
            pac_id = pac['pac_id']
            speed_turns_left = 0
            ability_cooldown = 0
            special_pallet = True
            x_special_pallet = pac['special_pellet'][0]
            y_special_pallet = pac['special_pellet'][1]
            special_pallet_location = []
            type_id = pac['type_id']

            pac_object = SimpleDevice(x, y, x_special_pallet, y_special_pallet, pac_id, speed_turns_left, ability_cooldown, width, height, type_id, special_pallet, special_pallet_location)

            activate_speed ,str_speed = pac_object.speed_boost()
            if activate_speed:
                order_list.append(str_speed)
            # str_move = pac_object.get_special_pallet_move()
            # order_list.append(str_move)
            pac_object_list.append(pac_object)


        # print("turn 1", file=sys.stderr)
        # print(f'we have an order list of {order_list}', file=sys.stderr)

        output = print_order_list(order_list)
        print(output)

    elif turn > 1:
        # normal turn, we get 1-information of special pallets outstanding // check if we change states
        new_pac_object_list = []
        order_list = []
        for pac_object in pac_object_list:

            # we update the pallet list
            # print(f'initial pellets {initial_pallets}', file=sys.stderr)
            # updating the pellets record
            initial_pallets.discard((pac_object.x, pac_object.y))
            if [pac_object.x, pac_object.y] in initial_pallets_list:
                initial_pallets_list.remove([pac_object.x, pac_object.y])
            if pac_is_dead(pac_object, my_pac_list):
                continue
            pac_object.update_turn(my_pac_list)
            print(f'{str(pac_object.state)}', file=sys.stderr)

            # is there is a defensive aciton to be taken
            # print(f"arg in error{opponent_pac_list}", file=sys.stderr)
            defense_needed, pac_type = pac_object.defensive_mecanism(opponent_pac_list)
            if defense_needed:
                str_move = pac_object.get_defensive_move(pac_type)

            elif str(pac_object.state) == 'ChaseClosestSpecialPallet':
                if pac_object.special_pallet_exist(visible_special_pellet):
                    str_move = pac_object.get_special_pallet_move()
                else:
                    pac_object.on_event('normal_chase')
                    pac_object.refresh_closest_normal_pallet(visible_normal_pellet, initial_pallets_list)
                    str_move = pac_object.get_normal_pallet_move()
            elif str(pac_object.state) == 'ChaseClosestNormalPallet':
                pac_object.refresh_closest_normal_pallet(visible_normal_pellet, initial_pallets_list)
                str_move = pac_object.get_normal_pallet_move()

            new_pac_object_list.append(pac_object)
            order_list.append(str_move)

        output = print_order_list(order_list)
        print(output)

    turn += 1







# for tests
# ####################################################################################
# ####################################################################################

my_pac_list = [{'pac_id': 0, 'mine': True, 'x': 17, 'y': 5, 'type_id': 'NEUTRAL', 'speed_turns_left': 0, 'ability_cooldown': 0}, {'pac_id': 1, 'mine': True, 'x': 27, 'y': 7, 'type_id': 'NEUTRAL', 'speed_turns_left': 0, 'ability_cooldown': 0}]
visible_special_pellet = [[15, 7], [19, 7], [8, 13]]
initial_pellets = {(6, 9), (11, 11), (29, 9), (3, 11), (8, 9), (22, 9), (27, 11), (1, 11), (24, 9), (11, 10), (4, 9), (2, 9), (11, 5), (30, 9), (5, 12), (28, 9), (5, 11), (11, 9), (26, 9), (29, 11), (3, 9), (1, 9), (27, 9), (11, 12), (7, 9), (11, 7), (5, 10), (28, 11), (2, 11), (23, 9), (0, 9), (11, 6)}
pac_object.state




