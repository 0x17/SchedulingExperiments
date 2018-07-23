import numpy as np



def core_loop():
    pass

def serial_sgs(p, choices, al):
    caused_jobs = [caused for causing, caused in p.conditional_jobs if causing in choices.values()]
    impl_jobs_al = [j for j in al if j in (list(choices.values()) + caused_jobs + p.mandatory_jobs)]
    enough_nonrenewables = all(sum([p.demands[j, non_renewable] for j in impl_jobs_al]) <= p.capacities[non_renewable] for non_renewable in p.non_renewables)
    # assert enough_nonrenewables
    if not enough_nonrenewables:
        return {'obj': p.T + sum(max(0, sum([p.demands[j, non_renewable] for j in impl_jobs_al]) - p.capacities[non_renewable]) for non_renewable in p.non_renewables)}

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

    return {'schedule': sts, 'obj': sts[p.lastJob]}


def print_result(res):
    if 'schedule' in res:
        sts, obj = res['schedule'], res['obj']
        print(f'Schedule = {sts}')
    print(f'Objective = {obj}')