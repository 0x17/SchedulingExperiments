import sys
import recommender


def script_for_range(start_index, end_index):
    return '''#!/bin/bash -login
#PBS -N hyperparam_opt_[start_index]_[end_index]
#PBS -M andre.schnabel@prod.uni-hannover.de
#PBS -m a
#PBS -j oe
#PBS -l nodes=1:ppn=1
#PBS -l walltime=0:05:00
#PBS -l mem=8gb
#PBS -W x=PARTITION:lena
#PBS -q all

module load GCC/4.9.3-2.25
module load OpenMPI/1.10.2
module load TensorFlow/1.4.0-Python-3.5.1
module load pandas/0.18.0-Python-3.5.1

export PYTHONPATH=$PYTHONPATH:/home/nhulschn/keras/lib/python3.5/site-packages

cd $PBS_O_WORKDIR

python3 recommender.py [start_index] [end_index]'''.replace('[start_index]', str(start_index)).replace('[end_index]', str(end_index))


def main(args):
    combos_per_job = 10
    combos = recommender.all_parameter_combinations(recommender.pgrid)
    num_combos = len(combos)
    ctr = 0
    while ctr < num_combos:
        start_ix = ctr
        end_ix = min(num_combos, ctr + combos_per_job)
        with open('hpopt_job_' + str(start_ix) + '_' + str(end_ix) + '.sh', 'w') as fp:
            fp.write(script_for_range(start_ix, end_ix))
        ctr += combos_per_job


if __name__ == '__main__':
    main(sys.argv)
