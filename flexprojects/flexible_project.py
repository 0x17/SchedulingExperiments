import numpy as np
import utils
from flexprojects.parser import parse_flexible_project


def decorate_quality_attributes(p, q, chosen_customer):
    qlevels = range(q['nqlevels'])

    def revenue_for_period(l, t):
        rperiods = q['customers']['revenue_periods']
        revs = q['customers']['revenues'][chosen_customer]
        if t in rperiods:
            return revs[l, t - min(rperiods)]
        elif t < min(rperiods):
            return revs[l, 0]
        else:
            return revs[l, len(rperiods) - 1]

    return {**q, **{
        'qlevels': qlevels,
        'qattributes': range(q['nqattributes']),
        'u': np.matrix([[revenue_for_period(l, t) for t in p['periods']] for l in qlevels])
    }}


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

def project_from_disk(fn):
    return utils.ObjectFromDict(**decorate_project(parse_flexible_project(fn)))


