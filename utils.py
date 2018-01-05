import os
import json


class Nothing:
    pass


class ObjectFromDict:
    def __init__(self, **entries):
        self.__dict__.update(entries)


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
