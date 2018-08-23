import os
import random

import numpy as np
import pandas as pd

random.seed(23)


def cache_frame(csv_fn):
    pkl_fn = csv_fn.replace('.csv', '.pkl')
    if os.path.isfile(pkl_fn):
        return pd.read_pickle(pkl_fn)
    else:
        df = pd.read_csv(csv_fn, ';', index_col=0, header=0)
        df.to_pickle(pkl_fn)
        return df


def generate(config):
    jobset_str = str(config['jobset'])
    xfn = config['xtype'] + '_' + jobset_str + '.csv'
    yfn = config['ytype'] + '_' + jobset_str + '.csv'
    x_val_frame = cache_frame(xfn)
    x_char_frame = cache_frame(f'characteristics_k{jobset_str}.csv')
    xframe = pd.concat([x_val_frame, x_char_frame], axis=1)
    yframe = cache_frame(yfn)
    assert xframe.shape[0] == yframe.shape[0]
    new_index = np.random.permutation(xframe.index)
    xframe.reindex(new_index)
    yframe.reindex(new_index)
    return xframe, yframe


def indices_of_best_methods(y, best_func):
    return (ix for ix, z in enumerate(y) if z == best_func(y))


def index_of_best_method(y, best_func):
    return next(indices_of_best_methods(y, best_func))


def generate_classification_problem(config, use_one_hot=True):
    best_func = min if config['ytype'] == 'gaps' else max

    xs, ys = generate(config)

    ys_index_vec = [index_of_best_method(y, best_func) for y in ys.values]
    ys_onehot = [[1.0 if ix == best_index else 0.0 for ix in range(ys.shape[1])] for best_index in ys_index_vec]

    ys_indices_vec = [list(indices_of_best_methods(y, best_func)) for y in ys.values]
    ys_multihot = [[1.0 if ix in best_indices else 0.0 for ix in range(ys.shape[1])] for best_indices in ys_indices_vec]

    ys_categ = ys_onehot if use_one_hot else ys_multihot

    return xs, pd.DataFrame(ys_categ, index=ys.index, columns=ys.columns)


def generate_binary_classification_problem(config, use_pandas=False):
    best_func = min if config['ytype'] == 'gaps' else max
    ls_indices = [3, 4, 5, 6, 7]

    def local_solver_in_best_methods(y):
        indices = indices_of_best_methods(y, best_func)
        return any(ls_index in indices for ls_index in ls_indices)

    xs, ys = generate(config)
    ys_is_ls = [local_solver_in_best_methods(y) for y in ys.values]
    return xs, pd.DataFrame(ys_is_ls, index=ys.index, columns=['is_local_solver'])


if __name__ == '__main__':
    config = {
        'xtype': 'flattened',
        'ytype': 'profits',  # 'gaps',
        'jobset': 30
    }
    cp = generate_classification_problem(config, True)
    # cp = generate_binary_classification_problem(config, True)
    print(cp)
