import json
import matplotlib.pyplot as plt
import numpy as np
import tensorflow
import tflearn
from math import exp
from keras import optimizers
from keras.layers import Dense
from keras.models import Sequential
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import GridSearchCV

np.random.seed(23)
tensorflow.set_random_seed(23)


def beautified_json(dnn):
    return json.dumps(json.loads(dnn.to_json()), indent=4)


def linear_regression():
    f = lambda x: x * 15.0 + 5.0
    xs = np.array([float(x) for x in range(100)])
    ys = np.array([f(x) for x in xs])

    # w = [np.array([[20.0]]),np.array([0.0])]
    w = [np.array([[15.0]]), np.array([5.0])]

    dnn = Sequential([
        Dense(1, input_dim=1, activation='relu', use_bias=True, weights=w),
    ])

    optimizer = optimizers.adam(lr=1.0, decay=0.01)
    dnn.compile(loss='mse', optimizer=optimizer, metrics=['accuracy'])

    print(beautified_json(dnn))
    with open('lregress.json') as fp:
        fp.write(beautified_json(dnn))

    dnn.fit(xs, ys, batch_size=10, epochs=40, verbose=2)


def exponential_regression_net_keras(xs, ys):
    nobias = False
    dnn = Sequential([
        Dense(250, input_dim=1, kernel_initializer='normal', activation='relu', use_bias=not (nobias)),
        Dense(150, kernel_initializer='normal', activation='sigmoid', use_bias=not (nobias)),
        Dense(60, kernel_initializer='normal', activation='relu', use_bias=not (nobias)),
        Dense(10, kernel_initializer='normal', activation='relu', use_bias=not (nobias)),
        Dense(1, kernel_initializer='normal', use_bias=not (nobias))
    ])
    # optimizer = optimizers.adam(lr=1.0, decay=0.01)
    dnn.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
    # print(beautified_json(dnn))
    # utils.spit(beautified_json(dnn), 'expregress.json')
    dnn.fit(xs, ys, batch_size=20, epochs=50, verbose=2)
    return dnn.predict(xs)


def pack_for_tf(vals): return [[val] for val in vals]


def exponential_regression_net_tf(xs, ys):
    tflearn.init_graph(num_cores=8, gpu_memory_fraction=0.5)
    net = tflearn.input_data(shape=(None, 1))
    net = tflearn.fully_connected(net, 250, activation='relu')
    net = tflearn.fully_connected(net, 150, activation='sigmoid')
    net = tflearn.fully_connected(net, 60, activation='relu')
    net = tflearn.fully_connected(net, 10, activation='relu')
    net = tflearn.fully_connected(net, 1, activation='relu')
    net = tflearn.regression(net, optimizer='adam', loss='mean_square')
    model = tflearn.DNN(net)
    pxs = pack_for_tf(xs)
    model.fit(pxs, pack_for_tf(ys), batch_size=20, n_epoch=50, show_metric=True)
    return model.predict(pxs)


def exponential_regression():
    xs, ys = expfunc_training_data()
    pys = exponential_regression_net_keras(xs, ys)
    pys2 = exponential_regression_net_tf(xs, ys)
    plt.plot(xs, ys, label='Reference')
    plt.plot(xs, pys, label='DNN (Keras)')
    plt.plot(xs, pys2, label='DNN (TensorFlow)')
    plt.legend()
    plt.show()


def grid_search_sklearn(builder, training_data):
    xs, ys = training_data
    model = KerasRegressor(build_fn=builder, verbose=1)
    '''return GridSearchCV(estimator=model, param_grid={
        'optimizer': ['sgd', 'adam'],
        'batch_size': [5, 10, 20],
        'epochs': [50],
        'init': ['normal', 'uniform'],
        'bias': [False, True],
        'af': ['relu']
    }).fit(xs, ys)'''
    #dict(batch_size=5, epochs=50, init='normal', bias=True, optimizer='adam', af='relu')
    return GridSearchCV(estimator=model, param_grid={
        'optimizer': ['adam'],
        'batch_size': [5],
        'epochs': [50],
        'init': ['normal'],
        'bias': [True],
        'af': ['relu']
    }).fit(xs, ys)

def exponential_regression_net_keras_builder():
    def builder(optimizer, init, bias, af):
        #layer_sizes = [250, 150, 60, 10, 1]
        layer_sizes = [250, 1]
        dnn = Sequential(
            [Dense(layer_sizes[0], input_dim=1, kernel_initializer=init, activation=af, use_bias=bias)] +
            [Dense(layer_size, kernel_initializer=init, activation=af, use_bias=bias) for layer_size in layer_sizes[1:-1]] +
            [Dense(layer_sizes[-1], kernel_initializer=init, activation=af, use_bias=bias)])
        dnn.compile(loss='mse', optimizer=optimizer)
        return dnn

    return builder


def expfunc_training_data():
    f = lambda x: 0.5 * exp(0.125 * x)
    # f = lambda x: 0.5 * math.sin(x)
    xs = np.array([float(x) for x in np.arange(10, 20, 0.01)])
    ys = np.array([f(x) for x in xs])
    return (xs, ys)


def exp_regr_grid():
    xs, ys = expfunc_training_data()
    res = grid_search_sklearn(exponential_regression_net_keras_builder(), (xs, ys))

    print(f"Best: {res.best_score_} using {res.best_params_}")
    print("All results:")
    for mean, stdev, param in zip(res.cv_results_['mean_test_score'], res.cv_results_['std_test_score'], res.cv_results_['params']):
        print(f"{mean}, {stdev}, {param}")


def eval_with_config(config):
    xs, ys = expfunc_training_data()
    dnn = exponential_regression_net_keras_builder()(config['optimizer'], config['init'], config['bias'], config['af'])
    dnn.fit(xs, ys, batch_size=config['batch_size'], epochs=config['epochs'], verbose=2)
    pys = dnn.predict(xs)
    plt.plot(xs, ys, label='Reference')
    plt.plot(xs, pys, label='DNN (Keras)')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    exp_regr_grid()
    #eval_with_config(dict(batch_size=5, epochs=50, init='normal', bias=True, optimizer='adam', af='relu'))
    # exponential_regression()
