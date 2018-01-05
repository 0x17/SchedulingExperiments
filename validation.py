import os
import utils

SKIPFILE_PATH = 'plsdoskip'


def validate_schedule_and_profit(inst_filename, schedule_filename='myschedule.txt', profit_filename='myprofit.txt',
                                 method='GUROBI'):
    result_filenames = [schedule_filename, profit_filename]
    all_filenames = result_filenames + [SKIPFILE_PATH]

    def append_to_invalid_lst():
        print('Appending ' + inst_filename + ' with method ' + method + ' to invalids...')
        with open('invalids.txt', 'a') as fp:
            fp.write(inst_filename + ';' + method + '\n')

    if (not os.path.isfile(schedule_filename)) or (not os.path.isfile(profit_filename)):
        print('Unable to find schedule or profit file for method ' + method + '!')
        utils.batch_del(all_filenames)
    else:
        utils.sys_call('java -jar ScheduleValidator.jar ' + os.getcwd() + os.sep + ' ' + inst_filename)
        if os.path.isfile(SKIPFILE_PATH):
            utils.batch_del(all_filenames)
            append_to_invalid_lst()
            raise Exception('Invalid schedule or profit for method ' + method + '!')
        else:
            utils.batch_del(result_filenames)
            print('Valid solution from ' + method + ' for ' + inst_filename)

