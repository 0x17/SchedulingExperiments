import os


def csv_to_dict(fn):
    with open(fn, 'r') as fp:
        return {line.split(';')[0]: round(float(line.split(';')[1]), 3) for line in fp.readlines()}


def serialize_profits(jobset, heur_profits, instance_names):
    ostr = 'instance;' + ';'.join(heur_profits.keys()) + '\n'
    for instance_name in instance_names:
        ostr += instance_name + ';' + ';'.join(
            [str(profit_dict[instance_name]) for method_name, profit_dict in heur_profits.items()]) + '\n'
    with open(f'profits_{jobset}.csv', 'w') as fp:
        fp.write(ostr)


def serialize_profits_for_jobset(jobset):
    #path_to_results = 'j30_1000schedulesJAN18/' if jobset == 30 else 'NochEinBackupDerErgebnisse/j120_1000schedules/'
    path_to_results = 'k30_1000schedules/'
    result_filenames = [path_to_results + entry for entry in os.listdir(path_to_results) if entry.endswith('Results.txt')]
    result_methods = [fn.replace('Results.txt', '').replace(path_to_results, '') for fn in result_filenames]
    heur_profits = {result_methods[ix]: csv_to_dict(result_filenames[ix]) for ix in range(len(result_filenames))}
    instance_names = list(list(heur_profits.values())[0].keys())
    serialize_profits(jobset, heur_profits, instance_names)


def main():
    serialize_profits_for_jobset(30)
    #serialize_profits_for_jobset(120)


if __name__ == '__main__':
    main()
