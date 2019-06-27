import numpy as np
import json
import os
import math
import pickle
import zipfile
from sklearn.preprocessing import MinMaxScaler, MaxAbsScaler, StandardScaler
from functions import *


features0 = ()
features1 = ('assists', 'deaths', 'denies', 'gold_per_min', 'gold_spent', 'hero_damage', 'hero_healing',
             'kills', 'last_hits', 'level', 'tower_damage', 'xp_per_min')
categorical_leaver_status = tuple()#('none_leaver_status', 'disconnected', 'disconnected_too_long', 'abandoned', 'afk',)
                             #'never_connected', 'never_connected_too_long')
hero_type_features = tuple('hero_' + s.lower() for s in ['MELEE', 'RANGE', 'CARRY', 'DISABLER', 'INITIATOR', 'JUNGLER',
                                                         'SUPPORT', 'DURABLE', 'NUKER', 'PUSHER', 'ESCAPE', 'STRENGTH',
                                                         'AGILITY', 'INTELLIGENCE'])
item_features = tuple('item_' + s for s in ['team', 'individualistic', 'default'])
custom_features = ('percentage_gold_spent', 'lose/win', 'leaving_tendency', 'greater_hero_damage', 'greater_tower_damage')

prefix_path = 'data\\'
MAX_PLAYERS = 160
MAX_MATCHES = 32


#%% MAIN #####

hero_to_hero_type = {int(key): val for key, val in get_hero_to_hero_type().items()}
item_builds = {int(key): set(val) for key, val in get_item_builds().items()}
leaver_status_to_leaving_tendency = [0, 1, 2, 3, 3]

zip_file = zipfile.ZipFile('matches_{}_{}.zip'.format(MAX_PLAYERS, MAX_MATCHES), 'w')

n_features_only_numeric = len(features0) + len(features1)
n_features = n_features_only_numeric + len(categorical_leaver_status) + len(HeroType) + len(item_features) + len(custom_features)

X = np.zeros((MAX_PLAYERS * MAX_MATCHES, n_features), dtype='float64')
Y = np.zeros((MAX_PLAYERS * MAX_MATCHES,), dtype='uint32')
Z = np.zeros((MAX_PLAYERS * MAX_MATCHES,), dtype='uint32')

# get player list
with open(prefix_path + 'player_list.txt', 'r') as infile, open(prefix_path + 'player_list2.txt', 'r') as infile2:
    valid_player_set = set(json.load(infile) + json.load(infile2))

# get matches to choose
choose_specific_players = True
with open('init_data\\players_to_pick.pkl', 'rb') as infile:
    players_to_hero_type_to_matches = pickle.load(infile)

#%% scan players

player_counter = 0
for player_entry in os.scandir(prefix_path + 'history'):  # scan all folders (players)
    if player_entry.is_file():
        continue

    player_account_id = int(player_entry.name)

    if player_account_id not in valid_player_set\
            or (choose_specific_players and player_account_id not in players_to_hero_type_to_matches):
        continue
    if player_counter == MAX_PLAYERS:
        break

    # scan matches of the player
    match_counter = 0
    used_matches = set()
    for i in range(max([len(v) for _, v in players_to_hero_type_to_matches[player_account_id].items()])):
        break_loop = False

        for match_file in [(v[i] if i < len(v) else None) for _, v in players_to_hero_type_to_matches[player_account_id].items()]:
            if match_file in used_matches or match_file is None:
                continue
            if match_counter >= MAX_MATCHES:
                break_loop = True
                break
            used_matches.add(match_file)

            # open match file
            with open(player_entry.path + '\\' + match_file, 'r') as infile:
                try:
                    match_data = json.load(infile)
                except json.decoder.JSONDecodeError as err:
                    # print('json decode err', err, '\nplayer:', player_entry.name, '\nmatch:', match_entry.name)
                    infile.close()
                    continue

                try:
                    player_data = list(filter(lambda x: x['account_id'] == player_account_id, match_data['players'])).pop()
                except IndexError as err:
                    print(player_account_id)
                    print(err)

                with zip_file.open('{}\\{}'.format(player_entry.name, match_file), 'w') as infile2:
                    infile2.write(json.dumps(match_data, indent=4).encode('utf-8'))

            # get player's play duration
            duration = (match_data['duration'] + 1) / 60.0

            # initialise feature row
            temp_row = np.zeros((1, n_features), dtype=float)

            # player performance data
            for index in range(len(features1)):
                try:
                    temp_row[0, index] = player_data[features1[index]]
                except KeyError as err:
                    print('player performance', err, player_account_id)

            # player's leaver status (categorical)
            #temp_row[0, n_features_only_numeric + player_data['leaver_status']] = 1

            # player's hero's features
            try:
                for index in hero_to_hero_type[player_data['hero_id']]:
                    temp_row[0, n_features_only_numeric + len(categorical_leaver_status) + index] = 1
            except KeyError as err:
                print('hero feature', err)

            # player's items' types
            for item in ['item_0', 'item_1', 'item_2', 'item_3', 'item_4', 'item_5']:
                item_id = player_data[item]
                for index in iterate_item_types(item_id):
                    temp_row[0, n_features_only_numeric + len(categorical_leaver_status) + len(HeroType) + index] += 1
                try:
                    if item_id in item_builds[player_data['hero_id']]:
                        temp_row[0, n_features_only_numeric + len(categorical_leaver_status) + len(HeroType) + 2] += 1
                except KeyError as err:
                    print('item', err)
                    break

            # generate custom features
            index = n_features_only_numeric + len(categorical_leaver_status) + len(HeroType) + len(item_features)
            try:
                temp_row[0, index] = player_data['gold_spent'] / (player_data['gold'] + player_data['gold_spent'] + 1)
            except KeyError:
                pass

            index = index + 1
            if player_data["player_slot"] >= 0b10000000:  # if dire
                temp_row[0, index] = 0 if match_data["radiant_win"] else 1
            else:  # radiant
                temp_row[0, index] = 1 if match_data["radiant_win"] else 0

            index = index + 1
            temp_row[0, index] = leaver_status_to_leaving_tendency[player_data['leaver_status']]

            index = index + 1
            if int(player_data.get("hero_damage") or 0) > 8 * int(player_data.get("tower_damage") or 0):
                temp_row[0, index] = 1
            elif int(player_data.get("hero_damage") or 0) < 8 * int(player_data.get("tower_damage") or 0):
                temp_row[0, index + 1] = 1

            # convert some features to 'per minute'
            convert_to_per_min(duration, features1, temp_row)

            # put row to matrix
            X[player_counter * MAX_MATCHES + match_counter, :] = temp_row
            Y[player_counter * MAX_MATCHES + match_counter] = player_account_id
            Z[player_counter * MAX_MATCHES + match_counter] = int(match_data['match_id'])

            match_counter += 1
        #end of inner match for loop

        # if max matches have been reached
        if break_loop:
            break
    #end of outer match loop

    if match_counter < MAX_MATCHES:
        print('fail')
        continue

    print('player counter:', player_counter)
    player_counter += 1
# end of extraction

features1 = convert_features_to_per_min(features1)
all_features = features1 + categorical_leaver_status + hero_type_features + item_features + custom_features

zip_file.close()

#%% scaling
nan_counter = set()
for i in range(X.shape[0]):
    for j in range(X.shape[1]):
        if not math.isfinite(X[i, j]):
            X[i, j] = 0.0
            nan_counter.add(i)
print(len(nan_counter)); del nan_counter

X = StandardScaler().fit_transform(X)
X = MinMaxScaler((0, 1)).fit_transform(X)

#%% save
print('finished extraction')
np.save('results\\X_{}_{}.npy'.format(player_counter, MAX_MATCHES), X)
np.save('results\\Y_{}_{}.npy'.format(player_counter, MAX_MATCHES), Y)
np.save('results\\Z_{}_{}.npy'.format(player_counter, MAX_MATCHES), Z)

with open('init_data\\all_features.txt', 'w') as outfile:
    outfile.write('\n'.join(all_features))

# put x to excel

import pandas as pd
pd.DataFrame(X)\
    .rename(columns={i: j for i, j in zip(range(len(all_features)), all_features)})\
    .to_csv('results\\raw_{}_{}.csv'.format(player_counter, MAX_MATCHES))
