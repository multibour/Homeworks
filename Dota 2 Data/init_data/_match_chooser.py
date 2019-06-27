import os
import json
import pickle
from functions import *

path = ''
player_to_matches = {}

hero_to_hero_type = {int(key): val for key, val in get_hero_to_hero_type().items()}

#%%

with open(path + 'player_list.txt', 'r') as infile, open(path + 'player_list2.txt', 'r') as infile2:
    valid_player_set = set(json.load(infile) + json.load(infile2))

player_counter = 0
for player_entry in os.scandir(path + 'history'):  # scan all folders (players)
    if player_entry.is_file():
        continue
    if player_counter >= 512:
        break

    hero_types_count = {HeroType.MELEE: set(), HeroType.RANGED: set(), HeroType.STRENGTH: set(),
                        HeroType.INTELLIGENCE: set(), HeroType.AGILITY: set()}

    player_account_id = int(player_entry.name)
    #player_to_matches[player_account_id] = set()

    for match_entry in os.scandir(player_entry.path):  # scan all match data of the player (json files)
        if not match_entry.name.endswith('.json'):
            continue

        # open match file
        with open(match_entry.path, 'r') as infile:
            try:
                match_data = json.load(infile)
            except json.decoder.JSONDecodeError as err:
                infile.close()
                continue

            try:
                player_data = list(filter(lambda x: x['account_id'] == player_account_id, match_data['players'])).pop()
            except IndexError as err:
                print(player_account_id, err)
                continue

        # get types
        try:
            types = hero_to_hero_type[player_data["hero_id"]]
        except KeyError:
            continue

        for t in types:
            if t in hero_types_count:
                hero_types_count[t].add(match_entry.name)

    player_to_matches[player_account_id] = hero_types_count###

    # check if all hero types are included
    for _, val in hero_types_count.items():
        if len(val) == 0:
            del player_to_matches[player_account_id]
            break

    player_counter += 1

    print(player_entry.name)

#%% save
for _, val in player_to_matches.items():
    for key in [HeroType.MELEE, HeroType.RANGED, HeroType.STRENGTH, HeroType.INTELLIGENCE, HeroType.AGILITY]:
        val[key] = list(val[key])

with open('players_to_pick.pkl', 'wb') as outfile:
    pickle.dump(player_to_matches, outfile)

