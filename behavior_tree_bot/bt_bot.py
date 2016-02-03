#!/usr/bin/env python
#

"""
// The do_turn function is where your code goes. The PlanetWars object contains
// the state of the game, including information about all planets and fleets
// that currently exist.
//
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn


def setup_behavior_tree():
    # Top-down construction of behavior tree
    root = Selector(name='High Level Ordering of Strategies')


    defensive_plan = Sequence(name="Defensive Plan")
    defend_being_attacked = Check(enemy_attacking)
    defend_planets = Action(defend_planet)
    defend_losing = Check(losing_enemy)
    defend_abandon = Action(abandon_planet)
    defensive_plan.child_nodes = [defend_being_attacked,defend_planets,defend_losing, defend_abandon]

    '''offensive_plan = Sequence(name='Offensive Strategy')
    largest_fleet_check = Check(have_largest_fleet)
    attack = Action(attack_weakest_enemy_planet)
    offensive_plan.child_nodes = [largest_fleet_check, attack]'''

    greedy_a_behavior = Sequence(name='Greedy Attack')
    greedy_a_check = Check(outnumebering_enemy)
    greedy_a_attack = Action(coordinate_attack_on_enemy)
    greedy_a_behavior.child_nodes = [greedy_a_check,greedy_a_attack]

    inter_a_behavior = Sequence(name="Intermediate Attack")
    inter_a_check = Check(winning_few_enemy)
    inter_a_attack = Action(attack_enemy)
    inter_a_behavior.child_nodes = [inter_a_check,inter_a_attack]

    caut_a_behavior = Sequence(name="Cautious Attack")
    caut_a_check = Check(losing_enemy)
    caut_a_attack = Action(attack_enemy)
    caut_a_behavior.child_nodes = [caut_a_check, caut_a_attack]

    offensive_plan = Selector(name='Offensive Strategy')
    offensive_plan.child_nodes = [greedy_a_behavior,inter_a_behavior,caut_a_behavior]





    spread_sequence = Sequence(name='Spread Strategy')
    neutral_planet_check = Check(if_neutral_planet_available)
    spread_nearby = Action(spread_to_nearby_planets)
    spread_action = Action(spread_to_planets)
    spread_sequence.child_nodes = [neutral_planet_check, spread_nearby, spread_action]

    '''spread_sequence = Sequence(name='Spread Strategy')
    neutral_planet_check = Check(if_neutral_planet_available)
    spread_action = Action(spread_to_weakest_neutral_planet)
    spread_sequence.child_nodes = [neutral_planet_check, spread_action]'''

    root.child_nodes = [defensive_plan,offensive_plan,spread_sequence]

    logging.info('\n' + root.tree_to_string())
    return root


if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)
    from timeit import default_timer as time
    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                start = time()
                planet_wars = PlanetWars(map_data)
                behavior_tree.execute(planet_wars)
                finish_turn()
                timeelapsed = time() - start
                logging.info("TIME TURNO:" + str(timeelapsed))
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
