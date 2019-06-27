import numpy as np
import json
import pandas as pd
import pickle
import csv
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
from sklearn.ensemble import ExtraTreesClassifier
import matplotlib.pyplot as plt
import dota2api
from enum import IntEnum


#%% -- Unused -- #

api = dota2api.Initialise('FBDD03E6BC1551712A95120920202C50')


def remove_from_player_waiting_list(id):
    with open('player_waiting_list.txt', 'r') as f:
        waiting_list = json.load(f)
    waiting_list.remove(id)
    with open('player_waiting_list.txt', 'w') as f:
        json.dump(waiting_list, f)


def get_player_waiting_list():
    with open('player_waiting_list.txt', 'r') as f:
        return json.load(f)


def get_player_list(pre=''):
    with open(pre + 'player_list.txt', 'r') as infile:
        return json.load(infile)


def get_matches_from_file(account_id):
    with open('history/{}.json'.format(account_id), 'r') as f:
        return json.load(f)


def get_match_details(match_id):
    details = None
    while details is None:
        try:
            details = api.get_match_details(match_id=match_id)
        except Exception as e:
            print("Exception thrown:", e)
            sleep(7)
    return details


#%% -- Used -- #


def get_feature_importance(x, y, features):
    forest = ExtraTreesClassifier(max_depth=10, random_state=0)
    forest.fit(x, y)
    importance = list(zip(features, forest.feature_importances_))
    importance.sort(key=lambda element: element[-1], reverse=True)
    return importance


def create_coefficient_table(lda=None, pca=None, features=None):
    if lda is not None:
        linear_coefficients = lda.scalings_[:, :lda._max_components]
    elif pca is not None:
        linear_coefficients = pca.components_.T
    else:
        return None
    coefficient_table = dict()

    for dim in range(linear_coefficients.shape[1]):
        dim_n = dim + 1
        coefficient_table[dim_n] = dict()

        for index in range(linear_coefficients.shape[0]):
            coefficient_table[dim_n][features[index]] = linear_coefficients[index, dim]

    return coefficient_table


def plot_dimensions(transformed, y, dim1=0, dim2=1, pca_lda=True):
    labels = np.unique(y)
    params = []
    symbols = [x + y for y in ('.', '+', 'x', '^', 'D') for x in ('b', 'r', 'g', 'c', 'm', 'y', 'k')] #h

    for index in range(labels.shape[0]):
        indices = (y == labels[index])
        params.append(transformed[indices, dim1])
        params.append(transformed[indices, dim2])
        try:
            params.append(symbols[index])
        except IndexError:
            params.pop()
            params.pop()
            break

    d = 'LD' if pca_lda else 'PC'
    plt.figure()
    plt.xlabel(d + str(dim1 + 1))
    plt.ylabel(d + str(dim2 + 1))
    plt.plot(*params, markersize=5)
    plt.show()


def calculate_plot_pca(x, y, features, n_components=8, svd_solver='auto', counts=(1024, 100), prefix='results\\'):
    pca = PCA(n_components=n_components, svd_solver=svd_solver)

    x_transformed = pca.fit_transform(x)
    coefficient_table = create_coefficient_table(pca=pca, features=features)

    with open(prefix + 'PCA_model_{}_{}.pkl'.format(*counts), 'wb') as outfile:
        pickle.dump(pca, outfile)

    plot_dimensions(x_transformed, y, pca_lda=False)
    print('pca variance:', pca.explained_variance_ratio_)

    pd.DataFrame(pca.explained_variance_ratio_)\
        .rename(lambda n: 'PC' + str(n+1), axis='index')\
        .rename(columns={0: '% Variance'})\
        .to_csv(prefix + 'pca_variance_{}_{}.csv'.format(*counts))

    return x_transformed, coefficient_table


def calculate_plot(x, y, features, n_components=8, counts=(1024, 100), prefix='results\\'):
    clf = LinearDiscriminantAnalysis(n_components=n_components, store_covariance=True)

    x_transformed = clf.fit_transform(x, y)
    coefficient_table = create_coefficient_table(lda=clf, features=features)
    feature_importance = get_feature_importance(x, y, features=features)

    with open(prefix + 'LDA_model_{}_{}.pkl'.format(*counts), 'wb') as outfile:
        pickle.dump(clf, outfile)

    plot_dimensions(x_transformed, y)
    print('lda variance:', clf.explained_variance_ratio_)
    print('lda covariance', clf.covariance_)

    mapper = {x: y for x, y in zip(range(len(features)), features)}
    D = np.sqrt(np.diag(clf.covariance_))
    pd.DataFrame(np.divide(np.divide(clf.covariance_, D), np.transpose(D)))\
        .replace(to_replace=[np.nan, np.inf, -np.inf], value=[0., 0., 0.])\
        .rename(index=mapper, columns=mapper)\
        .to_csv(prefix + 'correlation_{}_{}.csv'.format(*counts))

    pd.DataFrame(clf.explained_variance_ratio_)\
        .rename(lambda n: 'LD' + str(n+1), axis='index')\
        .rename(columns={0: '% Variance'})\
        .to_csv(prefix + 'variance_{}_{}.csv'.format(*counts))

    return x_transformed, coefficient_table, feature_importance


def write_influential_coefficients_to_file(coefficient_table, filename):
    with open(filename, 'w') as outfile:
        for dimension, coefficients in coefficient_table.items():
            print('dimension:', dimension)
            outfile.write('dimension: ' + str(dimension) + '\n')
            for f, c in sorted(list(coefficients.items()), key=lambda x: x[-1], reverse=True):
                outfile.write(f + ' (' + '{0:.5f}'.format(c) + ')\n')
            outfile.write('\n\n')


def create_influential_coefficients_csv(coefficient_table, filename, threshold, pca_lda=True):
    def to_readable(t):
        return t[0] + ' ({0:.5f})'.format(t[1])

    with open(filename, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Dimension', 'Positive Coefficients', 'Negative Coefficients'])

        for dimension, coefficients in coefficient_table.items():
            dim_identifier = ('LD' if pca_lda else 'PC') + str(dimension)
            positives = sorted([(f, c) for f, c in coefficients.items() if c >= threshold], key=lambda x: x[-1], reverse=True)
            negatives = sorted([(f, c) for f, c in coefficients.items() if c <= -threshold], key=lambda  x: x[-1])

            common = min(len(positives), len(negatives))
            for i in range(common):
                writer.writerow([dim_identifier, to_readable(positives[i]), to_readable(negatives[i])])
            if len(positives) > len(negatives):
                for i in range(common, len(positives)):
                    writer.writerow([dim_identifier, to_readable(positives[i]), ''])
            elif len(positives) < len(negatives):
                for i in range(common, len(negatives)):
                    writer.writerow([dim_identifier, '', to_readable(negatives[i])])

#####

to_convert = {'assists', 'deaths', 'denies', 'gold_spent', 'hero_damage', 'hero_healing',
              'kills', 'last_hits', 'level', 'tower_damage'}
team_items = {94, 86, 92, 187, 180, 185, 79, 81, 90, 231, 229, 102, 254, 88, 212, 242, 226}
individualistic_items = {65, 247, 104, 201, 202, 203, 204, 235, 149, 152, 145, 135, 137, 141, 139,
                         131, 125, 147, 114, 172, 236, 156, 162, 170, 154, 166, 158, 252}

def iterate_item_types(item_id):
    if item_id in team_items:
        yield 0
    if item_id in individualistic_items:
        yield 1

def convert_to_per_min(duration, features1, temp_row):
    index = 0
    for feature in features1:
        if feature in to_convert:
            temp_row[0, index] /= duration
        index += 1

def convert_features_to_per_min(features1):
    features1_copy = list(features1)

    index = 0
    for feature in features1:
        if feature in to_convert:
            features1_copy[index] += '_per_min'
        index += 1

    return tuple(features1_copy)


# HERO CLASSIFICATION #

class HeroType(IntEnum):
    # attack type
    MELEE = 0
    RANGED = 1
    # player role
    CARRY = 2
    DISABLER = 3
    INITIATOR = 4
    JUNGLER = 5
    SUPPORT = 6
    DURABLE = 7
    NUKER = 8
    PUSHER = 9
    ESCAPE = 10
    # player category
    STRENGTH = 11
    AGILITY = 12
    INTELLIGENCE = 13


def get_hero_to_hero_type(filename='init_data\\hero_features.json'):
    with open(filename, 'r') as infile:
        hero_to_hero_type = json.load(infile)
    return hero_to_hero_type

def get_item_builds(filename='..\\item_builds.json'):
    with open(filename, 'r') as infile:
        item_builds = json.load(infile)
    return item_builds

def remove_hero_features(x, all_features, all=True):
    if all:
        hero_type_features = set('hero_' + s.lower() for s in ['MELEE', 'RANGE', 'CARRY', 'DISABLER',
                                                               'INITIATOR', 'JUNGLER', 'SUPPORT',
                                                               'DURABLE', 'NUKER', 'PUSHER', 'ESCAPE', 'STRENGTH',
                                                               'AGILITY', 'INTELLIGENCE'])
    else:
        hero_type_features = set('hero_' + s.lower() for s in ['MELEE', 'RANGE', 'STRENGTH', 'AGILITY', 'INTELLIGENCE'])

    indexes_to_remove = []
    indices = [s for s in range(len(all_features))]
    for ht in hero_type_features:
        indexes_to_remove.append(all_features.index(ht))
        indices.remove(all_features.index(ht))

    all_features = list(filter(lambda s: s not in hero_type_features, all_features))
    x = x[:, indices]

    return x, all_features
