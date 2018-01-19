import sys
import model
import validation
import basedata
import visualization
import json
import utils
import sgs
import project
import functools


def main(args):
    # results = model.solve('j3010_1.json')
    # print(results)

    # p = project.load_project('j3010_1.json')
    # visualization.plot_digraph(p)
    # model.solve(p, initial_solution=sgs.serial_schedule_generation_scheme(p, p.topOrder))

    # model.serialize_results(results)
    # validation.validate_schedule_and_profit('j3010_1.sm')

    """modelfn = '../../Projekte/j30_json/j3045_6.json'
    res_dict = model.results_for_deadline_range(modelfn, model.makespan(model.shortest_with_overtime(modelfn)),
                                                model.makespan(model.shortest_without_overtime(modelfn)))
    utils.spit_dict_as_json(res_dict, 'res_dict.json')
    visualization.plot_revenue_cost_profit_for_makespan(res_dict)

    diffdict = model.collect_shortest_diffs_heuristically('../../Projekte/j30_json/')
    utils.spit_dict_as_json(diffdict, 'diffs.json')

    maxInstance = ''
    maxDelta = 0

    for k,v in diffdict.items():
        if v['delta'] > maxDelta:
            maxDelta = v['delta']
            maxInstance = k

    print(maxInstance)"""

    p = project.load_project('j3010_1.json')
    results = model.solve_with_fix_and_optimize(p, sgs.serial_schedule_generation_scheme(p, p.topOrder), 10)
    #results = model.solve(p)
    model.serialize_results(results)
    validation.validate_schedule_and_profit('j3010_1.sm')


if __name__ == '__main__':
    main(sys.argv)
