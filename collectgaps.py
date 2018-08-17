import os
from typing import Dict, List, Tuple


def compute_gap_dict(ref_values: Dict[str, float], heur_values: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str,float]]:
    odict = {}
    for heur_name, heur_mapping in heur_values.items():
        odict[heur_name] = {}
        for instance_name, opt_val in ref_values.items():
            odict[heur_name][instance_name] = max(0, (opt_val - heur_mapping[instance_name]) / opt_val)
    return odict


def csv_to_dict(fn: str) -> Dict[str, float]:
    with open(fn, 'r') as fp:
        return {line.split(';')[0]: round(float(line.split(';')[1]), 3) for line in fp.readlines()}


path_to_results = 'j30_1000schedulesJAN18/'
path_to_reference = 'GMS_CPLEX_Results.txt'

result_filenames: List[str] = [path_to_results + entry for entry in os.listdir(path_to_results) if
                               entry.endswith('Results.txt')]
result_methods: List[str] = [fn.replace('Results.txt', '').replace(path_to_results, '') for fn in result_filenames]

ref_values: Dict[str, float] = csv_to_dict(path_to_reference)
heur_values: Dict[str, Dict[str, float]] = {result_methods[ix]: csv_to_dict(result_filenames[ix]) for ix in
                                            range(len(result_filenames))}

heur_gaps:Dict[str, Dict[str,float]] = compute_gap_dict(ref_values, heur_values)


def serialize_gaps(heur_gaps: Dict[str, Dict[str,float]], instance_names: List[str]) -> None:
    def stringify(v: float):
        return str(round(v, 3))
    header = 'instance;'+';'.join(heur_gaps.keys())+'\n'
    ostr = header
    for instance_name in instance_names:
        ostr += instance_name + ';' + ';'.join([ stringify(gap_dict[instance_name]) for method_name, gap_dict in heur_gaps.items() ]) + '\n'
    with open('mygaps.txt', 'w') as fp:
        fp.write(ostr)


if __name__ == '__main__':
    serialize_gaps(heur_gaps, list(ref_values.keys()))
    print()
