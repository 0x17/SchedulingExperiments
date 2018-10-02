from datamerge_common import instance_results_dict


def dmap(func, dict):
    return {k: func(v) for k, v in dict.items()}


def profits_to_multihot(profits):
    mval = max(profits)
    return [1.0 if v == mval else 0.0 for v in profits]

def profits_to_multihot_decimal(profits):
    def bool2int(lst):
        y = 0
        for i, j in enumerate(lst):
            y += int(j) << i
        return y
    return [bool2int(profits_to_multihot(profits))]



def merge_tables(csv_tbl1_fn, csv_tbl2_fn):
    # dicts are str -> list[float] mappings
    def merge_dicts(master, slave):
        return {k: slave[k] + v for k, v in master.items()}

    hr1, d1 = instance_results_dict(csv_tbl1_fn)
    hr2, d2 = instance_results_dict(csv_tbl2_fn)

    #return hr1 + hr2[1:], merge_dicts(dmap(profits_to_multihot_decimal, d2), d1)
    return hr1 + ['Class'], merge_dicts(dmap(profits_to_multihot_decimal, d2), d1)


def serialize_table(hr, dict, fn):
    sep = ','
    with open(fn, 'w') as fp:
        fp.write(sep.join(hr) + '\n')
        for instance, vals in dict.items():
            fp.write(instance + sep + sep.join([str(v) for v in vals]) + '\n')


def merge_data():
    header_row, merged_dict = merge_tables('characteristics_j30.csv', 'methodprofits_30.csv')
    serialize_table(header_row, merged_dict, 'datamerged_classification_j30.csv')


if __name__ == '__main__':
    merge_data()
