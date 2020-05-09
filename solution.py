
# https://dev.to/karn/building-a-simple-state-machine-in-python


class State(object):
    """
    We define a state object which provides some utility functions for the
    individual states within the state machine.
    """

    def __init__(self):
        print('Processing current state:', str(self))

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

    def refresh_closest_normal_pallet(self, visible_normal_pellet):

        node = [self.x, self.y]
        best_pac_coordonate, pac_index = closest_node(node, visible_normal_pellet)

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


device = SimpleDevice(pac_type='neutral')

device.on_event('device_locked')
device.on_event('pin_entered')

device.state


device.on_event('device_locked')

device.state

device.on_event('device_locked')



# todo define the states the pac can be in (exemple search for the biggest// no biggest in sight)
# todo or search the closest dfs, etc
# todo add a is_stuck_method that run every turn // easy by checking new params with old attributes



import numpy as np

def print_order_list(order_list):
    char_print = ''
    for orders in order_list:
        if char_print == '':
            char_print = orders
        else:
            char_print += "| " + orders
    return char_print


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



# ####################################################################################
# ####################################################################################

my_pac_list = [{'pac_id': 0, 'mine': True, 'x': 17, 'y': 5, 'type_id': 'NEUTRAL', 'speed_turns_left': 0, 'ability_cooldown': 0}, {'pac_id': 1, 'mine': True, 'x': 27, 'y': 7, 'type_id': 'NEUTRAL', 'speed_turns_left': 0, 'ability_cooldown': 0}]
visible_special_pellet = [[15, 7], [19, 7], [8, 13]]

# assignement of the pacs (first round)
allocated_pacs = allocate_pacs(visible_special_pellet, my_pac_list)

pac_object_list = []
order_list = []
for pac in allocated_pacs:
    x = pac['pac_coordonate'][0]
    y = pac['pac_coordonate'][1]
    pac_id = pac['pac_id']
    speed_turns_left = -1
    ability_cooldown = -1
    special_pallet = True
    x_special_pallet = pac['special_pellet'][0]
    y_special_pallet = pac['special_pellet'][1]
    special_pallet_location = []

    pac_object = SimpleDevice(x, y, x_special_pallet, y_special_pallet, pac_id, speed_turns_left, ability_cooldown, special_pallet, special_pallet_location)
    str_move = pac_object.get_special_pallet_move()

    pac_object_list.append(pac_object)
    order_list.append(str_move)

print_order_list(order_list)


# #################
# normal turn, we get 1-information of special pallets outstanding // check if we change states
new_pac_object_list = []
order_list = []
for pac_object in pac_object_list:

    pac_object.update_turn()
    if pac_object.state.__class__.__name_ == 'ChaseClosestSpecialPallet':
        if pac_object.special_pallet_exist():
            str_move = pac_object.get_special_pallet_move()
        else:
            pac_object.on_event('normal_chase')
            pac_object.refresh_closest_normal_pallet()
            str_move = pac_object.get_normal_pallet_move()
    elif pac_object.state.__class__.__name_ == 'ChaseClosestNormalPallet':
        pac_object.refresh_closest_normal_pallet()
        str_move = pac_object.get_normal_pallet_move()

    new_pac_object_list.append(pac_object)
    order_list.append(str_move)

print_order_list(order_list)







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

