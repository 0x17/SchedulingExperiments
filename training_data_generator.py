import numpy as np
from typing import List
import random

random.seed(23)

jobset = 30
xtype = 'flattened'  # 'characteristics'
ytype = 'gaps'  # 'profits'


def generate_mx(csv_fn: str, instances_both_know: List[str]):
    instances_both_know_copy = list(instances_both_know)
    random.shuffle(instances_both_know_copy)
    with open(csv_fn, 'r') as fp:
        lines = fp.readlines()[1:]
        line_for_instance = lambda instance_name: next(line for line in lines if line.split(';')[0] == instance_name)
        return [[float(x) for x in line_for_instance(instance_name).split(';')[1:]] for instance_name in instances_both_know_copy]


def instances_in_both_csv_files(xfn, yfn):
    def instances(lines):
        return [line.split(';')[0] for line in lines]

    with open(xfn, 'r') as fp1:
        xinstances = instances(fp1.readlines()[1:])

    with open(yfn, 'r') as fp2:
        yinstances = instances(fp2.readlines()[1:])

    return [xinstance for xinstance in xinstances if xinstance in yinstances]


def generate():
    xfn = f'{xtype}_{jobset}.csv'
    yfn = f'{ytype}_{jobset}.csv'
    instances_both_know = instances_in_both_csv_files(xfn, yfn)
    xs = generate_mx(xfn, instances_both_know)
    ys = generate_mx(yfn, instances_both_know)
    return xs, ys
