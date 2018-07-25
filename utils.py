import os
import json
import random


def randelem(coll):
    return coll[random.randint(0, len(coll) - 1)]


class Nothing:
    pass


class ObjectFromDict:
    def __init__(self, **entries):
        self.__dict__.update(entries)
        self.basedict = entries

    def __str__(self):
        return str(self.basedict)


def sys_call(s):
    print('SYSCALL: ' + s)
    os.system(s)


def os_command_str(cmd):
    return './' + cmd + ' ' if os.name == 'posix' else cmd + '.exe '


def force_delete_file(fn):
    while True:
        try:
            if not (os.path.isfile(fn)): break
            os.remove(fn)
        except OSError:
            print('Deleting ' + fn + ' failed. Retry!')
        else:
            break


def batch_del(lst):
    for fn in lst:
        force_delete_file(fn)


def none_to_default(val, defval):
    return val if val is not None else defval


def none_to_zero(val):
    return none_to_default(val, 0)


def matrix_to_csv(mx, out_filename):
    with open(out_filename, 'w') as fp:
        fp.write('\n'.join([';'.join([str(cell) for cell in row]) for row in mx]))


def slurp(fn):
    with open(fn, 'r') as fp:
        return fp.read()


def slurp_lines(fn):
    with open(fn, 'r') as fp:
        return fp.readlines()


def spit(s, fn):
    with open(fn, 'w') as fp:
        fp.write(s)


def spit_dict_as_json(d, fn):
    with open(fn, 'w') as fp:
        json.dump(d, fp)


def concat_no_dups(a, b):
    return a.copy() + [e for e in b if e not in a]


def stem(path):
    return os.path.basename(os.path.splitext(path)[0])


def average(gen_expr, length):
    return sum(gen_expr) / length


def extract_csv_lines(csv_contents_or_fn):
    if type(csv_contents_or_fn) is str:
        if '.csv' in csv_contents_or_fn:
            with open(csv_contents_or_fn, 'r') as fp:
                return fp.readlines()
        else:
            return csv_contents_or_fn.split('\n')
    elif type(csv_contents_or_fn) is list:
        return csv_contents_or_fn


# TODO: Write unit test
def filter_csv_complement(csv_contents_or_fn, removed_col_names):
    col_names = extract_csv_lines(csv_contents_or_fn)[0].split(';')
    for rcol_name in removed_col_names:
        col_names.remove(rcol_name)
    return filter_csv(csv_contents_or_fn, column_names=col_names)


def filter_csv(csv_contents_or_fn, column_names=None, column_indices=None, ofn=None, as_str=False):
    csv_lines = extract_csv_lines(csv_contents_or_fn)

    if type(column_names) is list and column_indices is None:
        column_indices = [csv_lines[0].split(';').index(column_name) for column_name in column_names]

    olines = []
    for csv_line in csv_lines:
        take_parts = [part for ix, part in enumerate(csv_line.split(';')) if ix in column_indices]
        olines.append(';'.join(take_parts));

    ostr = '\n'.join(olines)
    if ofn is not None:
        with open(ofn, 'w') as fp:
            fp.write(ostr)

    return ostr if as_str else olines


def argmin(elems):
    minval = min(elems)
    for ix, elem in enumerate(elems):
        if elem == minval:
            return ix
    return -1


def without(lst, elems):
    return [elem for elem in lst if elem not in elems]


def random_pairs(coll):
    assert (len(coll) % 2 == 0)
    pairs = []
    rem_coll = list(coll)
    for i in range(int(len(coll) / 2)):
        a = randelem(rem_coll)
        b = randelem(without(rem_coll, [a]))
        pairs.append((a, b))
        rem_coll = without(rem_coll, [a, b])
    return pairs

def mapping_range(pairs, domain_vals):
    return [b for a, b in pairs if a in domain_vals]