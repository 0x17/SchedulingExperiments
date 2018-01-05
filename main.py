import sys
import model
import validation
import basedata
import visualization
import json
import utils
import sgs
import project


def main(args):
    #results = model.solve('j3010_1.json')
    #print(results)

    p = project.load_project('j3010_1.json')
    #visualization.plot_digraph(p)

    sts = sgs.serial_schedule_generation_scheme(p, p.topOrder)
    print(sts)

    # model.serialize_results(results)
    # validation.validate_schedule_and_profit('j3010_1.sm')

    # modelfn = 'j3010_1.json'
    # res_dict = model.results_for_deadline_range(modelfn, model.makespan(model.shortest_with_overtime(modelfn)),
    #                                            model.makespan(model.shortest_without_overtime(modelfn)))
    # visualization.plot_revenue_cost_profit_for_makespan(res_dict)

    #diffdict = model.collect_shortest_diffs('../../Projekte/j30_json/')
    #utils.spit_dict_as_json(diffdict, 'diffs.json')


if __name__ == '__main__':
    main(sys.argv)
