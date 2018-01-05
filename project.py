import json


class Project:
    def __init__(self, filename, **fields):
        self.__dict__.update(fields)
        self.J, self.T, self.R = self.main_sets()
        self.filename = filename

    def succs(self, i):
        return [j for j in range(self.numJobs) if self.adjMx[i][j] == 1]

    def preds(self, j):
        return [i for i in range(self.numJobs) if self.adjMx[i][j] == 1]

    def main_sets(self):
        return [range(self.numJobs), range(self.heuristicMaxMakespan + 1), range(self.numRes)]

    def last_pred_ft(self, j, sts):
        return max([sts[i] + self.durations[i] for i in self.preds(j)] + [0])

    def is_order_feasible(self, sts):
        return all(self.last_pred_ft(j, sts) <= stj for j, stj in enumerate(sts))

    def res_feasible_starting_at(self, j, stj, res_rem):
        return all(res_rem[r][t] - self.demands[j][r] >= 0 for t in active_periods(stj, self.durations[j]) for r in self.R)

    def active_in_period(self, t, sts):
        return [j for j in self.J if sts[j] < t <= sts[j] + self.durations[j]]

    def job_active_in_periods(self, j, periods, sts):
        return any(t in range(sts[j] + 1, sts[j] + self.durations[j] + 1) for t in periods)

    def remaining_capacity_in_period(self, r, t, sts, oc=0):
        return self.capacity[r] + oc - sum(self.demands[j][r] for j in self.active_in_period(t, sts))

    def is_res_feasible(self, sts, res_rem=None, oc=0):
        assert(res_rem is None or oc == 0)
        if res_rem is not None:
            return all(res_rem[r][t] >= 0 for t in self.T for r in self.R)
        else:
            return all(self.remaining_capacity_in_period(r, t, sts, oc) >= 0 for t in self.T for r in self.R)

    def compute_res_rem_for_schedule(self, sts):
        return [ [ self.remaining_capacity_in_period(r, t, sts) for t in self.T ] for r in self.R ]

    def average_remaining_capacity(self, r, sts):
        return sum(self.remaining_capacity_in_period(r, t, sts) for t in self.T) / len(self.T)

    def low_utilisation_periods(self, r, sts, threshold = None):
        threshold = threshold if threshold is not None else self.average_remaining_capacity(r, sts)
        return [ t for t in self.T if self.remaining_capacity_in_period(r, t, sts) <= threshold ]

    def active_in_low_utilisation_periods(self, r, sts, threshold = None):
        return [j for j in self.J if self.job_active_in_periods(j, self.low_utilisation_periods(r, sts, threshold), sts)]



def load_project(fn):
    with open(fn, 'r') as fp:
        return Project(fn, **json.load(fp))


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
