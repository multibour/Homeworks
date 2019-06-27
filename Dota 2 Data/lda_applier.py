import numpy as np
import math
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from functions import *


features1 = ('assists_per_min', 'deaths_per_min', 'denies_per_min', 'gold_per_min', 'gold_spent_per_min', 'hero_damage_per_min', 'hero_healing_per_min',
             'kills_per_min', 'last_hits_per_min', 'level_per_min', 'tower_damage_per_min', 'xp_per_min')
categorical_leaver_status = ('none_leaver_status', 'disconnected', 'disconnected_too_long', 'abandoned', 'afk',)
                             #'never_connected', 'never_connected_too_long')
hero_type_features = tuple('hero_' + s.lower() for s in ['MELEE', 'RANGE', 'CARRY', 'DISABLER', 'INITIATOR', 'JUNGLER',
                                                         'SUPPORT', 'DURABLE', 'NUKER', 'PUSHER', 'ESCAPE', 'STRENGTH',
                                                         'AGILITY', 'INTELLIGENCE'])
item_features = tuple('item_' + s for s in ['team', 'individualistic', 'default'])
custom_features = ('percentage_gold_spent', 'lose/win')

all_features = list(features1 + categorical_leaver_status + hero_type_features + item_features + custom_features)

with open('init_data\\all_features.txt', 'r') as infile:
    all_features = []
    for line in infile.readlines():
        all_features.append(line.strip())

#####

clf = LinearDiscriminantAnalysis(n_components=8)

N = 160
M = 32
no_hero = True
pca_lda = True

#####

X = np.load('results\\X_{}_{}.npy'.format(N, M))
Y = np.load('results\\Y_{}_{}.npy'.format(N, M))

nan_counter = set()
for i in range(X.shape[0]):
    for j in range(X.shape[1]):
        if not math.isfinite(X[i, j]):
            X[i, j] = 0.0
            nan_counter.add(i)
print(len(nan_counter))

if X.shape[1] != len(all_features):
    raise Exception('sizes do no match')


#%% remove hero type features
if no_hero:
    X, all_features = remove_hero_features(X, all_features, all=False)

#%% apply lda/pca

if pca_lda:
    X_transformed, coefficient_table, feature_importance = calculate_plot(X, Y, features=all_features, counts=(N, M))

    with open('feature_importance_player_data_{}_{}.txt'.format(N, M), 'w') as outfile:
        for feature, importance in feature_importance:
            outfile.write('{} : {}\n'.format(feature, importance))

    write_influential_coefficients_to_file(coefficient_table, filename='results\\influential_coefficients_{}_{}.txt'.format(N, M))

else:
    X_transformed_pca, coefficient_table = calculate_plot_pca(X, Y, n_components=8, features=all_features, counts=(N, M))
    write_influential_coefficients_to_file(coefficient_table, filename='results\\influential_coefficients_pca_{}_{}.txt'.format(N, M))

th = float(input('give threshold: '))
create_influential_coefficients_csv(coefficient_table,
                                    'results\\influential_coefficients_' + ('lda' if pca_lda else 'pca') + '.csv',
                                    threshold=th, pca_lda=pca_lda)

