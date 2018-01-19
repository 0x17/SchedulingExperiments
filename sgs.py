from project import active_periods


def serial_schedule_generation_scheme(p, al, zmax = None):
    J, T, R = p.main_sets()

    def zmaxfn(r):
        return 0 if zmax is None else zmax[r]

    def schedule_job_at(j, stj, sts):
        sts[j] = stj
        for r in R:
            for t in active_periods(stj, p.durations[j]):
                res_rem[r][t] -= p.demands[j][r]

    res_rem = [[p.capacities[r] + zmaxfn(r)] * p.numPeriods for r in R]
    sts = [None]*p.numJobs
    sts[0] = al[0]

    for j in al[1:]:
        stj = p.last_pred_ft(j, sts)
        while not p.res_feasible_starting_at(j, stj, res_rem):
            stj += 1
        schedule_job_at(j, stj, sts)

    return sts
