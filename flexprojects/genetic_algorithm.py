import numpy as np
import utils
import flexprojects.flexible_project as fp


def caused_jobs(p, choices):
    return utils.mapping_range(p.conditional_jobs, choices.values())


def implemented_jobs(p, choices):
    return [j for j in p.jobs if j in (list(choices.values()) + caused_jobs(p, choices) + p.mandatory_jobs)]


def compute_non_renew_demands(p, choice_repr):
    impl_jobs = implemented_jobs(p, choice_repr) if len(choice_repr) == p.ndecisions else [j for j in p.jobs if choice_repr[j]]
    return [sum([p.demands[j, non_renewable] for j in impl_jobs]) for non_renewable in p.non_renewables]


def has_enough_nonrenewables(p, choice_repr):
    demands = compute_non_renew_demands(p, choice_repr)
    return all(demands[non_renewable] <= p.capacities[non_renewable] for non_renewable in p.non_renewables)


def initial_project_structure(p, max_tries):
    v = []
    for ctr in range(max_tries):
        v = [j in p.mandatory_jobs for j in p.jobs]
        for e in p.decisions:
            if v[p.decision_causing_jobs[e]]:
                v[utils.randelem(p.decision_sets[e])] = True

        for k in [k for j in p.jobs for k in p.jobs if v[j] and (j, k) in p.conditional_jobs]:
            v[k] = True

        if has_enough_nonrenewables(p, v):
            break
    return v


POP_SIZE = 80
NUM_GENS = 100


def choices_from_impl(p, v):
    return [p.decision_sets[e][k] for e in p.decisions for k in p.jobs if v[p.decision_sets[e][k]]]


class Individual:
    def __init__(self, p, ps, al):
        self.ps = ps
        self.al = al
        self.fitness = -serial_sgs(p, choices_from_impl(p, ps), al)['obj']


def al_opc(m, f, q):
    return m[:q] + [j for j in f if j not in m[:q]]


def ps_opc(p, m, f, q):
    def inherit_choices(decisions, choices, v):
        for e in decisions:
            for j in p.decision_sets[e]:
                v[j] = False
            v[choices[e]] = True

    mc = choices_from_impl(p, m)
    fc = choices_from_impl(p, f)

    v = [j in p.mandatory_jobs for j in p.jobs]
    inherit_choices(p.decisions[:q], mc, v)

    for e in p.decisions[q:]:
        dcj = p.decision_causing_jobs[e]
        if v[dcj]:
            if f[dcj]:
                inherit_choices([e], fc, v)
            else:
                inherit_choices([e], mc, v)

    return v


def crossover(p, m, f):
    v = ps_opc(p, m.ps, f.ps, utils.randelem(p.decisions))
    al = al_opc(m.al, f.al, utils.randelem(p.jobs))
    return Individual(p, v, al)


# TODO: Implement
def mutate(p, indiv):
    return indiv


def solve_with_ga(p):
    pop = [Individual(p, initial_project_structure(p, 128), fp.random_topological_order(p.preds, p.jobs)) for i in range(POP_SIZE)]
    for i in range(NUM_GENS):
        pairs = utils.random_pairs(pop)
        children = []
        for pair in pairs:
            children += [crossover(p, pair[0], pair[1]), crossover(p, pair[1], pair[0])]
        children = [mutate(p, child) for child in children]
        pop += children


def serial_sgs(p, choices, al):
    enough_nonrenewables = has_enough_nonrenewables(p, choices)
    if not enough_nonrenewables:
        return {'obj': p.T + sum(max(0, sum([p.demands[j, non_renewable] for j in [j for j in al if j in implemented_jobs(p, choices)]]) - p.capacities[non_renewable]) for non_renewable in p.non_renewables)}

    def latest_pred_finished(j, sts, impl_jobs):
        return max([sts[i] + p.durations[i] for i in p.preds[j] if i in impl_jobs] + [0])

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

    impl_jobs = implemented_jobs(p, choices)

    for j in al:
        if j not in impl_jobs: continue
        t = latest_pred_finished(j, sts, impl_jobs)
        while not enough_capacity(res_rem, t, j): t += 1
        sts[j] = t
        reduce_res_rem(res_rem, j, t)

    return {'schedule': sts, 'obj': sts[p.lastJob]}


def print_result(res):
    if 'schedule' in res:
        sts, obj = res['schedule'], res['obj']
        print(f'Schedule = {sts}')
    print(f'Objective = {obj}')
