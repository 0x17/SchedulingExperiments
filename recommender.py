import os
import sys

import numpy as np
import tensorflow
from keras.layers import Dense
from keras.models import Sequential, load_model
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import GridSearchCV

import project
import training_data_generator
import utils

np.random.seed(23)
tensorflow.set_random_seed(23)

# jobset = 30
jobset = 120
restype = 'gaps'


def construct_model_topology(ninputs, noutputs):
    dnn = Sequential([
        Dense(24, input_dim=ninputs, activation='relu'),
        Dense(12, activation='relu'),
        Dense(noutputs, activation='sigmoid')
    ])
    # optimizer = optimizers.adam(lr=0.1, decay=0.001)
    dnn.compile(loss='mse', optimizer='adam')
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


def grid_search_sklearn(builder, training_data):
    inputs, expected_outputs = training_data
    model = KerasRegressor(build_fn=builder, verbose=1)
    return GridSearchCV(estimator=model, param_grid={
        'optimizer': ['sgd', 'adam'],
        'batch_size': [5, 10, 12, 20],
        'epochs': [50, 100, 160],
        'init': ['glorot_uniform', 'normal', 'uniform']
    }).fit(inputs, expected_outputs)


def export_training_data(data, outfn):
    def to_s(lst): return [str(elem) for elem in lst]

    characteristics, res_mx = data
    nrows = characteristics.shape[0]
    assert (nrows == res_mx.shape[0])

    ostr = ''
    for i in range(nrows):
        ostr += ';'.join(to_s(list(characteristics[i]) + list(res_mx[i]))) + '\n'

    with open(outfn, 'w') as fp:
        fp.write(ostr)


def setup_and_train_validate_model(outfn=None):
    if outfn is not None and os.path.exists(outfn): os.remove(outfn)

    xs, ys = training_data_generator.generate(True)

    split_perc = 0.5
    split_count = round(len(xs) * split_perc)

    xs_train, ys_train = np.matrix(xs[:split_count]), np.matrix(ys[:split_count])
    xs_validate, ys_validate = np.matrix(xs[split_count:]), np.matrix(ys[split_count:])

    res = grid_search_sklearn(model_topology_builder(xs_train.shape[1], ys_train.shape[1]), (xs_train, ys_train))
    print(res.cv_results_)

    model = construct_model_topology(xs_train.shape[1], ys_train.shape[1])

    model.fit(xs, ys, batch_size=12, epochs=160, verbose=2)

    scores = model.evaluate(xs_validate, ys_validate)
    print(scores)

    if outfn is not None: model.save(outfn)


def load_and_predict(projfn, infn):
    xs = np.matrix([float(v) for v in project.flatten_project(projfn)])
    model = load_model(infn)
    prediction = model.predict(xs, verbose=1)
    print(f'Prediction: {prediction}')
    return prediction


def verbalize_prediction(pred):
    best_candidate = list(pred).index(max(pred))
    method_names = ['Gurobi', 'GA (lambda|beta)', 'GA (lambda|zr)', 'GA (lambda|zrt)', 'LS (lambda|beta)',
                    'LS (lambda|zr)', 'LS (lambda|zrt)']
    print(f'Recommended solution method for this instance: {method_names[best_candidate]}')


def flatten_projects(paths, outfn):
    maxT = max(len(project.load_project(path).T) for path in paths)
    with open(outfn, 'w') as fp:
        value_count = len(project.flatten_project(paths[0], maxT))
        fp.write('instance;' + ';'.join([f'v{ix}' for ix in range(value_count)]) + '\n')
        for path in paths:
            instanceName = utils.stem(path)
            fp.write(instanceName + ';' + ';'.join(project.flatten_project(path, maxT)) + '\n')


def big_project_paths(prefix, limit=None):
    with open(f'methodprofits_{jobset}.csv', 'r') as fp:
        all_paths = [prefix + line.split(';')[0] + '.json' for line in fp.readlines()[1:]]
        return all_paths if limit is None else all_paths[:limit]


def main(args):
    # flatten_projects(big_project_paths(f'/Users/andreschnabel/Seafile/Dropbox/Scheduling/Projekte/j{jobset}_json/'), f'flattened_{jobset}.csv')
    setup_and_train_validate_model(f'dnn_{jobset}.h5')
    print(load_and_predict('j3010_1.json', 'dnn_30.h5'))


if __name__ == '__main__':
    main(sys.argv)
