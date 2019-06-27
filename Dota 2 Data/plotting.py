import matplotlib.pyplot as plt
import numpy as np
import pickle
import math
from functions import *

player_count = 160
match_count = 32
no_hero = True
pca_lda = True

xp_per_min_limit = 0.04
gold_spent_per_min_limit = 0.1
tower_damage_per_min_limit = 0.5
gold_per_min_limit = 0.1


#%% start

with open('init_data/all_features.txt', 'r') as infile:
    all_features = []
    for line in infile.readlines():
        all_features.append(line.strip())

with open('results/' + ('LDA' if pca_lda else 'PCA') + '_model_{}_{}.pkl'.format(player_count, match_count), 'rb') as infile:
    lda = pickle.load(infile)

X = np.load('results/X_{}_{}.npy'.format(player_count, match_count))
nan_counter = set()
for i in range(X.shape[0]):
    for j in range(X.shape[1]):
        if not math.isfinite(X[i, j]):
            X[i, j] = 0.0
            nan_counter.add(i)
print(len(nan_counter))


X_old = X.copy()
old_all_features = all_features.copy()
if no_hero:
    X, all_features = remove_hero_features(X, all_features, all=False)


X_transformed = lda.transform(X)


#-- plot feature-ld --#

selected_features = ['percentage_gold_spent', 'xp_per_min', 'tower_damage_per_min', 'gold_spent_per_min', 'gold_per_min']
colours = ['b', 'r', 'g', 'y', 'm', 'k', 'c']


for feature in selected_features:
    colour = colours.pop()
    index = all_features.index(feature)
    for ld in range(X_transformed.shape[1]):
        if ld > 2:
            break
        plot_x, plot_y = [], []

        for i in range(X.shape[0]):
            plot_x.append(X[i, index])
            plot_y.append(X_transformed[i, ld])

            if (feature == 'xp_per_min' and plot_x[-1] > xp_per_min_limit) \
                    or (feature == 'gold_spent_per_min' and plot_x[-1] > gold_spent_per_min_limit)\
                    or (feature == 'gold_per_min' and plot_x[-1] > gold_per_min_limit)\
                    or (feature == 'tower_damage_per_min' and plot_x[-1] > tower_damage_per_min_limit): # eliminate some noise
                plot_x.pop()
                plot_y.pop()

        ld = ld + 1
        print('plot', feature, 'ld', ld)

        plt.figure()
        plt.plot(plot_x, plot_y, colour + 'o', markersize=0.5)
        plt.title('{} - {}{}'.format(feature, 'LD' if pca_lda else 'PC', ld))
        plt.xlabel(feature)
        plt.ylabel('{}{}'.format('LD' if pca_lda else 'PC', ld))
        plt.savefig(('results/{}_' + ('ld' if pca_lda else 'pc') +'{}.png').format(feature, ld), bbox_inches='tight')


## boxplots of categorical
selected_features = ['hero_durable', 'hero_initiator']

for ld in range(X_transformed.shape[1]):
    if ld > 2:
        break
    for feature in selected_features:
        collections = [[] for _ in selected_features]
        index = all_features.index(feature)

        for i in range(X_old.shape[0]):
            if X_old[i, index] > 0:
                collections[1].append(X_transformed[i, ld])
            else:
                collections[0].append(X_transformed[i, ld])

        print('boxplot categorical ld/pc', ld + 1)
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.boxplot(list(map(lambda x: np.array(x, dtype='float64'), collections)), sym='',
                   labels=(['no durable hero', 'durable hero'] if feature == 'hero_durable' else ['no initiator hero', 'initiator hero']))
        plt.ylabel('{}{}'.format('LD' if pca_lda else 'PC', ld + 1))
        plt.grid(True, axis='y')
        plt.savefig('results/boxplot_' + ('LD' if pca_lda else 'PC') + '{}_{}.png'.format(ld + 1, feature))

#%%
ld = 0
collections = [[], [], []]
greater_tower_index = all_features.index('greater_tower_damage')
greater_hero_index = all_features.index('greater_hero_damage')

for i in range(X_old.shape[0]):
    if X_old[i, greater_tower_index] > 0:
        index = 0
    elif X_old[i, greater_hero_index] > 0:
        index = 2
    else:
        index = 1
    collections[index].append(X_transformed[i, ld])
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.boxplot(list(map(lambda x: np.array(x, dtype='float64'), collections)), sym='',
           labels=['greater tower damage', 'none', 'greater hero damage'])
plt.ylabel('{}{}'.format('LD' if pca_lda else 'PC', ld + 1))
plt.grid(True, axis='y')
plt.savefig('results/boxplot_' + ('LD' if pca_lda else 'PC') + '{}_GREATER.png'.format(ld + 1))


#%% plot boxplots --#
selected_features = ['strength', 'agility', 'intelligence', 'melee', 'range']
hero_strength_index = old_all_features.index('hero_strength')
hero_agility_index = old_all_features.index('hero_agility')
hero_intelligence_index = old_all_features.index('hero_intelligence')
hero_melee_index = old_all_features.index('hero_melee')
hero_range_index = old_all_features.index('hero_range')


for ld in range(X_transformed.shape[1]):
    if ld > 2:
        break
    collections = [[] for _ in selected_features]

    for i in range(X_old.shape[0]):
        if X_old[i, hero_strength_index] > 0:
            index = 0
        elif X_old[i, hero_agility_index] > 0:
            index = 1
        elif X_old[i, hero_intelligence_index] > 0:
            index = 2
        else:
            continue

        collections[index].append(X_transformed[i, ld])

        if X_old[i, hero_melee_index] > 0:
            index = 3
        elif X_old[i, hero_range_index] > 0:
            index = 4
        else:
            index = None

        collections[index].append(X_transformed[i, ld])

    ld = ld + 1

    print('boxplot ld/pc', ld)
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.boxplot(list(map(lambda x: np.array(x, dtype='float64'), collections)), sym='', labels=selected_features)
    plt.ylabel('{}{}'.format('LD' if pca_lda else 'PC', ld))
    plt.grid(True, axis='y')
    plt.savefig('results/boxplot_' + ('LD' if pca_lda else 'PC') + '{}.png'.format(ld))
