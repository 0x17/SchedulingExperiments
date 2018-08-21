from typing import List
import random
import pandas as pd

random.seed(23)

def generate_mx(csv_fn: str, instances_both_know: List[str]):
    with open(csv_fn, 'r') as fp:
        lines = fp.readlines()[1:]
        line_for_instance = lambda instance_name: next(line for line in lines if line.split(';')[0] == instance_name)
        return [[float(x) for x in line_for_instance(instance_name).split(';')[1:]] for instance_name in
                instances_both_know]


def instances_in_both_csv_files(xfn, yfn):
    def instances(lines):
        return [line.split(';')[0] for line in lines]

    with open(xfn, 'r') as fp1:
        xinstances = instances(fp1.readlines()[1:])

    with open(yfn, 'r') as fp2:
        yinstances = instances(fp2.readlines()[1:])

    return [xinstance for xinstance in xinstances if xinstance in yinstances]


def generate(config, use_pandas=False):
    xfn = config['xtype'] + '_' + str(config['jobset']) + '.csv'
    yfn = config['ytype'] + '_' + str(config['jobset']) + '.csv'
    instances_both_know = instances_in_both_csv_files(xfn, yfn)
    random.shuffle(instances_both_know)
    xs = generate_mx(xfn, instances_both_know)
    ys = generate_mx(yfn, instances_both_know)
    if use_pandas:
        with open(yfn, 'r') as fp:
            method_names = fp.readlines()[0].split(';')[1:]
        xframe = pd.DataFrame(xs, index=instances_both_know, columns=['v' + str(ix + 1) for ix in range(len(xs[0]))])
        yframe = pd.DataFrame(ys, index=instances_both_know, columns=method_names)
        return xframe, yframe
    else:
        return xs, ys


def generate_classification_problem(config, use_pandas=False):
    def index_of_best_method(y):
        return next(ix for ix,z in enumerate(y) if z == min(y))

    xs, ys = generate(config, use_pandas)
    ys_index_vec = [index_of_best_method(y) for y in ys.values]
    ys_onehot = [ [ ix == best_index for ix in range(ys.shape[1]) ] for best_index in ys_index_vec ]
    return xs, (pd.DataFrame(ys_onehot, index=ys.index, columns=ys.columns) if use_pandas else ys_onehot)

if __name__ == '__main__':
    config = {
        'xtype': 'flattened',
        'ytype': 'gaps',
        'jobset': 30
    }
    cp = generate_classification_problem(config, True)
    print(cp)