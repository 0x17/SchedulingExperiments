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

        # sets
        J = range(p.numJobs)
        T = range(p.T)
        heurT = range(p.heuristicMaxMakespan)
        R = range(p.numRes)

        def time_window(j):
            return [t for t in heurT if t >= p.efts[j] and t <= p.lfts[j]]

        def time_window_for_demand(j, t):
            return [tau for tau in heurT if tau >= t and tau <= min(t + p.durations[j], p.heuristicMaxMakespan)]

        # decision variables
        # primary
        xjt = [[model.addVar(lb=0.0, ub=1.0 if t >= p.efts[j] and t <= p.lfts[j] else 0.0, obj=0.0, vtype=GRB.BINARY,
                             name=f'x{j},{t}') for t in heurT] for j in J]
        # derived
        zrt = [[model.addVar(lb=0.0, ub=p.zmax[r], vtype=GRB.INTEGER, name=f'z{r},{t}') for t in heurT] for r in R]

        # objective
        revenueForMakespan = quicksum([ p.revenue[t] * xjt[p.numJobs-1][t] for t in time_window(p.numJobs-1)])
        requiredOvertimeCosts = quicksum([ p.kappa[r] * zrt[r][t] for r in R for t in heurT ])
        model.setObjective(revenueForMakespan - requiredOvertimeCosts, GRB.MAXIMIZE)

        # constraints
        model.addConstrs([quicksum([xjt[j][t] for t in heurT]) == 1 for j in J])

        def ft(j):
            return quicksum([xjt[j][t] * t for t in time_window(j)])

        model.addConstrs([ft(i) <= ft(j) - p.durations[j] for i in J for j in J if p.adjMx[i][j] == 1 ])

        def cumDemand(r, t):
            return quicksum([p.demands[j][r] * xjt[j][tau] for j in J for tau in time_window_for_demand(j, t) ])

        model.addConstrs([cumDemand(r,t) <= p.capacities[r] + zrt[r][t] for r in R for t in heurT ])

        return {'model': model, 'xjt': xjt, 'zrt': zrt}

    except GurobiError as e:
        print(e)


def solve(instance_filename):
    p = load_project(instance_filename)
    model_compound = build_model(p)

    model, xjt, zrt = [ model_compound[key] for key in ['model', 'xjt', 'zrt'] ]

    model.update()
    model.optimize()

    xjt_results = [[ xjt[j][t].x  for t in range(p.heuristicMaxMakespan) ] for j in range(p.numJobs) ]
    zrt_results = [[ zrt[r][t] for r in range(p.numRes) ] for t in range(p.heuristicMaxMakespan)]
    obj = model.getObjective()

    return { 'xjt': xjt_results, 'zrt': zrt_results, 'obj': obj }


