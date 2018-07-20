import numpy as np


def parse_flexible_project(fn):
    def extract_col(lines, col, offset=0):
        return [int(line.split()[col]) + offset for line in lines]

    def extract_last_cols(lines, start_col_incl, offset=0):
        return [[int(d) + offset for d in line.split()[start_col_incl:]] for line in lines]

    def extract_col_pairs(lines, col1, col2, offset=0):
        return [(int(line.split()[col1]) + offset, int(line.split()[col2]) + offset) for line in lines]

    def next_sep(lines, ctr):
        return next(c for c, l in enumerate(lines) if l.startswith('***') and c > ctr)

    def parse_precedence_relations(p, lines):
        prel = []
        for line in lines:
            parts = line.split()
            i = int(parts[0])
            for j in parts[3:]:
                prel.append((i - 1, int(j) - 1))
        p['precedence_relation'] = prel

    def parse_requests_durations(p, lines):
        p['durations'] = extract_col(lines, 2)
        p['demands'] = np.matrix(extract_last_cols(lines, 3))

    def parse_decisions(p, lines):
        p['decision_causing_jobs'] = extract_col(lines, 1, -1)
        p['decision_sets'] = extract_last_cols(lines, 3, -1)

    def parse_conditional_jobs(p, lines):
        p['conditional_jobs'] = extract_col_pairs(lines, 1, 3, -1)

    p = {}

    with open(fn, 'r') as fp:
        lines = fp.readlines()
        nre = 0
        for ctr, line in enumerate(lines):
            if line.startswith('jobs (incl. supersource/sink'):
                p['njobs'] = int(line.split(':')[1])
            elif '- renewable' in line:
                nre = int(line.split()[-2])
                p['renewables'] = list(range(0, nre))
            elif '- nonrenewable' in line:
                nnre = int(line.split()[-2])
                p['non_renewables'] = list(range(nre, nre + nnre))
            elif line.startswith('PRECEDENCE RELATIONS:'):
                prec_start = ctr + 2
                parse_precedence_relations(p, lines[prec_start:prec_start + p['njobs']])
            elif line.startswith('REQUESTS/DURATIONS'):
                reqdur_start = ctr + 3
                parse_requests_durations(p, lines[reqdur_start:reqdur_start + p['njobs']])
            elif line.startswith('RESOURCEAVAILABILITIES'):
                p['capacities'] = [int(capstr) for capstr in lines[ctr + 2].split()]
            elif line.startswith('Entscheidungen'):
                parse_decisions(p, lines[ctr + 2:next_sep(lines, ctr + 2)])
            elif line.startswith('Bedingungen'):
                parse_conditional_jobs(p, lines[ctr + 2:next_sep(lines, ctr + 2)])

    return p


if __name__ == '__main__':
    p = parse_flexible_project('Modellendogen0001.DAT')
    print(p)
