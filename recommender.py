import json
import os
import random
from math import exp

import matplotlib.pyplot as plt
import numpy as np
import tensorflow
import tflearn
from keras import optimizers
from keras.layers import Dense
from keras.models import Sequential, load_model

import utils
import project

import sys

from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import GridSearchCV

import training_data_generator

np.random.seed(23)
tensorflow.set_random_seed(23)

jobset = 30  # 120
# restype = 'gaps'  # 'profits'
# restype = 'gaps'
restype = 'gaps'


# TODO: plot histograms? für ausprägung von Kenngröße wenn Variante X dominiert?
# TODO: Plot average gaps for method for cluster of characterstic (caro diss)
# TODO: Find patterns

def extract_data(char_fn=f'characteristics_{jobset}.csv', method_results_fn=f'method{restype}_{jobset}.csv'):
    def extract_dict(fn):
        out_dict = {}
        with open(fn, 'r') as fp:
            lines = fp.readlines()
            header = lines[0].split(';')
            numfields = len(lines[0].split(';')) - 1
            for line in lines[1:]:
                if ';' not in line: continue
                parts = line.split(';')
                out_dict[parts[0]] = [float(field.rstrip()) for field in parts[1:]]
        return out_dict, numfields, header

    char_for_instance, numchar, characteristics_header = extract_dict(char_fn)
    results_for_instance, numresults, method_results_header = extract_dict(method_results_fn)

    instances = list(results_for_instance.keys())
    random.shuffle(instances)

    method_names = [method_name.rstrip() for method_name in method_results_header[1:]]

    return {'characteristics': (char_for_instance, numchar, characteristics_header),
            'results': (results_for_instance, numresults, method_results_header),
            'instances': instances,
            'method_names': method_names}


def extract_matrices(start_ix, end_ix, char_fn=f'characteristics_{jobset}.csv',
                     method_profits_fn=f'method{restype}_{jobset}.csv'):
    ntrain = end_ix - start_ix

    data = extract_data(char_fn, method_profits_fn)

    char_for_instance, numchar, characteristics_header = data['characteristics']
    results_for_instance, numresults, method_results_header = data['results']
    method_names = data['method_names']

    def compute_out_mx_row(instance_results, ctr, type):
        best_val = max(instance_results) if 'gap' not in type else min(instance_results)
        if 'perc' in type:
            span = max(instance_results) - min(instance_results)
            return [1.0 if span == 0 else (profit - best_val) / span for profit in instance_results]
        elif 'onehot' in type:
            first_best_ix = instance_results.index(best_val)
            return [1 if i == first_best_ix else 0 for i in range(len(instance_results))]
        else:
            return instance_results

    characteristics = np.ndarray(shape=(ntrain, numchar), dtype=float)
    out_mx = np.ndarray(shape=(ntrain, len(method_names)), dtype=float)

    type = restype  # + '_onehot'

    ctr2 = 0
    for ctr, instance in enumerate(data['instances'][start_ix:end_ix]):
        if ctr >= ntrain or instance not in char_for_instance:
            continue
        characteristics[ctr2] = char_for_instance[instance]
        out_mx[ctr2] = compute_out_mx_row(results_for_instance[instance], ctr2, type)
        ctr2 += 1

    return characteristics, out_mx


def beautified_json(dnn):
    return json.dumps(json.loads(dnn.to_json()), indent=4)


def construct_model_topology(ninputs, noutputs):
    dnn = Sequential([
        Dense(24, input_dim=ninputs, activation='relu'),
        Dense(12, activation='relu'),
        Dense(noutputs, activation='sigmoid')
    ])
    #optimizer = optimizers.adam(lr=0.1, decay=0.001)
    dnn.compile(loss='mse', optimizer='adam')
    dnn.summary()
    #print(beautified_json(dnn))
    return dnn


def model_topology_builder(ninputs, noutputs):
    def builder(optimizer, init):
        dnn = Sequential([
            Dense(24, input_dim=ninputs, activation='relu', kernel_initializer=init),
            Dense(12, activation='relu', kernel_initializer=init),
            Dense(8, activation='relu', kernel_initializer=init),
            Dense(noutputs, activation='sigmoid', kernel_initializer=init)
        ])
        # optimizer = optimizers.adam(lr=0.1, decay=0.001)
        dnn.compile(loss='mse', optimizer=optimizer, metrics=['accuracy'])
        return dnn

    return builder


def grid_search_sklearn(builder, training_data):
    inputs, expected_outputs = training_data
    model = KerasClassifier(build_fn=builder, verbose=1)
    return GridSearchCV(estimator=model, param_grid={
        'optimizer': ['sgd', 'adam'],
        'batch_size': [5, 10, 20],
        'epochs': [50, 100, 150],
        'init': ['glorot_uniform', 'normal', 'uniform']
    }).fit(inputs, expected_outputs)


def train_model(dnn, training_data):
    inputs, expected_outputs = training_data
    dnn.fit(inputs, expected_outputs, batch_size=12, epochs=160, verbose=2)


def evaluate_model(model, validation_data):
    inputs, expected_outputs = validation_data
    scores = model.evaluate(inputs, expected_outputs)
    print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1] * 100))


def predict_model(model, data):
    print(f'Prediction: {model.predict(data, verbose=1)}')


def to_s(lst):
    return [str(elem) for elem in lst]


def export_training_data(data, outfn):
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

    #solvecount = 270
    #solvecount = 585
    #splitpoint = int(solvecount * 1.0)  # int(solvecount * 0.5)
    #training_data = extract_matrices(0, splitpoint, f'flattened_{jobset}.csv')
    #training_data = (csv_to_mx())
    # validation_data = extract_matrices(splitpoint, solvecount, f'flattened_{jobset}.csv')

    #export_training_data(training_data, 'training_data.csv')

    #characteristics, profits = training_data

    # res = grid_search_sklearn(model_topology_builder(characteristics.shape[1], profits.shape[1]), training_data)
    # print(res.cv_results_)

    #model = construct_model_topology(characteristics.shape[1], profits.shape[1])

    xs, ys = training_data_generator.generate()

    split_perc = 0.5
    split_count = round(len(xs)*split_perc)

    xs_train, ys_train = np.matrix(xs[:split_count]), np.matrix(ys[:split_count])
    xs_validate, ys_validate = np.matrix(xs[split_count:]), np.matrix(ys[split_count:])

    model = construct_model_topology(xs_train.shape[1], ys_train.shape[1])

    train_model(model, (xs_train, ys_train))
    scores = model.evaluate(xs_validate, ys_validate)
    print(scores)

    #evaluate_model(model, validation_data)
    # predict_model(model, validation_data[0])

    if outfn is not None: model.save(outfn)


def csv_line_to_characteristics_vector(csv_line):
    return np.array([float(entry.rstrip()) for entry in csv_line.split(';')[1:]])


def load_and_predict(projfn, infn):
    xs = np.matrix([ float(v) for v in project.flatten_project(projfn) ])
    model = load_model(infn)
    prediction = model.predict(xs, verbose=1)
    print(f'Prediction: {prediction}')
    return prediction


def verbalize_prediction(pred):
    best_candidate = list(pred).index(max(pred))
    method_names = ['Gurobi', 'GA (lambda|beta)', 'GA (lambda|zr)', 'GA (lambda|zrt)', 'LS (lambda|beta)',
                    'LS (lambda|zr)', 'LS (lambda|zrt)']
    print(f'Recommended solution method for this instance: {method_names[best_candidate]}')


def characteristics_vector_for_instance(instance_name):
    with open(f'characteristics_{jobset}.csv', 'r') as fp:
        lines = fp.readlines()
        for line in lines:
            if line.startswith(instance_name):
                return csv_line_to_characteristics_vector(line)
    return np.ndarray((1, 8), dtype='float')


def main(args):
    setup_and_train_validate_model(f'dnn_{jobset}.h5')

    # csv_line_to_characteristics_vector('j3013_2;4;639.5;47;32;74;1.5;0.9375;0.197073')

    #instname = 'j3010_1.json' if len(args) <= 1 else args[1]
    #pred = load_and_predict(instname, 'dnn_30.h5')
    #print(pred)
    #verbalize_prediction(pred)


def predict_all():
    with open(f'methodprofits_{jobset}.csv', 'r') as fp:
        lines = fp.readlines()[1:]
        for line in lines:
            instname = line.split(';')[0]
            pred = load_and_predict(characteristics_vector_for_instance(instname), 'dnn.h5')
            verbalize_prediction(pred[0])


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


if __name__ == '__main__':
    flatten_projects(big_project_paths(f'/Users/andreschnabel/Seafile/Dropbox/Scheduling/Projekte/j{jobset}_json/'),
                     f'flattened_{jobset}.csv')
    main(sys.argv)
    # linear_regression()
    # exponential_regression()
