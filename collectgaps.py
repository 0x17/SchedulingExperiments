import os

# jobset = 30
jobset = 120
path_to_results = 'j30_1000schedulesJAN18/' if jobset == 30 else 'NochEinBackupDerErgebnisse/j120_1000schedules/'
path_to_reference = 'GMS_CPLEX_Results.txt'


def csv_to_dict(fn):
    with open(fn, 'r') as fp:
        return {line.split(';')[0]: round(float(line.split(';')[1]), 3) for line in fp.readlines()}


def compute_gap_dict(ref_values, heur_values):
    odict = {}
    for heur_name, heur_mapping in heur_values.items():
        odict[heur_name] = {}
        for instance_name, opt_val in ref_values.items():
            odict[heur_name][instance_name] = max(0, (opt_val - heur_mapping[instance_name]) / opt_val)
    return odict


def serialize_gaps(heur_gaps, instance_names):
    def stringify(v: float):
        return str(round(v, 3))

    ostr = 'instance;' + ';'.join(heur_gaps.keys()) + '\n'
    for instance_name in instance_names:
        ostr += instance_name + ';' + ';'.join([stringify(gap_dict[instance_name]) for method_name, gap_dict in heur_gaps.items()]) + '\n'
    with open(f'gaps_{jobset}.csv', 'w') as fp:
        fp.write(ostr)


def best_known_solutions_dict(heur_values):
    def bks(instance_name):
        return max(res_dict[instance_name] for method_name, res_dict in heur_values.items())

    instance_names = next(iter(heur_values.items()))[1].keys()
    return {instance_name: bks(instance_name) for instance_name in instance_names}


def main():
    result_filenames = [path_to_results + entry for entry in os.listdir(path_to_results) if
                        entry.endswith('Results.txt')]
    result_methods = [fn.replace('Results.txt', '').replace(path_to_results, '') for fn in result_filenames]
    heur_values = {result_methods[ix]: csv_to_dict(result_filenames[ix]) for ix in range(len(result_filenames))}
    ref_values = csv_to_dict(path_to_reference) if jobset == 30 else best_known_solutions_dict(heur_values)
    heur_gaps = compute_gap_dict(ref_values, heur_values)
    serialize_gaps(heur_gaps, list(ref_values.keys()))


if __name__ == '__main__':
    main()
