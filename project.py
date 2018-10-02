import json
import utils


class Project:
    def __init__(self, filename, **fields):
        self.__dict__.update(fields)
        self.J, self.T, self.R = self.main_sets()
        self.filename = filename
        self.special_periods_collectors = {
            'low_residual': self.low_residual_capacity_periods,
            'high_residual': self.high_residual_capacity_periods,
            'low_cumulative': self.low_cumulative_demands_periods,
            'high_cumulative': self.high_cumulative_demands_periods
        }

    # region Precedence and Order
    def succs(self, i):
        return [j for j in range(self.numJobs) if self.adjMx[i][j] == 1]

    def preds(self, j):
        return [i for i in range(self.numJobs) if self.adjMx[i][j] == 1]

    def last_pred_ft(self, j, sts):
        return max([sts[i] + self.durations[i] for i in self.preds(j)] + [0])

    def is_schedule_order_feasible(self, sts):
        return all(self.last_pred_ft(j, sts) <= stj for j, stj in enumerate(sts))

    # endregion

    def main_sets(self):
        return [range(self.numJobs), range(self.heuristicMaxMakespan + 1), range(self.numRes)]

    # region Resource consumption and feasibility
    def res_feasible_starting_at(self, j, stj, res_rem):
        return all(
            res_rem[r][t] - self.demands[j][r] >= 0 for t in active_periods(stj, self.durations[j]) for r in self.R)

    def active_in_period(self, t, sts):
        return [j for j in self.J if sts[j] < t <= sts[j] + self.durations[j]]

    def job_active_in_periods(self, j, periods, sts):
        return any(t in range(sts[j] + 1, sts[j] + self.durations[j] + 1) for t in periods)

    def is_schedule_resource_feasible(self, sts, res_rem=None):
        if res_rem is not None:
            return all(res_rem[r][t] >= 0 for t in self.T for r in self.R)
        else:
            return all(self.residual_capacity_in_period(r, t, sts) >= 0 for t in self.T for r in self.R)

    def compute_res_rem_for_schedule(self, sts):
        return [[self.residual_capacity_in_period(r, t, sts) for t in self.T] for r in self.R]

    # endregion

    # region Period resource statistics
    def cumulative_demands_in_period(self, r, t, sts):
        return sum(self.demands[j][r] for j in self.active_in_period(t, sts))

    def residual_capacity_in_period(self, r, t, sts):
        return self.capacities[r] - self.cumulative_demands_in_period(r, t, sts)

    def average_resource_spec_common(self, r, sts, func):
        return utils.average((func(r, t, sts) for t in self.T), len(self.T))

    def average_residual_capacity(self, r, sts):
        return self.average_resource_spec_common(r, sts, self.residual_capacity_in_period)

    def average_cumulative_demands(self, r, sts):
        return self.average_resource_spec_common(r, sts, self.cumulative_demands_in_period)

    # endregion

    # region Special periods
    def edge_periods_common(self, r, sts, low, average_func, in_period_func):
        threshold = average_func(r, sts)
        c = -1 if low else 1
        return [t for t in self.T if in_period_func(r, t, sts) >= c * threshold]

    def cumulative_demands_edge_periods(self, r, sts, low):
        return self.edge_periods_common(r, sts, low, self.average_cumulative_demands, self.cumulative_demands_in_period)

    def residual_capacity_edge_periods(self, r, sts, low):
        return self.edge_periods_common(r, sts, low, self.average_residual_capacity, self.residual_capacity_in_period)

    def high_residual_capacity_periods(self, r, sts):
        return self.residual_capacity_edge_periods(r, sts, False)

    def low_residual_capacity_periods(self, r, sts):
        return self.residual_capacity_edge_periods(r, sts, True)

    def high_cumulative_demands_periods(self, r, sts):
        return self.cumulative_demands_edge_periods(r, sts, False)

    def low_cumulative_demands_periods(self, r, sts):
        return self.cumulative_demands_edge_periods(r, sts, True)

    # endregion

    # region Jobs in special periods
    def jobs_active_in_periods(self, sts, periods):
        return [j for j in self.J if self.job_active_in_periods(j, periods, sts)]

    def active_in_special_periods(self, speciality_type, r, sts):
        return self.jobs_active_in_periods(sts, self.special_periods_collectors[speciality_type](r, sts))

    # endregion

    # region Objective function and terms
    def revenue(self, sts):
        return self.u[makespan(sts)]

    def total_costs(self, sts):
        return sum(
            max(-self.residual_capacity_in_period(r, t, sts), 0) * self.kappa[r] for r in self.R for t in self.T)

    def profit(self, sts):
        return self.revenue(sts) - self.total_costs(sts)
    # endregion


def load_project(fn):
    with open(fn, 'r') as fp:
        return Project(fn, **json.load(fp))


def row_major(mx):
    return [val for row in mx for val in row]


def flatten_project(fn, maxT = None):
    cols = []
    p = load_project(fn)

    maxT = len(p.T) if maxT is None else maxT
    upscaled_revenues = p.u + [0]*(maxT - len(p.u))
    assert len(upscaled_revenues) == maxT

    for vec in [p.durations, p.capacities, p.kappa, p.zmax, upscaled_revenues]:
        cols += map(str, vec)

    for mx in [p.demands, p.adjMx]:
        cols += map(str, row_major(mx))

    return cols


def makespan(res):
    if type(res) is dict and 'Sj' in res:
        return res['Sj'][-1]
    elif type(res) is list:
        return res[-1]
    else:
        return 0


def edges_to_adj_mx(num_jobs, edges):
    return [[1 if (i, j) in edges else 0 for j in range(num_jobs)] for i in range(num_jobs)]


def adj_mx_to_edges(adj_mx):
    return [(i, j) for j in range(len(adj_mx[0])) for i in range(len(adj_mx)) if adj_mx[i][j] == 1]


def active_periods(stj, dj):
    return range(stj + 1, stj + dj + 1)


if __name__ == '__main__':
    print(flatten_project('j3010_1.json'))
