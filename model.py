import json

from gurobipy import *


class ObjectFromJson:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def load_project(fn):
    with open(fn, 'r') as fp:
        return ObjectFromJson(**json.load(fp))


def setup_options(opts):
    env = Env()
    env.setParam('GRB_DoubleParam_MIPGap', opts['gap'])
    env.setParam('GRB_DoubleParam_TimeLimit', opts['timeLimit'])
    env.setParam('GRB_IntParam_DisplayInterval', opts['displayInterval'])
    env.setParam('GRB_IntParam_Threads', opts['threadCount'])
    return env


def build_model(p):
    try:
        model = Model("rcpsp-roc")

        J = range(p.numJobs)
        T = range(p.heuristicMaxMakespan)
        R = range(p.numRes)

        def time_window(j):
            return [t for t in T if p.efts[j] <= t <= p.lfts[j]]

        def time_window_for_demand(j, t):
            return [tau for tau in T if t <= tau <= min(t + p.durations[j], p.heuristicMaxMakespan)]

        xjt = [[model.addVar(0.0, 1.0 if p.efts[j] <= t <= p.lfts[j] else 0.0, 0.0, GRB.BINARY, 'x' + str(j) + ',' + str(t)) for t in T] for j in J]
        zrt = [[model.addVar(0.0, p.zmax[r], 0.0, GRB.INTEGER, 'z' + str(r) + ',' + str(t)) for t in T] for r in R]

        def add_objective():
            revenue_for_makespan = quicksum([p.u[t] * xjt[p.numJobs - 1][t] for t in time_window(p.numJobs - 1)])
            required_overtime_costs = quicksum([p.kappa[r] * zrt[r][t] for r in R for t in T])
            model.setObjective(revenue_for_makespan - required_overtime_costs, GRB.MAXIMIZE)

        def add_restrictions():
            model.addConstrs(quicksum([xjt[j][t] for t in T]) == 1 for j in J)

            def ft(j):
                return quicksum([xjt[j][t] * t for t in time_window(j)])

            model.addConstrs(ft(i) <= ft(j) - p.durations[j] for i in J for j in J if p.adjMx[i][j] == 1)

            def cum_demand(r, t):
                return quicksum([p.demands[j][r] * xjt[j][tau] for j in J for tau in time_window_for_demand(j, t)])

            model.addConstrs(cum_demand(r, t) <= p.capacities[r] + zrt[r][t] for r in R for t in T)

        add_objective()
        add_restrictions()

        return {'model': model, 'xjt': xjt, 'zrt': zrt}

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
    model.optimize()

    R = range(p.numRes)
    T = range(p.heuristicMaxMakespan)

    xjt_results = [[xjt[j][t].x for t in T] for j in range(p.numJobs)]
    zrt_results = [[zrt[r][t].x for r in R] for t in range(p.heuristicMaxMakespan)]

    def st(j):
        return next(t for t, xjt_val in enumerate(xjt_results[j]) if xjt_results[j][t] > 0.0)

    revenue = p.u[st(p.numJobs - 1)]
    overtime_costs = sum([p.kappa[r] * sum([zrt[r][t].x for t in T]) for r in R])

    obj = revenue - overtime_costs

    assert_optimality(model)
    assert (obj == model.objVal)

    return {'Sj': [st(j) for j in range(p.numJobs)], 'oc': overtime_costs, 'revenue': revenue, 'obj': obj}
