import sys
sys.path.insert(0, '../')
from planet_wars import issue_order

import logging

def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)

def defend_planet(state):
    fleets_attacking = [fleet for fleet in state.enemy_fleets() if state.planets[fleet.destination_planet].owner == 1]
    message = "\nAll fleets\n" + str(fleets_attacking)
    logging.info(message)
    for fleet in fleets_attacking:
        planet_being_attacked = state.planets[fleet.destination_planet]
        fleets_defending = [fleet.num_ships for fleet in state.my_fleets() if state.planets[fleet.destination_planet].ID == planet_being_attacked.ID]
        total_fleet_defending = sum(fleets_defending)
        needed_fleet = fleet.num_ships - planet_being_attacked.num_ships - \
                       planet_being_attacked.growth_rate * fleet.turns_remaining - total_fleet_defending +1
        message = "\nTesting fleee" + str(fleet) + " " + str(needed_fleet) + " " + str(total_fleet_defending)
        logging.info(message)
        if needed_fleet > 0:
            close_planets = [planet for planet in state.my_planets() if state.distance(planet.ID, planet_being_attacked.ID) < fleet.turns_remaining]
            for close_planet in close_planets:
                max_can_send = min(close_planet.num_ships/3,needed_fleet)
                if max_can_send == 0:
                    continue
                issue_order(state,close_planet.ID,planet_being_attacked.ID,max_can_send)
                needed_fleet -= max_can_send
                if needed_fleet < 0:
                    break
    return False