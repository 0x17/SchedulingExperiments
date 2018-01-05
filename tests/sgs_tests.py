import unittest

from sgs import ascending_top_order
from project import Project, edges_to_adj_mx


class TestSGS(unittest.TestCase):
    pass
    '''def test_ascending_top_order(self):
        p = Project('', **{'numJobs': 7, 'numRes': 0, 'heuristicMaxMakespan': 0, 'adjMx': edges_to_adj_mx(7, [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (3, 6), (4, 6), (5, 6)])})
        top_order = ascending_top_order(p)
        self.assertEqual(p.numJobs, len(top_order))
        self.assertTrue(all([j in top_order for j in range(p.numJobs)]))
        self.assertEqual(0, top_order[0])
        self.assertEqual(p.numJobs - 1, top_order[-1])
        self.assertEqual(list(range(p.numJobs)), top_order)'''
