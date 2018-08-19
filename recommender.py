import os
import os.path
import sys
import itertools
import math

import numpy as np
import pandas as pd

from keras.layers import Dense
from keras.models import Sequential, load_model
from keras.wrappers.scikit_learn import KerasRegressor
# from sklearn.model_selection import GridSearchCV

import project
import training_data_generator
import utils

np.random.seed(23)

# jobset = 30
jobset = 120
restype = 'gaps'


def construct_model_topology(ninputs, noutputs):
    init = 'uniform'
    dnn = Sequential([
        Dense(24, input_dim=ninputs, activation='relu', kernel_initializer=init),
        Dense(12, activation='relu', kernel_initializer=init),
        Dense(noutputs, activation='sigmoid', kernel_initializer=init)
    ])
    # optimizer = optimizers.adam(lr=0.1, decay=0.001)
    dnn.compile(loss='mse', optimizer='sgd')
    dnn.summary()
    return dnn


def model_topology_builder(ninputs, noutputs):
    def builder(optimizer, init):
        dnn = Sequential([
            Dense(24, input_dim=ninputs, activation='relu', kernel_initializer=init),
            Dense(12, activation='relu', kernel_initializer=init),
            Dense(noutputs, activation='sigmoid', kernel_initializer=init)
        ])
        # optimizer = optimizers.adam(lr=0.1, decay=0.001)
        dnn.compile(loss='mse', optimizer=optimizer)
        dnn.summary()
        return dnn

    return builder


pgrid = {
    'optimizer': ['sgd', 'adam'],
    'batch_size': [5, 10, 12, 20],
    'epochs': [50, 100, 160],
    'init': ['glorot_uniform', 'normal', 'uniform']
}


def all_parameter_combinations(grid):
    tuples = list(itertools.product(*grid.values()))
    return [{list(grid.keys())[i]: tuple[i] for i in range(len(tuple))} for tuple in tuples]


def split_list(lst, sublen):
    num_sublists = math.ceil(len(lst) / sublen)
    return [lst[sublen * i:sublen * (i + 1)] if i < num_sublists else lst[sublen * i:] for i in range(num_sublists)]


'''def grid_search_sklearn(builder, training_data):
    inputs, expected_outputs = training_data
    model = KerasRegressor(build_fn=builder, verbose=1)
    return GridSearchCV(estimator=model, param_grid=pgrid).fit(inputs, expected_outputs)'''


class TrainingData:
    def __init__(self, data, split_perc=0.5):
        xs, ys = data
        split_count = round(len(xs) * split_perc)
        self.train = xs[:split_count], ys[:split_count]
        self.validation = xs[split_count:], ys[split_count:]
        self.xs, self.ys = xs, ys


def load_train_data():
    return TrainingData(training_data_generator.generate(True))


def setup_train_validate_model(outfn=None):
    if outfn is not None and os.path.exists(outfn): os.remove(outfn)

    td = load_train_data()

    xs_train, ys_train = td.train
    xs_validate, ys_validate = td.validation
    xs, ys = td.xs, td.ys

    model = construct_model_topology(xs_train.shape[1], ys_train.shape[1])

    model.fit(xs, ys, batch_size=5, epochs=160, verbose=2)

    scores = model.evaluate(xs_validate, ys_validate)
    print(scores)

    if outfn is not None: model.save(outfn)


def losses_for_hyperparameters(td, params):
    builder = model_topology_builder(td.xs.shape[1], td.ys.shape[1])
    dnn = builder(params['optimizer'], params['init'])
    history = dnn.fit(td.train[0], td.train[1], params['batch_size'], params['epochs'], shuffle=False,
                      validation_data=td.validation)
    return history.history['loss'][-1], history.history['val_loss'][-1]


def load_and_predict(input, dnn_fn = None):
    xs = np.matrix([float(v) for v in project.flatten_project(input)]) if type(input) is str else input
    model = load_model(dnn_fn) if dnn_fn is not None else setup_train_validate_model(dnn_fn)
    prediction = model.predict(xs, verbose=1)
    return prediction


def verbalize_prediction(pred):
    best_candidate = list(pred).index(max(pred))
    method_names = ['Gurobi', 'GA (lambda|beta)', 'GA (lambda|zr)', 'GA (lambda|zrt)', 'LS (lambda|beta)',
                    'LS (lambda|zr)', 'LS (lambda|zrt)']
    print('Recommended solution method for this instance: ' + method_names[best_candidate])


def flatten_projects(paths, outfn):
    maxT = max(len(project.load_project(path).T) for path in paths)
    with open(outfn, 'w') as fp:
        value_count = len(project.flatten_project(paths[0], maxT))
        fp.write('instance;' + ';'.join(['v' + str(ix) for ix in range(value_count)]) + '\n')
        for path in paths:
            instanceName = utils.stem(path)
            fp.write(instanceName + ';' + ';'.join(project.flatten_project(path, maxT)) + '\n')


def big_project_paths(prefix, limit=None):
    with open('methodprofits_' + str(jobset) + '.csv', 'r') as fp:
        all_paths = [prefix + line.split(';')[0] + '.json' for line in fp.readlines()[1:]]
        return all_paths if limit is None else all_paths[:limit]


def collect_all_losses():
    td = load_train_data()
    combinations = all_parameter_combinations(pgrid)
    res = [(params, losses_for_hyperparameters(td, params)) for params in combinations]
    df = pd.DataFrame([list(params.values()) + list(losses) for params, losses in res],
                      columns=list(pgrid.keys()) + ['train_loss', 'validation_loss'])
    df.to_pickle('losses.pkl')
    df2 = pd.read_pickle('losses.pkl')
    print(df2.sort_values(by=['validation_loss', 'train_loss']))


def collect_losses_for_range(start_ix, end_ix, ofn='losses.csv'):
    sorted_keys = sorted(list(pgrid.keys()))
    td = load_train_data()
    combinations = all_parameter_combinations(pgrid)[start_ix:end_ix]
    res = [(params, losses_for_hyperparameters(td, params)) for params in combinations]
    ostr = '\n'.join([';'.join([str(v) for v in ([params[k] for k in sorted_keys] + list(losses))]) for params, losses in res]) + '\n'
    if not os.path.isfile(ofn):
        with open(ofn, 'w') as fp:
            fp.write(';'.join(sorted_keys + ['train_loss', 'validation_loss']) + '\n' + ostr)
    else:
        with open(ofn, 'a') as fp:
            fp.write(ostr)


def main(args):
    # flatten_projects(big_project_paths(f'/Users/andreschnabel/Seafile/Dropbox/Scheduling/Projekte/j{jobset}_json/'), f'flattened_{jobset}.csv')
    #setup_train_validate_model(f'dnn_{jobset}.h5')
    #print(load_and_predict('j3010_1.json', 'dnn_30.h5'))
    
    td = load_train_data()
    res = load_and_predict(td.validation[0], 'dnn_30.h5')
    df = pd.DataFrame(res, td.validation[1].index, td.validation[1].columns)
    df.to_csv('predicted_validation.csv')
    td.validation[1].to_csv('actual_validation.csv')

    # sublists = split_list(all_parameter_permutations(pgrid), 10)
    # collect_all_losses()
    #collect_losses_for_range(int(args[1]), int(args[2]))


if __name__ == '__main__':
    main(sys.argv)
