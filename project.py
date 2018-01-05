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
        return [range(self.numJobs), range(self.heuristicMaxMakespan), range(self.numRes)]

    def last_pred_ft(self, j, sts):
        return max([sts[i] + self.durations[i] for i in self.preds(j)] + [0])

    def is_order_feasible(self, sts):
        return all(self.last_pred_ft(j, sts) <= stj for j, stj in enumerate(sts))

    def res_feasible_starting_at(self, j, stj, res_rem):
        return all(res_rem[r][t] - self.demands[j][r] >= 0 for t in active_periods(stj, self.durations[j]) for r in self.R)


def load_project(fn):
    with open(fn, 'r') as fp:
        return Project(fn, **json.load(fp))


def makespan(res):
    return res['Sj'][-1]


def edges_to_adj_mx(num_jobs, edges):
    return [[1 if (i, j) in edges else 0 for j in range(num_jobs)] for i in range(num_jobs)]


def adj_mx_to_edges(adj_mx):
    return [(i, j) for j in range(len(adj_mx[0])) for i in range(len(adj_mx)) if adj_mx[i][j] == 1]


def active_periods(stj, dj):
    return range(stj + 1, stj + dj + 1)
