import json
import utils
import validation

from gurobipy import *


def load_project(fn):
    with open(fn, 'r') as fp:
        return utils.ObjectFromDict(**json.load(fp))


def setup_options(opts):
    env = Env()
    env.setParam('GRB_DoubleParam_MIPGap', opts['gap'])
    env.setParam('GRB_DoubleParam_TimeLimit', opts['timeLimit'])
    env.setParam('GRB_IntParam_DisplayInterval', opts['displayInterval'])
    env.setParam('GRB_IntParam_Threads', opts['threadCount'])
    return env


def main_sets(p):
    return [range(p.numJobs), range(p.heuristicMaxMakespan), range(p.numRes)]


def build_model(p):
    try:
        model = Model("rcpsp-roc")

        def add_named_constraints(constraint_name_pairs):
            for cstr, name in constraint_name_pairs:
                model.addConstr(cstr, name)

        J, T, R = main_sets(p)

        last_job = p.numJobs - 1

        def time_window(j):
            return [t for t in T if p.efts[j] <= t <= p.lfts[j]]

        def time_window_for_demand(j, t):
            return [tau for tau in T if t <= tau <= t + p.durations[j] - 1]

        x = [[model.addVar(0.0, 1.0 if t in time_window(j) else 0.0, 0.0, GRB.BINARY, 'x' + str(j) + ',' + str(t)) for t
              in T] for j in J]
        z = [[model.addVar(0.0, p.zmax[r], 0.0, GRB.CONTINUOUS, 'z' + str(r) + ',' + str(t)) for t in T] for r in R]

        def add_objective():
            revenue_for_makespan = quicksum([p.u[t] * x[last_job][t] for t in time_window(last_job)])
            required_overtime_costs = quicksum([p.kappa[r] * z[r][t] for r in R for t in T])
            model.setObjective(revenue_for_makespan - required_overtime_costs, GRB.MAXIMIZE)

        def add_restrictions():
            add_named_constraints([(quicksum([x[j][t] for t in time_window(j)]) == 1, '{0}_once'.format(j)) for j in J])

            def ft(j):
                return quicksum([x[j][t] * t for t in time_window(j)])

            def st(j):
                return ft(j) - p.durations[j]

            add_named_constraints([(ft(i) <= st(j), '{0}_before_{1}'.format(i,j)) for i in J for j in J if p.adjMx[i][j] == 1])

            def cum_demand(r, t):
                return quicksum([p.demands[j][r] * x[j][tau] for j in J for tau in time_window_for_demand(j, t)])

            add_named_constraints([(cum_demand(r, t) <= p.capacities[r] + z[r][t], 'rfeas_of_{0}_in_{1}'.format(r,t)) for r in R for t in T])

        add_objective()
        add_restrictions()

        return {'model': model, 'xjt': x, 'zrt': z}

    except GurobiError as e:
        print(e)


def assert_optimality(model):
    for bad_status in [GRB.Status.INF_OR_UNBD, GRB.Status.INFEASIBLE, GRB.Status.UNBOUNDED]:
        assert (model.status != bad_status)
    assert (model.status == GRB.Status.OPTIMAL)


def solve(instance_filename):
    p = load_project(instance_filename)
    model_compound = build_model(p)

    model, xjt, zrt = [model_compound[key] for key in ['model', 'xjt', 'zrt']]

    model.update()

    model.write('mymodel.lp')

    model.optimize()

    J, T, R = main_sets(p)

    xjt_results = [[xjt[j][t].x for t in T] for j in J]

    # zrt_results = [[zrt[r][t].x for r in R] for t in T]

    utils.matrix_to_csv(xjt_results, 'xjt_mx.csv')

    def ft(j):
        return next(t for t, xjt_val in enumerate(xjt_results[j]) if xjt_val > 0.0)

    def st(j):
        return ft(j) - p.durations[j]

    revenue = p.u[st(p.numJobs - 1)]
    overtime_costs = sum([p.kappa[r] * sum([zrt[r][t].x for t in T]) for r in R])

    obj = revenue - overtime_costs

    assert_optimality(model)
    assert (obj == model.objVal)

    sts = [st(j) for j in J]

    validation.assert_order_feasibility(p, sts)

    return {'Sj': sts,
            'Fj': [st(j) + p.durations[j] for j in J],
            'oc': overtime_costs,
            'revenue': revenue, 'obj': obj}


def serialize_results(results):
    with open('myschedule.txt', 'w') as fp:
        ostr = ''
        for j, stj in enumerate(results['Sj']):
            ostr += str(j + 1) + '->' + str(stj) + '\n'
        fp.write(ostr)

    with open('myprofit.txt', 'w') as fp:
        fp.write(str(results['obj']))


