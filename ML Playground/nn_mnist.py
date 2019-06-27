import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder, normalize
from keras import datasets


def neural_net(x, pixels):
    layer_1 = tf.layers.Dense(256, activation=tf.nn.relu, name='layer_1', input_dim=[None, pixels])(x)
    layer_2 = tf.layers.Dense(256, activation=tf.nn.relu, name='layer_2')(layer_1)
    layer_3 = tf.layers.Dense(128, activation=tf.nn.relu, name='layer_3', )(layer_2)
    output_layer = tf.layers.Dense(10, activation=tf.nn.softmax, name='out')(layer_3)
    return output_layer


if __name__ == '__main__':
    # Get mnist dataset
    (train_x, train_y), (test_x, test_y) = datasets.mnist.load_data()
    print('train x: {}, train y: {}, test x: {}, test y: {}'.format(train_x.shape, train_y.shape,
                                                                    test_x.shape, test_y.shape))
    # Reshape data
    px_count = train_x.shape[1] * train_x.shape[2]
    train_x, test_x = train_x.reshape(-1, px_count), test_x.reshape(-1, px_count)
    train_x, test_x = normalize(train_x, axis=1), normalize(test_x, axis=1)

    # Redo label data
    enc = OneHotEncoder()
    train_y = enc.fit_transform(train_y.reshape(-1, 1)).toarray()
    test_y = enc.transform(test_y.reshape(-1, 1)).toarray()

    # Split the validation dataset
    #p = 0.7  # percentage split
    #train_x, val_x = train_x[:int(len(train_x)*p)], train_x[int(len(train_x)*p):]
    #train_y, val_y = train_y[:int(len(train_y)*p)], train_y[int(len(train_y)*p):]

    # Set placeholders
    X = tf.placeholder(tf.float32, [None, px_count])
    Y = tf.placeholder(tf.float32, [None, 10])

    # Session functions
    logits = neural_net(X, px_count)
    loss = tf.reduce_mean(tf.losses.softmax_cross_entropy(Y, logits=logits))
    optimizer = tf.train.AdamOptimizer(learning_rate=1e-3).minimize(loss)

    prediction_results = tf.equal(tf.argmax(logits, 1), tf.argmax(Y, 1))
    accuracy = tf.reduce_mean(tf.cast(prediction_results, tf.float32))

    history_train = []
    history_test = []
    history_loss = []

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        batch_size = 32
        step_count = len(train_x) // batch_size + 1

        for epoch in range(1):
            print('--- epoch {} ---'.format(epoch))

            for step in range(step_count):
                start = step * batch_size
                batch_x, batch_y = train_x[start:start+batch_size], train_y[start:start+batch_size]

                sess.run(optimizer, feed_dict={X: batch_x, Y: batch_y})
                if (step+1) % 50 == 0 or step == 0:
                    cost, acc = sess.run([loss, accuracy], feed_dict={X: batch_x, Y: batch_y})
                    print('step {} loss {} accuracy {}'.format(step+1, cost, acc))
                    history_loss.append(cost)

                if step % 50 == 0:
                    history_train.append(sess.run(accuracy, feed_dict={X: train_x, Y: train_y}))
                    history_test.append(sess.run(accuracy, feed_dict={X: test_x, Y: test_y}))

        print('final accuracy:', sess.run(accuracy, feed_dict={X: train_x, Y: train_y}))
        print('test acc:', sess.run(accuracy, feed_dict={X: test_x, Y: test_y}))

    # Plot
    plt.figure()
    plt.plot(np.arange(1, len(history_train)+1), history_train, label='Train Set')
    plt.plot(np.arange(1, len(history_test)+1), history_test, label='Test Set')
    plt.xlabel('step')
    plt.ylabel('accuracy')
    plt.legend()
    plt.show()

    plt.figure()
    plt.plot(np.arange(1, len(history_loss)+1), history_loss)
    plt.title('Loss')
    plt.xlabel('step')
    plt.ylabel('accuracy')
    plt.show()
