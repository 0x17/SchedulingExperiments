import os
import os.path
import sys
import itertools
import math

import numpy as np
import pandas as pd

from keras.layers import Dense
from keras.models import Sequential, load_model

import project
import training_data_generator
import utils

jobset = 30
# jobset = 120
restype = 'gaps'

def construct_model_topology(ninputs, noutputs, regression_problem):
    init = 'uniform'
    bias = True
    dnn = Sequential([
        Dense(24, input_dim=ninputs, activation='relu', kernel_initializer=init, use_bias=bias),
        Dense(12, activation='relu', kernel_initializer=init, use_bias=bias),
        Dense(noutputs, activation=('sigmoid' if regression_problem else 'softmax'), kernel_initializer=init, use_bias=bias)
    ])

    if regression_problem: dnn.compile(loss='mape', optimizer='sgd')
    else: dnn.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['acc'])

    dnn.summary()
    return dnn


def model_topology_builder(ninputs, noutputs, regression_problem):
    def builder(optimizer, init):
        dnn = Sequential([
            Dense(24, input_dim=ninputs, activation='relu', kernel_initializer=init),
            Dense(12, activation='relu', kernel_initializer=init),
            Dense(noutputs, activation=('sigmoid' if regression_problem else 'softmax'), kernel_initializer=init)
        ])

        if regression_problem: dnn.compile(loss='mape', optimizer=optimizer)
        else: dnn.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['acc'])

        dnn.summary()
        return dnn

    return builder


pgrid = {
    'optimizer': ['sgd', 'adam'],
    'batch_size': [5, 10, 12, 20],
    'epochs': [50, 100, 160],
    'init': ['glorot_uniform', 'normal', 'uniform']
    # learning rate? (w/ adam and sgd)
    # decay? (only with adam)
}


def all_parameter_combinations(grid):
    tuples = list(itertools.product(*grid.values()))
    return [{list(grid.keys())[i]: tuple[i] for i in range(len(tuple))} for tuple in tuples]


def split_list(lst, sublen):
    num_sublists = math.ceil(len(lst) / sublen)
    return [lst[sublen * i:sublen * (i + 1)] if i < num_sublists else lst[sublen * i:] for i in range(num_sublists)]


def load_train_data(regression_problem):
    config = dict(xtype='flattened', ytype=restype, jobset=jobset)
    return training_data_generator.generate(config, True) if regression_problem else training_data_generator.generate_classification_problem(config, True)
    #return training_data_generator.generate_binary_classification_problem(config, True)


def setup_train_validate_model(regression_problem, outfn=None):
    if outfn is not None and os.path.exists(outfn): os.remove(outfn)

    xs, ys = load_train_data(regression_problem)

    ninputs = xs.shape[1]
    noutputs = ys.shape[1]

    model = construct_model_topology(ninputs, noutputs, regression_problem)

    model.fit(xs, ys, batch_size=10, epochs=100, verbose=2, shuffle=True, validation_split=0.5)

    if outfn is not None: model.save(outfn)

def losses_for_hyperparameters(data, params, regression_problem):
    xs, ys = data
    builder = model_topology_builder(xs.shape[1], ys.shape[1], regression_problem)
    dnn = builder(params['optimizer'], params['init'])
    history = dnn.fit(xs, ys, batch_size=params['batch_size'], epochs=params['epochs'], shuffle=True, validation_split=0.5)
    return history.history['loss'][-1], history.history['val_loss'][-1], history.history['acc'][-1],history.history['val_acc'][-1]


def load_and_predict(input, dnn_fn=None):
    xs = np.matrix([float(v) for v in project.flatten_project(input)]) if type(input) is str else input
    model = load_model(dnn_fn) if dnn_fn is not None else setup_train_validate_model(dnn_fn)
    prediction = model.predict(xs, verbose=1)
    return prediction


def flatten_projects(paths, outfn):
    maxT = max(len(project.load_project(path).T) for path in paths)
    with open(outfn, 'w') as fp:
        value_count = len(project.flatten_project(paths[0], maxT))
        fp.write('instance;' + ';'.join(['v' + str(ix) for ix in range(value_count)]) + '\n')
        for path in paths:
            instanceName = utils.stem(path)
            fp.write(instanceName + ';' + ';'.join(project.flatten_project(path, maxT)) + '\n')


def project_paths(prefix, limit=None):
    with open('methodprofits_' + str(jobset) + '.csv', 'r') as fp:
        all_paths = [prefix + line.split(';')[0] + '.json' for line in fp.readlines()[1:]]
        return all_paths if limit is None else all_paths[:limit]

res_cols = ['train_loss', 'validation_loss', 'train_acc', 'validation_acc']

def collect_all_losses(regression_problem):
    td = load_train_data(False)
    combinations = all_parameter_combinations(pgrid)
    res = [(params, losses_for_hyperparameters(td, params, regression_problem)) for params in combinations]
    df = pd.DataFrame([list(params.values()) + list(losses) for params, losses in res],
                      columns=list(pgrid.keys()) + res_cols)
    df.to_pickle('losses.pkl')
    df2 = pd.read_pickle('losses.pkl')
    print(df2.sort_values(by=['validation_loss', 'train_loss']))


def collect_losses_for_range(start_ix, end_ix, regression_problem, ofn='losses.csv'):
    sorted_keys = sorted(list(pgrid.keys()))
    td = load_train_data(False)
    combinations = all_parameter_combinations(pgrid)[start_ix:end_ix]
    res = [(params, losses_for_hyperparameters(td, params, regression_problem)) for params in combinations]
    ostr = '\n'.join([';'.join([str(v) for v in ([params[k] for k in sorted_keys] + list(losses))]) for params, losses in res]) + '\n'
    if not os.path.isfile(ofn):
        with open(ofn, 'w') as fp:
            fp.write(';'.join(sorted_keys + res_cols) + '\n' + ostr)
    else:
        with open(ofn, 'a') as fp:
            fp.write(ostr)


def main(args):
    np.random.seed(23)
    #flatten_projects(project_paths(f'/Users/andreschnabel/Seafile/Dropbox/Scheduling/Projekte/j{jobset}_json/'), f'flattened_{jobset}.csv')
    #setup_train_validate_model(False, f'dnn_{jobset}.h5')
    #print(load_and_predict('j3010_1.json', 'dnn_30.h5'))

    '''xs, true_ys = load_train_data(False)
    true_ys.to_csv('true_values.csv')

    predicted_ys = pd.DataFrame(load_and_predict(xs, f'dnn_{jobset}.h5'), true_ys.index, true_ys.columns)
    predicted_ys.to_csv('predicted_values.csv')

    predicted_classes = predicted_ys.apply(lambda row: [round(v) for v in row], axis='columns')
    predicted_classes.to_csv('predicted_classes.csv')'''

    # diff between predicted and true: how many misclassifications

    # sublists = split_list(all_parameter_permutations(pgrid), 10)

    collect_all_losses(False)
    #collect_losses_for_range(int(args[1]), int(args[2]), False)
    #collect_losses_for_range(0, 3, False)

    #td = load_train_data(False)
    #losses = losses_for_hyperparameters(td, {'optimizer': 'sgd', 'batch_size': 10, 'epochs': 100, 'init': 'uniform'}, False)
    #print(losses)


if __name__ == '__main__':
    main(sys.argv)
