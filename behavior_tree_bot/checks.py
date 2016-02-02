

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())


def outnumebering_enemy(state):
    my_fleets = sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets())
    enemy_fleets = sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

    reason = (my_fleets+1)/(enemy_fleets+1)
    return reason >= 2


def winning_few_enemy(state):
    my_fleets = sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets())
    enemy_fleets = sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

    reason = (my_fleets+1)/(enemy_fleets+1)
    return 2 > reason >= 1


def losing_enemy(state):
    my_fleets = sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets())
    enemy_fleets = sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

    reason = (my_fleets+1)/(enemy_fleets+1)
    import logging
    logging.info("Perdendo?" + str(reason))
    return 1 > reason


def enemy_attacking(state):
    return [fleet for fleet in state.enemy_fleets() if state.planets[fleet.destination_planet].owner == 1] != []