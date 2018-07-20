from gurobipy import *
import numpy as np
import utils

import flexparse

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

q1 = {
    'qlevels': range(3),
    'nqlevels': 3,
    'qattributes': range(2),
    'nqattributes': 2,
    'costs': [0, 5, 3, 2, 1, 7, 10, 6, 1, 0],
    'base_qualities': [20, 0],
    'quality_improvements': [
        {4: 10, 5: 12, 7: 15, 8: 5, 9: 8},
        {4: 0, 5: 10, 7:15, 8: 0, 9: 20}
    ],
    'qlevel_requirement': np.matrix('40 35 30; 20 15 10'),
    'customers': {
        'revenue_periods': [12, 13, 14],
        'revenues': [
            np.matrix('50 49 48; 40 39 38; 30 29 28'),
            np.matrix('50 40 30; 49 39 29; 48 38 28'),
            np.matrix('40 39 38; 39 38 37; 38 37 36')
        ]
    }
}


def eligibles(jobs, preds, already_scheduled):
    return [j for j in jobs if j not in already_scheduled and all(i in already_scheduled for i in preds[j])]


def topological_sort(preds, jobs):
    al = []
    for ix in range(len(jobs)):
        al.append(min(eligibles(jobs, preds, al)))
    return al


def canonical_choice(p):
    cd = {}

    def choose_min_nonrenew_demand(eligibles):
        return utils.argmin([max(p.demands[j, r] for r in p.non_renewables) for j in eligibles])

    def recurse_triggered_decisions(causing_job):
        for od in p.optional_decisions:
            if p.decision_causing_jobs[od] == causing_job:
                cd[od] = choose_min_nonrenew_demand(p.decision_sets[od])
                recurse_triggered_decisions(cd[od])

    for md in p.mandatory_decisions:
        cd[md] = choose_min_nonrenew_demand(p.decision_sets[md])
        recurse_triggered_decisions(cd[md])

    return cd


def decorate_project(p):
    jobs = list(range(p['njobs']))
    T = sum(p['durations'])
    ndecisions = len(p['decision_sets'])
    adj_mx = np.matrix([[(i, j) in p['precedence_relation'] for j in jobs] for i in jobs])
    indecision = [j for dset in p['decision_sets'] for j in dset]
    decisions = list(range(ndecisions))
    mandatory_jobs = [j for j in jobs if j not in indecision and j not in [caused for causing, caused in p['conditional_jobs']]]
    preds = [[i for i in jobs if adj_mx[i, j]] for j in jobs]
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
        'preds': preds,
        'mandatory_jobs': mandatory_jobs,
        'mandatory_decisions': [e for e in decisions if p['decision_causing_jobs'][e] in mandatory_jobs],
        'optional_decisions': [e for e in decisions if p['decision_causing_jobs'][e] not in mandatory_jobs],
        'topOrder': topological_sort(preds, jobs)
    }}


def serial_sgs(p, choices, al):
    caused_jobs = [caused for causing, caused in p.conditional_jobs if causing in choices.values()]
    impl_jobs_al = [j for j in al if j in (list(choices.values()) + caused_jobs + p.mandatory_jobs)]
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


def solve_with_gurobi(p, quality_consideration = False):
    def constraints(name_constr_pairs):
        for name, cstr in name_constr_pairs:
            model.addConstr(cstr, name)

    try:
        model = Model("rcpsp-ps" + ("-q" if quality_consideration else ""))

        bigM = 99999999

        model.params.threads = 0
        model.params.mipgap = 0
        model.params.timelimit = GRB.INFINITY
        model.params.displayinterval = 5

        x = np.matrix([[model.addVar(0.0, 1.0, 0.0, GRB.BINARY, f'x{j}{t}') for t in p.periods] for j in p.jobs])

        def finish_periods_if_active_in(j, t):
            return range(t, min(t + p.durations[j], p.T))

        if quality_consideration:
            y = np.matrix([[model.addVar(0.0, 1.0, GRB.BINARY, f'y{j}{t}') for t in p.periods] for l in p.qlevels])
            model.setObjective(quicksum(p.u[l,t] * y[l,t] for t in p.periods for l in p.qlevels) - quicksum(p.costs[j] * quicksum(x[j,t] for t in p.periods) for j in p.actualJobs), GRB.MAXIMIZE)
            constraints((f'qlevel_reached_{o}_{l}', p.base_qualities[o] + quicksum(p.quality_improvements[o][j] * quicksum(x[j,t] for t in p.periods) for j in p.actualJobs) >= p.qlevel_requirement[o,l] - bigM * (1-quicksum(y[l,t] for t in p.periods))) for o in p.qattributes for l in p.qlevels)
            constraints((f'sync_x_y_{t}', quicksum(y[l,t] for l in p.qlevels) == x[p.lastJob,t]) for t in p.periods)

        else:
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


def project_from_disk(fn):
    return utils.ObjectFromDict(**decorate_project(flexparse.parse_flexible_project(fn)))


def main():
    # p = utils.ObjectFromDict(**decorate_project(p1))
    p = project_from_disk('Modellendogen0002.DAT')

    # chosen_jobs = [4, 6]
    # al = [0, 2, 5, 3, 1, 7, 4, 6, 8, 9]

    al = p.topOrder
    choices = canonical_choice(p)
    serial_sgs(p, choices, al)
    solve_with_gurobi(p)


if __name__ == '__main__':
    main()
