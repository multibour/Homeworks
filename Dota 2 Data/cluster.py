from sklearn.cluster import KMeans
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import pickle
import zipfile
from statistics import mean
import math
from functions import *

plt.rcParams.update({'figure.max_open_warning': 0})

colours = ['b', 'r', 'g', 'y', 'k', 'c', 'm', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:orange']

M = 160
N = 32
pca_lda = True
no_hero = True

take_centroids = False

#%%

prefix_path = 'results'

with open(prefix_path + '..\\init_data\\all_features.txt', 'r') as infile:
    all_features = []
    for line in infile.readlines():
        all_features.append(line.strip())

with open(prefix_path + ('LDA' if pca_lda else 'PCA') + '_model_{}_{}.pkl'.format(M, N), 'rb') as infile:
    X = np.load(prefix_path + 'X_{}_{}.npy'.format(M, N))

    nan_counter = set()
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            if not math.isfinite(X[i, j]):
                X[i, j] = 0.0
                nan_counter.add(i)
    print(len(nan_counter))

    if no_hero:
        X, all_features = remove_hero_features(X, all_features, all=False)

    X_transformed = pickle.load(infile).transform(X)
del i, j, nan_counter, infile

ld_12 = X_transformed[:, :2]
ld_123 = X_transformed[:, :3]

print('dim 1-4 cor:', np.corrcoef(X_transformed[:, 0], X_transformed[:, 3]))


#%% take centroids
Y = np.load(prefix_path + 'Y_{}_{}.npy'.format(M, N))
#Z = np.load(prefix_path + 'Z_{}_{}.npy'.format(M, N))
if take_centroids:
    new_ld_12 = np.zeros((Y.shape[0], ld_12.shape[1]), dtype='float64')
    new_ld_123 = np.zeros((Y.shape[0], ld_123.shape[1]), dtype='float64')

    toggle = False
    for matrix in [ld_12, ld_123]:
        toggle = not toggle
        row_counter = 0

        start = 0
        label = Y[0]
        for i in range(matrix.shape[0]):
            if Y[i] == label:
                continue

            (new_ld_12 if toggle else new_ld_123)[row_counter, :] = np.mean(matrix[start:i, :], axis=0, dtype='float64')
            row_counter += 1

            start = i
            label = Y[i]

    ld_12 = new_ld_12
    ld_123 = new_ld_123


#%% clustering 2d

observe_set = set()
points = []
for cluster_count in range(2, 13):
    k_means = KMeans(n_clusters=cluster_count)
    k_means.fit(ld_12)

    points.append(k_means.inertia_)

    if cluster_count > 8:
        continue

    plt.figure()
    for i in range(cluster_count):
        plot_x, plot_y = [], []
        for row in range(ld_12.shape[0]):
            if k_means.labels_[row] == i:
                plot_x.append(ld_12[row, 0])
                plot_y.append(ld_12[row, 1])
            if not take_centroids and ld_12[row, 0] > 5:
                observe_set.add(Y[row])
                observe_set.add(Z[row])
        plt.plot(plot_x, plot_y, color=colours[i], marker='.', linestyle='')

    plt.xlabel('{}1'.format('LD' if pca_lda else 'PC'))
    plt.ylabel('{}2'.format('LD' if pca_lda else 'PC'))
    plt.title('k = {}'.format(cluster_count))
    plt.savefig(prefix_path + 'clustering_{}12_{}.png'.format('LD' if pca_lda else 'PC', cluster_count))

print(observe_set)
with zipfile.ZipFile('to_observe.zip', 'w') as outfile:
    for i in range(Z.shape[0]):
        if Y[i] not in observe_set or Z[i] not in observe_set:
            continue
        with outfile.open('{}\\{}.json'.format(Y[i], Z[i]), 'w') as outfile_zip,\
                open('..\\..\\history\\{}\\{}.json'.format(Y[i], Z[i]), 'r') as outfile_real:
            outfile_zip.write(outfile_real.read().encode('utf-8'))


plt.figure()
plt.plot([2 + x for x in range(len(points))], points, 'o-')
plt.title('WSS by number of clusters for {0}1-{0}2 space'.format('LD' if pca_lda else 'PC'))
plt.xlabel('Number of clusters (k)')
plt.ylabel('Sum of squares')
plt.savefig(prefix_path + '{0}1-{0}2_cluster_wss.png'.format('LD' if pca_lda else 'PC'))


#%% clustering 3d

points = []
for cluster_count in range(2, 13):
    k_means = KMeans(n_clusters=cluster_count)
    k_means.fit(ld_123)

    points.append(k_means.inertia_)

    if cluster_count > 8:
        continue

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for i in range(cluster_count):
        xyz = [list() for _ in range(3)]
        for row in range(ld_123.shape[0]):
            if k_means.labels_[row] == i:
                for j in range(3):
                    xyz[j].append(ld_123[row, j])
        ax.scatter(*xyz, c=colours[i], marker='.')

    ax.set_xlabel('{}1'.format('LD' if pca_lda else 'PC'))
    ax.set_ylabel('{}2'.format('LD' if pca_lda else 'PC'))
    ax.set_zlabel('{}3'.format('LD' if pca_lda else 'PC'))
    ax.set_title('k = {}'.format(cluster_count))
    fig.savefig(prefix_path + 'clustering_{}123_{}.png'.format('LD' if pca_lda else 'PC', cluster_count))
    fig.show()

plt.figure()
plt.plot([2 + x for x in range(len(points))], points, 'o-')
plt.title('WSS by number of clusters for {0}1-{0}2-{0}3 space'.format('LD' if pca_lda else 'PC'))
plt.xlabel('Number of clusters (k)')
plt.ylabel('Sum of squares')
plt.savefig(prefix_path + '{0}1{0}2{0}3_cluster_wss.png'.format('LD' if pca_lda else 'PC'))