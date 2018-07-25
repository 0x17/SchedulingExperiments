import unittest
import utils


class TestUtils(unittest.TestCase):
    def test_filter_csv(self):
        csv_strs = ['instance;NC;RF', 'j3012_1.sm;0.8;1.7']
        exp_out = ['instance;RF', 'j3012_1.sm;1.7']
        self.assertEqual(exp_out, utils.filter_csv(csv_strs, column_names=['instance', 'RF']))
        self.assertEqual(exp_out, utils.filter_csv('\n'.join(csv_strs), column_names=['instance', 'RF']))
        self.assertEqual(exp_out, utils.filter_csv(csv_strs, column_indices=[0, 2]))
        self.assertEqual('\n'.join(exp_out), utils.filter_csv(csv_strs, column_indices=[0, 2], as_str=True))

    def test_randelem(self):
        ntries = 10
        nums = [3, 8, 12, 20]
        picks = [utils.randelem(nums) for i in range(ntries)]
        for pick in picks:
            self.assertTrue(pick in nums)
        self.assertFalse(min(picks) == max(picks))

    def test_random_pairs(self):
        nums = list(range(10))
        pairs = utils.random_pairs(nums)
        self.assertEquals(5, len(pairs))
        for pair in pairs:
            self.assertTrue(pair[0] in nums)
            self.assertTrue(pair[1] in nums)
            self.assertEquals(1, pairs.count(pair))
