def first_col(line, sep=';'):
    return line.split(sep)[0]


def tof(l): return [float(v) for v in l]


def instance_results_dict(csv_fn):
    sep = ';'
    with open(csv_fn, 'r') as fp:
        lines = fp.readlines()
        return lines[0].replace('\n', '').split(sep), {first_col(line): tof(line.split(sep)[1:]) for line in lines[1:]}
