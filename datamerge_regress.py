from datamerge_common import first_col, instance_results_dict

def get_optimals(char_dict):
    with open('optimals_j30.csv', 'r') as fp:
        return {first_col(line): char_dict[first_col(line)] + [float(line.split(';')[1])] for line in fp.readlines()}


def merge_data():
    header_row, char_dict = instance_results_dict('characteristics_j30.csv')
    opt_dict = get_optimals(char_dict)
    with open('datamerged_regress_j30.csv', 'w') as fp:
        sep = ','
        fp.write(','.join(header_row) + ',optimalObjective\n')
        for instance, vals in opt_dict.items():
            fp.write(instance + sep + sep.join([str(v) for v in vals]) + '\n')


if __name__ == '__main__':
    merge_data()
