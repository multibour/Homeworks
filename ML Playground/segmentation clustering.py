import numpy as np
from imageio import imread, imsave
from sklearn.cluster import KMeans, MeanShift
from sklearn.preprocessing import StandardScaler
import os


def segmentation_clustering(image, clustering=KMeans()):
    if not isinstance(image, np.ndarray):
        raise TypeError('image has to be a numpy matrix')

    # Rearrange the image data into points in 2+Channels dimensional space
    # Spatial data with colour (generally Red+Green+Blue)
    height, width, channels = image.shape
    data = np.zeros((height*width, 2+channels), dtype='int')
    for i in range(height):
        for j in range(width):
            data[width*i+j, :] = [i, j, *image[i, j, :]]

    # Standardize then cluster data points
    data = StandardScaler().fit_transform(data.astype(np.float32))
    labels = clustering.fit_predict(data)

    # Construct result image
    result = np.zeros_like(image)  # same shape as the original image
    for c in range(len(clustering.cluster_centers_)):
        indices = (labels == c)  # indices of the points assigned to cluster c
        mean = np.mean(data[indices, -channels:], axis=0)  # mean of colour values of the points in the same cluster

        indices = [index for index, element in enumerate(indices.tolist()) if element is True]
        row_indices = list(map(lambda i: i // width, indices))
        column_indices = list(map(lambda i: i % width, indices))
        result[row_indices, column_indices, :] = mean

    return result


if __name__ == '__main__':
    directory = './images/'
    for filename in os.listdir(directory):
        if filename.startswith('_'):
            continue
        result = segmentation_clustering(imread(directory + filename), KMeans(n_clusters=5))
        imsave(directory + '_n5_' + filename, result)
