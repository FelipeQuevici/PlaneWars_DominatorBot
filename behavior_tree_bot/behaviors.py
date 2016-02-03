import sys
from math import inf, ceil
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


def abandon_planet(state):
    fleets_destinations = [fleet.destination_planet for fleet in state.enemy_fleets()]
    planets_being_attacked = [planet for planet in state.my_planets() if planet.ID in fleets_destinations]
    for planet in planets_being_attacked:
        fleets_defending = [fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == planet.ID]
        fleets_defending_total = sum(fleets_defending)
        fleets_attacking = [fleet for fleet in state.enemy_fleets() if state.planets[fleet.destination_planet].ID == planet.ID]
        fleets_attacking.sort(key=lambda x: x.turns_remaining)
        total_defense = fleets_attacking[0].turns_remaining*planet.growth_rate + planet.num_ships + fleets_defending_total - fleets_attacking[0].num_ships
        message = "Sera que precisa?"+str(fleets_defending) + " " + str(fleets_attacking) + " " + str(total_defense)
        logging.info(message)
        if total_defense < 0:
            logging.info("ALGUM PLANETA DEVERIA SER ABANDONADO")
            other_planets = [p for p in state.my_planets() if p.ID != planet.ID]
            if other_planets:
                closest = min(other_planets,key=lambda x: state.distance(planet.ID, x.ID))
                issue_order(state, planet.ID, closest.ID, planet.num_ships)
    return False

def coordinate_attack_on_enemy(state):
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships)

    enemy_planets = [planet for planet in state.enemy_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    enemy_planets.sort(key=lambda p: p.num_ships)

    target_planets = iter(enemy_planets)

    '''my_fleet_size = sum(planet.num_ships for planet in state.my_planets()) \
                    + sum(fleet.num_ships for fleet in state.my_fleets())

    local_planets = []
    enemy_distances = {}

    plausible_target = []'''


    try:
        target_planet = next(target_planets)
        while True:
            closest_enemy_allies = get_neighbors_within(state, target_planet, enemy_planets, inf)
            radius = inf
            if len(closest_enemy_allies) != 0:
                radius = closest_enemy_allies[0][1]
            logging.error("cea: " + str(closest_enemy_allies))
            logging.error("enemy planets: " + str(enemy_planets))
            logging.error("target planet: " + str(target_planet))
            best_offesive_planets = get_neighbors_within(state, target_planet, my_planets, radius)
            if len(best_offesive_planets) > 0:
                required_ships = 0
                if radius == inf:
                    required_ships = target_planet.num_ships + \
                                 state.distance(best_offesive_planets[-1][0].ID, target_planet.ID) * target_planet.growth_rate + 1
                else:
                    required_ships = target_planet.num_ships + \
                                 state.distance(closest_enemy_allies[0][0].ID, target_planet.ID) * target_planet.growth_rate + 1
                offesive_planets_scored = score_planets_contributions(state, best_offesive_planets, required_ships)
                for offesive_planet in offesive_planets_scored:
                    issue_order(state, offesive_planet[0].ID, target_planet.ID, offesive_planet[1])
            target_planet = next(target_planets)

    except StopIteration:
        return False
    '''
    #check if there is an enemy planet near one of ours that meets our
    #evaluation Function




    for enemy_planet in enemy_planets:
        ships = enemy_planet.num_ships
        growth_rate = enemy_planet.growth_rate

        nearest_enemy_ally = (None, inf)
        for other_enemy_planet in enemy_planets:
            if enemy_planet == other_enemy_planet:
                continue
            if nearest_enemy_ally[1] > state.distance()'''

def get_neighbors_within(state, target_planet, planet_set, radius):
    neighbors = []
    for planet in planet_set:
        logging.error("planet: " + str(planet))
        if planet.ID == target_planet.ID:
            continue
        distance = state.distance(target_planet.ID, planet.ID)
        if  distance < radius:
            neighbors.append((planet, distance))

    sorted(neighbors)
    return neighbors

def score_planets_contributions(state, planet_set, coalition_size_needed):
    scored_planets = []
    ready_planets = []
    total_ships_ready = 0
    for planet in planet_set:
        logging.error("planet: " + str(planet))
        if is_under_attack(state, planet):
            continue
        total_ships_ready += planet[0].num_ships
        ready_planets.append(planet[0])

    for planet in ready_planets:
        logging.error("planet2: " + str(planet))
        contribution_ratio = planet.num_ships / total_ships_ready
        contributions = ceil(planet.num_ships * contribution_ratio)
        scored_planets.append((planet, contributions))

    return scored_planets

def is_under_attack(state, planet):
    fleets_attacking = [fleet for fleet in state.enemy_fleets() if state.planets[fleet.destination_planet].owner == 1]
    fleets_destinations = [fleet.destination_planet for fleet in fleets_attacking]
    if planet in fleets_destinations:
        return True
    return False


def attack_enemy(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    enemy_planets = [planet for planet in state.enemy_planets()
                      if not any(fleet.destination_planet == planet.ID for fleet in state.my_fleets())]
    enemy_planets.sort(key=lambda p: p.num_ships)

    target_planets = iter(enemy_planets)

    try:
        my_planet = next(my_planets)
        target_planet = next(target_planets)
        while True:
            def strength(p, turns):
                return p.num_ships + turns * p.growth_rate \
                    - sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) \
                    + sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)

            required_ships = target_planet.num_ships + state.distance(my_planet.ID, target_planet.ID) * target_planet.growth_rate + 1

            if my_planet.num_ships > required_ships:
                issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet = next(target_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        return False


def spread_to_planets(state):
    my_planets = iter(sorted(state.my_planets(), key=lambda p: p.num_ships))

    def strength(p):
        return p.num_ships \
               - sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) \
               + sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)

    neutral_planets = [(planet, strength(planet)) for planet in state.neutral_planets() if strength(planet) > 0]
    neutral_planets.sort(key=lambda x: state.planets[x[0].ID].num_ships)
    target_planets = iter(neutral_planets)

    possible_actions = []

    try:
        my_planet = next(my_planets)
        target_planet, target_planet_strength = next(target_planets)
        while True:
            required_ships = target_planet_strength + 1
            if my_planet.num_ships > required_ships:
                possible_actions.append((my_planet,target_planet,required_ships,state.distance(my_planet.ID,target_planet.ID)))
                #issue_order(state, my_planet.ID, target_planet.ID, required_ships)
                my_planet = next(my_planets)
                target_planet,target_planet_strength = next(target_planets)
            else:
                my_planet = next(my_planets)

    except StopIteration:
        if possible_actions:
            def ordenation(x):
                result = x[2]/x[3]
                return result
            possible_actions.sort(key=ordenation)
            for action in possible_actions:
                if action[0].num_ships > action[2]:
                    issue_order(state,action[0].ID,action[1].ID,action[2])

        return True


def defend_planet(state):
    fleets_attacking = [fleet for fleet in state.enemy_fleets() if state.planets[fleet.destination_planet].owner == 1]
    fleets_destinations = [fleet.destination_planet for fleet in fleets_attacking]
    planets_not_being_attacked = [planet for planet in state.my_planets() if planet.ID not in fleets_destinations]
    for fleet in fleets_attacking:
        planet_being_attacked = state.planets[fleet.destination_planet]
        fleets_defending = [fleet.num_ships for fleet in state.my_fleets() if state.planets[fleet.destination_planet].ID == planet_being_attacked.ID]
        total_fleet_defending = sum(fleets_defending)
        needed_fleet = fleet.num_ships - planet_being_attacked.num_ships - \
                       planet_being_attacked.growth_rate * fleet.turns_remaining - total_fleet_defending +1
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
    return True