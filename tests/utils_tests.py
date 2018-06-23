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


