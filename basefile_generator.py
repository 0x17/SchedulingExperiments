import itertools
import basedata


def all_variable_parameter_combinations(grid):
    tuples = list(itertools.product(*grid.values()))
    return [{list(grid.keys())[i]: tuple[i] for i in range(len(tuple))} for tuple in tuples]


def generate_basefiles(grid, template_fn):
    combos = all_variable_parameter_combinations(grid)
    template_name = template_fn.replace('.bas', '')
    for ix, combo in enumerate(combos):
        basedata.overwrite_parameters_in_basefile(template_fn, f'{template_name}{(ix + 1)}_.bas', combo)


if __name__ == '__main__':
    pgrid = {
        'Complexity': [1.5, 1.8, 2.0],
        'RRF': [0.25, 0.5, 0.75, 1.0],
        'RRS': [0.2, 0.5, 0.7, 1.0]
    }

    generate_basefiles(pgrid, 'k30.bas')


