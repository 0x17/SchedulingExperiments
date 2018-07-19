from gurobipy import *
import numpy as np
import utils

p1 = {
    'njobs': 10,
    'renewables': [0],
    'non_renewables': [1],
    'durations': [0, 3, 4, 3, 5, 6, 4, 2, 2, 0],
    'demands': np.matrix('0 3 7 5 2 8 6 5 4 0; 0 2 5 8 3 5 3 9 3 0').transpose(),
    'capacities': [11, 38],
    'decision_sets': [[3, 4], [6, 7]],
    'decision_causing_jobs': [0, 4],
    'conditional_jobs': [(3, 8)],
    'precedence_relation': [(0, 1), (0, 2), (1, 3), (1, 4), (0, 5), (3, 5), (2, 4), (2, 8), (4, 6), (4, 7), (5, 9), (6, 9), (7, 9), (8, 9)]
}

def decorate_project(p):
    jobs = list(range(p['njobs']))
    T = sum(p['durations'])
    ndecisions = len(p['decision_sets'])
    adj_mx = np.matrix([[(i, j) in p['precedence_relation'] for j in jobs] for i in jobs])
    indecision = [j for dset in p['decision_sets'] for j in dset]
    decisions = list(range(ndecisions))
    mandatory_jobs = [j for j in jobs if j not in indecision and j not in [caused for causing, caused in p['conditional_jobs']]]
    return {**p, **{
        'jobs': jobs,
        'lastJob': jobs[-1],
        'actual_jobs': jobs[1:-1],
        'T': T,
        'periods': range(T),
        'ndecisions': ndecisions,
        'decisions': decisions,
        'indecision': indecision,
        'caused_by': [[i for i in jobs if (i, j) in p['conditional_jobs']] for j in jobs],
        'preds': [[i for i in jobs if adj_mx[i, j]] for j in jobs],
        'mandatory_jobs': mandatory_jobs,
        'mandatory_decisions': [e for e in decisions if p['decision_causing_jobs'][e] in mandatory_jobs],
        'optional_decisions': [e for e in decisions if p['decision_causing_jobs'][e] not in mandatory_jobs]
    }}

def serial_sgs(p, chosen_jobs, al):
    caused_jobs = [caused for causing, caused in p.conditional_jobs if causing in chosen_jobs]
    impl_jobs_al = [j for j in al if j in (chosen_jobs + caused_jobs + p.mandatory_jobs)]
    enough_nonrenewables = all(sum([p.demands[j, non_renewable] for j in impl_jobs_al]) <= p.capacities[non_renewable] for non_renewable in p.non_renewables)

    assert enough_nonrenewables

    def latest_pred_finished(j, sts):
        return max([sts[i] + p.durations[i] for i in p.preds[j] if i in impl_jobs_al] + [0])

    def active_periods(j, stj):
        return range(stj + 1, stj + p.durations[j] + 1)

    def enough_capacity(res_rem, t, j):
        return all(res_rem[r, tau] - p.demands[j, r] >= 0 for r in p.renewables for tau in active_periods(j, t))

    def reduce_res_rem(res_rem, j, t):
        for r in p.renewables:
            for tau in active_periods(j, t):
                res_rem[r, tau] -= p.demands[j, r]

    sts = {}

    res_rem = np.matrix([[p.capacities[r] for t in p.periods] for r in p.renewables])

    for j in impl_jobs_al:
        t = latest_pred_finished(j, sts)
        while not enough_capacity(res_rem, t, j): t += 1
        sts[j] = t
        reduce_res_rem(res_rem, j, t)

    print(sts)
    return sts


def solve_with_gurobi(p):
    def constraints(name_constr_pairs):
        for name, cstr in name_constr_pairs:
            model.addConstr(cstr, name)

    try:
        model = Model("rcpsp-ps")
        model.params.threads = 0
        model.params.mipgap = 0
        model.params.timelimit = GRB.INFINITY
        model.params.displayinterval = 5

        x = np.matrix([[model.addVar(0.0, 1.0, 0.0, GRB.BINARY, f'x{j}{t}') for t in p.periods] for j in p.jobs])

        def finish_periods_if_active_in(j, t):
            return range(t, min(t + p.durations[j], p.T))

        model.setObjective(quicksum(t * x[p.lastJob, t] for t in p.periods), GRB.MINIMIZE)
        constraints((f'each_once_{j}',
                     quicksum(x[j, t] for t in p.periods) == 1) for j in p.mandatory_jobs)
        constraints((f'decision_triggered_{e}',
                     quicksum(x[j, t] for j in p.decision_sets[e] for t in p.periods) == quicksum(x[p.decision_causing_jobs[e], t] for t in p.periods)) for e in p.decisions)
        constraints((f'conditional_jobs_{e}_{j}_{i}',
                     quicksum(x[i, t] for t in p.periods) == quicksum(x[j, t] for t in p.periods)) for e in p.decisions for j in p.decision_sets[e] for i in p.caused_by[j])
        constraints((f'precedence_{j}_{i}',
                     quicksum(t * x[i, t] for t in p.periods) <= quicksum((t - p.durations[j]) * x[j, t] for t in p.periods) + p.T * (1 - quicksum(x[j, t] for t in p.periods))) for j in p.jobs for i in p.preds[j])
        constraints((f'renewable_capacity_{r}_{t}',
                     quicksum(p.demands[j, r] * quicksum(x[j, tau] for tau in finish_periods_if_active_in(j, t)) for j in p.actual_jobs) <= p.capacities[r]) for r in p.renewables for t in p.periods)
        constraints((f'nonrenewable_capacity_{r}',
                     quicksum(p.demands[j, r] * quicksum(x[j, t] for t in p.periods) for j in p.actual_jobs) <= p.capacities[r]) for r in p.non_renewables)

        model.update()
        model.write('mymodel.lp')
        model.optimize()

        if model.status == GRB.Status.OPTIMAL:
            implemented_jobs = [j for j in p.jobs if any(x[j, t].x > 0.0 for t in p.periods)]
            sts = [[t for t in p.periods if x[j, t].x > 0.0][0] if j in implemented_jobs else -1 for j in p.jobs]
            print(f'Optimal solution: {sts}')
        else:
            print(f'Unable to obtain optimal solution. Status code = {model.status}')
            sts = [0] * p.njobs

        return sts

    except GurobiError as e:
        print(e)

def main():
    p = utils.ObjectFromDict(**decorate_project(p1))
    chosen_jobs = [4, 6]
    al = [0, 2, 5, 3, 1, 7, 4, 6, 8, 9]
    serial_sgs(p, chosen_jobs, al)
    solve_with_gurobi(p)



if __name__ == '__main__':
    main()