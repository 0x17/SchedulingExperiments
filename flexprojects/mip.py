from gurobipy import *
import numpy as np


def solve_with_gurobi(p):
    def constraints(name_constr_pairs):
        for name, cstr in name_constr_pairs:
            model.addConstr(cstr, name)

    try:
        quality_consideration = hasattr(p, 'qlevels')
        overtime_consideration = hasattr(p, 'zmax')

        model = Model("rcpsp-ps" + ("-q" if quality_consideration else ""))

        bigM = 99999999

        model.params.threads = 0
        model.params.mipgap = 0
        model.params.timelimit = GRB.INFINITY
        model.params.displayinterval = 5

        x = np.matrix([[model.addVar(0.0, 1.0, 0.0, GRB.BINARY, f'x{j}_{t}') for t in p.periods] for j in p.jobs])
        z = np.matrix([[model.addVar(0.0, 1.0, 0.0, GRB.BINARY, f'z{r}_{t}') for t in p.periods] for r in p.renewables]) if overtime_consideration else None

        def finish_periods_if_active_in(j, t):
            return range(t, min(t + p.durations[j], p.T))

        if quality_consideration:
            def qimprove(o, j):
                return p.quality_improvements[o][j] if j in p.quality_improvements[o] else 0

            y = np.matrix([[model.addVar(0.0, 1.0, 0.0, GRB.BINARY, f'y{l}_{t}') for t in p.periods] for l in p.qlevels])
            overtime_costs = 0 if not overtime_consideration else quicksum(p.kappa[r] * z[r,t] for r in p.renewables for t in p.periods)
            model.setObjective(quicksum(p.u[l, t] * y[l, t] for t in p.periods for l in p.qlevels) - quicksum(p.costs[j] * quicksum(x[j, t] for t in p.periods) for j in p.actual_jobs) - overtime_costs, GRB.MAXIMIZE)
            constraints((f'qlevel_reached_{o}_{l}', p.base_qualities[o] + quicksum(qimprove(o, j) * quicksum(x[j, t] for t in p.periods) for j in p.actual_jobs) >= p.qlevel_requirement[o, l] - bigM * (1 - quicksum(y[l, t] for t in p.periods))) for o in p.qattributes for l in p.qlevels)
            constraints((f'sync_x_y_{t}', quicksum(y[l, t] for l in p.qlevels) == x[p.lastJob, t]) for t in p.periods)

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
                     quicksum(p.demands[j, r] * quicksum(x[j, tau] for tau in finish_periods_if_active_in(j, t)) for j in p.actual_jobs) <= p.capacities[r] + (z[r,t] if overtime_consideration else 0)) for r in p.renewables for t in p.periods)
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