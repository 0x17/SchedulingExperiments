from keras.models import Sequential, load_model, Model
from keras.layers import Dense

import numpy as np
import sys

np.random.seed(7)


def extract_data(start_ix, end_ix, char_fn='characteristics.csv', method_profits_fn='methodprofits.csv'):
    ntrain = end_ix - start_ix

    char_for_instance = {}
    with open(char_fn, 'r') as fp:
        lines = fp.readlines()[1:]
        numchar = len(lines[0].split(';')) - 1
        for line in lines:
            if ';' not in line: continue
            parts = line.split(';')
            char_for_instance[parts[0]] = [float(chr.rstrip()) for chr in parts[1:]]

    with open(method_profits_fn, 'r') as fp:
        lines = fp.readlines()
        method_names = [line.rstrip() for line in lines[0].split(';')[1:]]

        characteristics = np.ndarray(shape=(ntrain, numchar), dtype=float)
        indicators = np.ndarray(shape=(ntrain, len(method_names)), dtype=float)
        indicators_one_hot = np.ndarray(shape=(ntrain, len(method_names)), dtype=float)

        ctr = 0
        for line in lines[1 + start_ix:end_ix]:
            if ctr >= ntrain: break
            if ';' not in line: continue
            parts = line.split(';')
            instance_name = parts[0]
            profits = [float(profit) for profit in parts[1:]]
            span = max(profits) - min(profits)
            mp = min(profits)
            indicators[ctr] = [1.0 if span == 0 else (profit - mp) / span for profit in profits]
            characteristics[ctr] = char_for_instance[instance_name]
            first_best_ix = profits.index(max(profits))
            indicators_one_hot[ctr] = [1 if i == first_best_ix else 0 for i in range(len(profits))]
            ctr += 1

    return characteristics, indicators_one_hot


def construct_model_topology(ninputs, noutputs):
    dnn = Sequential([
        Dense(12, input_dim=ninputs, activation='relu'),
        Dense(8, activation='relu'),
        Dense(noutputs, activation='sigmoid')
    ])
    dnn.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
    return dnn


def train_model(dnn, training_data):
    inputs, expected_outputs = training_data
    dnn.fit(inputs, expected_outputs, batch_size=10, epochs=40, verbose=2)


def evaluate_model(model, validation_data):
    inputs, expected_outputs = validation_data
    scores = model.evaluate(inputs, expected_outputs)
    print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1] * 100))


def predict_model(model, data):
    print(f'Prediction: {model.predict(data, verbose=1)}')


def setup_and_eval_model(outfn=None):
    solvecount = 270

    training_data = extract_data(0, int(solvecount / 2))
    validation_data = extract_data(int(solvecount / 2), solvecount)

    characteristics, profits = training_data
    model = construct_model_topology(characteristics.shape[1], profits.shape[1])

    # print(model.to_json())
    train_model(model, training_data)
    #evaluate_model(model, validation_data)
    #predict_model(model, validation_data[0])

    if outfn is not None: model.save(outfn)


def csv_line_to_characteristics_vector(csv_line):
    mx = np.ndarray((1, 8), dtype='float')
    mx[0] = [float(entry.rstrip()) for entry in csv_line.split(';')[1:]]
    return mx


def load_and_predict(characteristics, infn):
    model = load_model(infn)
    prediction = model.predict(characteristics, verbose=1)
    print(f'Prediction: {prediction}')
    return prediction


def verbalize_prediction(pred):
    best_candidate = list(pred).index(max(pred))
    method_names = ['Gurobi', 'GA (lambda|beta)', 'GA (lambda|zr)', 'GA (lambda|zrt)', 'LS (lambda|beta)', 'LS (lambda|zr)', 'LS (lambda|zrt)']
    print(f'Recommended solution method for this instance: {method_names[best_candidate]}')


def characteristics_vector_for_instance(instance_name):
    with open('characteristics.csv', 'r') as fp:
        lines = fp.readlines()
        for line in lines:
            if line.startswith(instance_name):
                return csv_line_to_characteristics_vector(line)
    return np.ndarray((1, 8), dtype='float')


def main(args):
    #setup_and_eval_model('dnn.h5')

    #csv_line_to_characteristics_vector('j3013_2;4;639.5;47;32;74;1.5;0.9375;0.197073')

    instname = 'j3013_2' if len(args) <= 1 else args[1]
    pred = load_and_predict(characteristics_vector_for_instance(instname), 'dnn.h5')
    verbalize_prediction(pred[0])


if __name__ == '__main__':
    main(sys.argv)
