import utils

from gurobipy import *

from project import makespan, load_project, Project


def build_model(p, deadline=None):
    try:
        model = Model("rcpsp-roc")

        model.params.threads = 0
        model.params.mipgap = 0
        model.params.timelimit = GRB.INFINITY
        model.params.displayinterval = 5

        def add_named_constraints(constraint_name_pairs):
            for cstr, name in constraint_name_pairs:
                model.addConstr(cstr, name)

        J, T, R = p.main_sets()

        last_job = p.numJobs - 1

        def time_window(j):
            return [t for t in T if p.efts[j] <= t <= p.lfts[j]]

        def time_window_for_demand(j, t):
            return [tau for tau in T if t <= tau <= t + p.durations[j] - 1]

        x = [[model.addVar(0.0, 1.0 if t in time_window(j) else 0.0, 0.0, GRB.BINARY, 'x{0},{1}'.format(j, t)) for t in
              T] for j in J]
        z = [[model.addVar(0.0, p.zmax[r], 0.0, GRB.CONTINUOUS, 'z{0},{1}'.format(r, t)) for t in T] for r in R]

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

            add_named_constraints(
                [(ft(i) <= st(j), '{0}_before_{1}'.format(i, j)) for i in J for j in J if p.adjMx[i][j] == 1])

            def cum_demand(r, t):
                return quicksum([p.demands[j][r] * x[j][tau] for j in J for tau in time_window_for_demand(j, t)])

            add_named_constraints(
                [(cum_demand(r, t) <= p.capacities[r] + z[r][t], 'rfeas_of_{0}_in_{1}'.format(r, t)) for r in R for t in
                 T])

            if deadline is not None:
                model.addConstr(ft(last_job) <= deadline, 'deadline')

        add_objective()
        add_restrictions()

        return {'model': model, 'xjt': x, 'zrt': z}

    except GurobiError as e:
        print(e)


def assert_optimality(model):
    for bad_status in [GRB.Status.INF_OR_UNBD, GRB.Status.INFEASIBLE, GRB.Status.UNBOUNDED]:
        assert (model.status != bad_status)
    assert (model.status == GRB.Status.OPTIMAL)


def parse_results(p, model, xjt, zrt):
    J, T, R = p.main_sets()

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

    assert (p.is_order_feasible(sts))

    return {'Sj': sts,
            'Fj': [st(j) + p.durations[j] for j in J],
            'oc': overtime_costs,
            'revenue': revenue,
            'obj': obj}


def set_mip_starts(p, xjt, initial_solution):
    assert(makespan(initial_solution) <= p.heuristicMaxMakespan)
    for j in p.J:
        for t in p.T:
            xjt[j][t].start = 1.0 if initial_solution[j] + p.durations[j] == t else 0.0


def solve(instance_or_filename, initial_solution=None, deadline=None, project_modification_callback=None):
    p = instance_or_filename if isinstance(instance_or_filename, Project) else load_project(instance_or_filename)

    if project_modification_callback is not None:
        project_modification_callback(p)

    model_compound = build_model(p, deadline)

    model, xjt, zrt = [model_compound[key] for key in ['model', 'xjt', 'zrt']]

    if initial_solution is not None:
        set_mip_starts(p, xjt, initial_solution)

    model.update()
    model.write('mymodel.lp')
    model.optimize()

    return parse_results(p, model, xjt, zrt)


def serialize_results(results):
    with open('myschedule.txt', 'w') as fp:
        ostr = ''
        for j, stj in enumerate(results['Sj']):
            ostr += '{0}->{1}\n'.format(j + 1, stj)
        fp.write(ostr)

    with open('myprofit.txt', 'w') as fp:
        fp.write(str(results['obj']))


def results_for_deadline_range(instance_filename, lb, ub):
    result_dict = {}
    for deadline in range(lb, ub + 1):
        result_dict[deadline] = solve(instance_filename, deadline=deadline)
    return result_dict


def shortest_with_overtime(instance_filename):
    def modifier_callback(p):
        p.kappa = [0.0] * len(p.kappa)

    return solve(instance_filename, project_modification_callback=modifier_callback)


def shortest_without_overtime(instance_filename):
    def modifier_callback(p):
        p.zmax = [0] * len(p.zmax)

    return solve(instance_filename, project_modification_callback=modifier_callback)


def collect_shortest_diffs(path):
    odict = {}
    for fn in os.listdir(path):
        if fn.endswith('.json'):
            with_ot_ms = makespan(shortest_with_overtime(path + fn))
            wout_ot_ms = makespan(shortest_without_overtime(path + fn))
            odict[fn] = {'makespan_with_overtime': with_ot_ms, 'makespan_without_overtime': wout_ot_ms,
                         'delta': wout_ot_ms - with_ot_ms}
    return odict
