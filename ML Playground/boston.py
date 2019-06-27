import numpy as np
from keras import datasets
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.callbacks import EarlyStopping
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt


def get_model(dense_size=32, dropout=0.0):
    model = Sequential()
    model.add(Dense(dense_size, activation='relu'))
    model.add(Dropout(dropout))
    model.add(Dense(1))
    model.compile(loss='mse', optimizer='adam')
    return model


if __name__ == '__main__':
    # load data
    (train_x, train_y), (test_x, test_y) = datasets.boston_housing.load_data()
    print('train x: {}, train y: {}, test x: {}, test y: {}'.format(train_x.shape, train_y.shape,
                                                                    test_x.shape, test_y.shape))

    # wrap the Keras model for scikit objects
    model = KerasRegressor(get_model, epochs=128, validation_split=0.2, verbose=False)

    # create a scaling pipeline
    pipeline = Pipeline([('scaler', StandardScaler()),
                         ('nn', model)])

    # create grid search object
    clf = GridSearchCV(pipeline, param_grid={'nn__batch_size': [3, 4, 5], 'nn__dense_size': [16, 32, 64],
                                             'nn__dropout': np.arange(0.0, 0.6, 0.1),
                                             'nn__callbacks': [[EarlyStopping(patience=10)]]})
    # find the best estimator
    clf.fit(train_x, train_y)
    best_estimator = clf.best_estimator_
    print(clf.best_params_)

    # calculate r^2 scores of train and test sets
    predicted = best_estimator.predict(train_x)
    print('Train R^2:', r2_score(train_y, predicted))

    predicted = best_estimator.predict(test_x)
    print('Test R^2:', r2_score(test_y, predicted))


