from keras import datasets
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Dropout, Embedding, LSTM
from keras.callbacks import EarlyStopping
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import GridSearchCV


def create_model(dropout=0.0, lstm_size=128, dense_size=32):
    model = Sequential()
    model.add(Embedding(1024, lstm_size))
    model.add(LSTM(lstm_size, dropout=dropout))
    model.add(Dense(dense_size, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


if __name__ == '__main__':
    maxlen = 100

    # get imdb reviews dataset
    (train_x, train_y), (test_x, test_y) = datasets.imdb.load_data(num_words=1024, maxlen=maxlen)
    print('train_x: {}, train_y: {}, test_x: {}, test_y: {}'.format(train_x.shape, train_y.shape, test_x.shape,
                                                                    test_y.shape))

    train_x = pad_sequences(train_x, maxlen=maxlen, padding='post')
    test_x = pad_sequences(test_x, maxlen=maxlen, padding='post')
    print(train_x.shape, test_x.shape)

    # wrap classifier for scikit objects
    model = KerasClassifier(create_model, epochs=10)

    # grid search for best hyperparams
    clf = GridSearchCV(model, param_grid={'dropout': [0.0, 0.2, 0.5], 'lstm_size': [100, 128],
                                          'dense_size': [16, 32, 64], 'batch_size': [32, 64],
                                          'callbacks': [[EarlyStopping(patience=5)]]}
                       )  # early stopping is given as a parameter to grid search since it gives an error if given to the wrapper class, reason unknown

    clf.fit(train_x, train_y)
    best_model = clf.best_estimator_
    print(clf.best_params_)

    score, acc = best_model.evaluate(test_x, test_y)
    print('Test score: {}, test accuracy: {}'.format(score, acc))
