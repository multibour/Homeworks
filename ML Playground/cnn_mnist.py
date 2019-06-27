import tensorflow as tf
import numpy as np
from keras import datasets
from keras.models import Model
from keras.layers import Dense, Conv2D, MaxPool2D, Input, Concatenate, Flatten, Dropout
from sklearn.preprocessing import OneHotEncoder


def cnn(im_shape) -> Model:
    # implement a mini version GoogLeNet's Inception model
    input = Input(im_shape)

    conv_1 = Conv2D(8, (1, 1), padding='same', activation='relu')(input)

    conv_2 = Conv2D(12, (1, 1), padding='same', activation='relu')(input)
    conv_2 = Conv2D(16, (3, 3), padding='same', activation='relu')(conv_2)

    conv_3 = Conv2D(2, (1, 1), padding='same', activation='relu')(input)
    conv_3 = Conv2D(4, (5, 5), padding='same', activation='relu')(conv_3)

    conv_4 = MaxPool2D((3, 3), padding='same', strides=(1, 1))(input)
    conv_4 = Conv2D(4, (1, 1), padding='same', activation='relu')(conv_4)

    concat = Concatenate(axis=-1)([conv_1, conv_2, conv_3, conv_4])

    flat = Flatten()(concat)
    dense = Dense(32, activation='relu')(flat)
    dense = Dropout(0.4)(dense)
    out = Dense(10, activation='softmax', name='out')(dense)

    model = Model(input, out)
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    return model


if __name__ == '__main__':
    # get mnist dataset
    (train_x, train_y), (test_x, test_y) = datasets.mnist.load_data()
    print('train x: {}, train y: {}, test x: {}, test y: {}'.format(train_x.shape, train_y.shape,
                                                                    test_x.shape, test_y.shape))

    # reshape input data from (n, height, width, 1) to (n, height, width, 1) or it does not work
    train_x = train_x[..., np.newaxis]
    test_x = test_x[..., np.newaxis]

    # encode labels
    enc = OneHotEncoder()
    train_y = enc.fit_transform(train_y.reshape(-1, 1)).toarray()
    test_y = enc.transform(test_y.reshape(-1, 1)).toarray()

    # create and fit model
    model = cnn(train_x[0, ...].shape)
    batch_size= 64
    model.fit(train_x, train_y, epochs=3, batch_size=batch_size)

    # evaluate model
    score, acc = model.evaluate(test_x, test_y, batch_size=batch_size)
    print('test score: {}, test acc: {}'.format(score, acc))

    '''
    A simple NN converges faster and predicts better for now
    TODO: experiment with the dense layers a bit
    '''

    # look at the results for the first 10 test images
    predicted = model.predict(test_x, test_y)
    print(test_y[:10], np.argmax(predicted[:10], axis=1))

