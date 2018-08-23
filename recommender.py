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

def construct_model_topology(ninputs, noutputs, regression_problem, use_one_hot):
    init = 'uniform'
    bias = True
    dnn = Sequential([
        Dense(24, input_dim=ninputs, activation='relu', kernel_initializer=init, use_bias=bias),
        Dense(12, activation='relu', kernel_initializer=init, use_bias=bias),
        Dense(noutputs, activation=('sigmoid' if regression_problem or not(use_one_hot) else 'softmax'), kernel_initializer=init, use_bias=bias)
    ])

    if regression_problem: dnn.compile(loss='mape', optimizer='sgd')
    else: dnn.compile(loss=('categorical_crossentropy' if use_one_hot else 'binary_crossentropy'), optimizer='adam', metrics=['acc'])

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

class TrainingData:
    def __init__(self, xs, ys, validation_split):
        self.xs, self.ys = xs, ys
        val_split_index = round(len(xs) * validation_split)
        self.val_xs, self.val_ys = xs[:val_split_index], ys[:val_split_index]
        self.train_xs, self.train_ys = xs[val_split_index:], ys[val_split_index:]
        self.ninputs, self.noutputs = xs.shape[1], ys.shape[1]

def load_train_data(regression_problem, restype, jobset, validation_split, use_one_hot):
    config = dict(xtype='flattened', ytype=restype, jobset=jobset)
    xs, ys = training_data_generator.generate(config) if regression_problem else training_data_generator.generate_classification_problem(config, use_one_hot=use_one_hot)
    return TrainingData(xs, ys, validation_split)


def setup_train_validate_model(regression_problem, restype, jobset, use_one_hot, outfn=None):
    if outfn is not None and os.path.exists(outfn): os.remove(outfn)

    td = load_train_data(regression_problem, restype, jobset, 0.5, use_one_hot)
    model = construct_model_topology(td.ninputs, td.noutputs, regression_problem, use_one_hot)
    model.fit(td.train_xs, td.train_ys, batch_size=10, epochs=200, verbose=2)

    if outfn is not None: model.save(outfn)

    return td

def losses_for_hyperparameters(data, params, regression_problem):
    builder = model_topology_builder(data.ninputs, data.noutputs, regression_problem)
    dnn = builder(params['optimizer'], params['init'])
    history = dnn.fit(data.train_xs, data.train_ys, batch_size=params['batch_size'], epochs=params['epochs'])
    return history.history['loss'][-1], history.history['val_loss'][-1], history.history['acc'][-1],history.history['val_acc'][-1]


def load_and_predict(input, dnn_fn):
    xs = np.matrix([float(v) for v in project.flatten_project(input)]) if type(input) is str else input
    model = load_model(dnn_fn)
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


def project_paths(prefix, jobset, limit=None):
    with open('profits_' + str(jobset) + '.csv', 'r') as fp:
        all_paths = [prefix + line.split(';')[0] + '.json' for line in fp.readlines()[1:]]
        return all_paths if limit is None else all_paths[:limit]

res_cols = ['train_loss', 'validation_loss', 'train_acc', 'validation_acc']

def collect_all_losses(regression_problem, restype, jobset):
    td = load_train_data(False, restype, jobset, 0.5, True)
    combinations = all_parameter_combinations(pgrid)
    res = [(params, losses_for_hyperparameters(td, params, regression_problem)) for params in combinations]
    df = pd.DataFrame([list(params.values()) + list(losses) for params, losses in res],
                      columns=list(pgrid.keys()) + res_cols)
    df.to_pickle('losses.pkl')
    df2 = pd.read_pickle('losses.pkl')
    print(df2.sort_values(by=['validation_loss', 'train_loss']))


def collect_losses_for_range(start_ix, end_ix, regression_problem, restype, jobset, ofn='losses.csv'):
    sorted_keys = sorted(list(pgrid.keys()))
    td = load_train_data(False, restype, jobset, 0.5, True)
    combinations = all_parameter_combinations(pgrid)[start_ix:end_ix]
    res = [(params, losses_for_hyperparameters(td, params, regression_problem)) for params in combinations]
    ostr = '\n'.join([';'.join([str(v) for v in ([params[k] for k in sorted_keys] + list(losses))]) for params, losses in res]) + '\n'
    if not os.path.isfile(ofn):
        with open(ofn, 'w') as fp:
            fp.write(';'.join(sorted_keys + res_cols) + '\n' + ostr)
    else:
        with open(ofn, 'a') as fp:
            fp.write(ostr)

def percentage_correct_in_prediction(caption, true_ys, pred_ys, use_one_hot):
    correct_count = 0

    def array_leq(v1, v2):
        return all(v1[ix] <= v2[ix] for ix in range(len(v1)))

    def array_eq(v1, v2):
        return np.array_equal(v1, v2)

    cmp_func = array_eq if use_one_hot else array_leq

    for index, row in pred_ys.iterrows():
        true_vals = true_ys.loc[index].values
        predicted_vals = row.values
        correct_count += 1 if cmp_func(predicted_vals, true_vals) else 0

    total_count = pred_ys.shape[0]

    print(f'Percentage in {caption} correct: ' + str(correct_count / total_count))

def collect_predictions(xs, ys, jobset):
    predicted_ys = pd.DataFrame(load_and_predict(xs, f'dnn_{jobset}.h5'), ys.index, ys.columns)
    predicted_classes = predicted_ys.apply(lambda row: [round(v) for v in row], axis='columns')

    ys.to_csv('true_values.csv')
    predicted_ys.to_csv('predicted_values.csv')
    predicted_classes.to_csv('predicted_classes.csv')

    return predicted_classes

def hyperparameter_optimization():
    #sublists = split_list(all_parameter_permutations(pgrid), 10)
    #collect_all_losses(False, restype, jobset)
    #collect_losses_for_range(int(args[1]), int(args[2]), False, restype, jobset)
    #collect_losses_for_range(0, 3, False, restype, jobset)
    #td = load_train_data(False, 0.5)
    #losses = losses_for_hyperparameters(td, {'optimizer': 'sgd', 'batch_size': 10, 'epochs': 100, 'init': 'uniform'}, False)
    #print(losses)
    pass

def main(args):
    jobset = 30
    restype = 'profits'

    np.random.seed(23)

    #flatten_projects(project_paths(f'/Users/andreschnabel/Seafile/Dropbox/Scheduling/Projekte/k{jobset}_json/', jobset), f'flattened_{jobset}.csv')
    use_one_hot = True
    td = setup_train_validate_model(regression_problem=False, restype=restype, jobset=jobset, use_one_hot=use_one_hot, outfn=f'dnn_{jobset}.h5')

    #pd.read_csv('true_values.csv')
    #pd.read_csv('predicted_classes.csv')

    percentage_correct_in_prediction('Validation',
                                     true_ys=td.val_ys,
                                     pred_ys=collect_predictions(td.val_xs, td.val_ys, jobset),
                                     use_one_hot=use_one_hot)

    percentage_correct_in_prediction('Training',
                                     true_ys=td.train_ys,
                                     pred_ys=collect_predictions(td.train_xs, td.train_ys, jobset),
                                     use_one_hot=use_one_hot)


if __name__ == '__main__':
    main(sys.argv)
