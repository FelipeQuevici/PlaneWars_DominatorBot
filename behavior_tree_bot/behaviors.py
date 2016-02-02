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


def spread_to_planets(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    def strength(p):
        return p.num_ships \
               - sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) \
               + sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)


    neutral_planets = [(planet, strength(planet)) for planet in state.neutral_planets() if strength(planet) > 0]
    logging.info("Criout " + str(neutral_planets))
    neutral_planets.sort(key=lambda x: state.planets[x[0].ID].num_ships)
    logging.info("Ordenou " + str(neutral_planets))
    target_planets = iter(neutral_planets)

    try:
        my_planet = next(my_planets)
        target_planet, target_planet_strength = next(target_planets)
        logging.info("Teste 2" + str(target_planet) + str(target_planet_strength))
        while True:
            required_ships = target_planet_strength + 1
            logging.info("ship" + str(target_planet) + str(target_planet_strength))
            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet,target_planet_strength = next(target_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        return True


def defend_planet(state):
    fleets_attacking = [fleet for fleet in state.enemy_fleets() if state.planets[fleet.destination_planet].owner == 1]
    fleets_destinations = [fleet.destination_planet for fleet in fleets_attacking]
    planets_not_being_attacked = [planet for planet in state.my_planets() if planet.ID not in fleets_destinations]
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
            close_planets = [planet for planet in planets_not_being_attacked if state.distance(planet.ID, planet_being_attacked.ID) < fleet.turns_remaining]
            for close_planet in close_planets:
                max_can_send = min(close_planet.num_ships/3,needed_fleet)
                if max_can_send == 0:
                    continue
                issue_order(state,close_planet.ID,planet_being_attacked.ID,max_can_send)
                needed_fleet -= max_can_send
                if needed_fleet < 0:
                    break
    return False