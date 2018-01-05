import unittest
import basedata
import utils
import os


class TestBasedata(unittest.TestCase):
    def test_extract_key_val_for_line(self):
        line = '  MinJob             :  30      & minimal number of jobs per project'
        k, v = basedata.extract_key_val_for_line(line)
        self.assertEqual('MinJob', k)
        self.assertEqual('30', v)

    def test_read_parameters_from_basefile(self):
        self.assertTrue(os.path.exists('EXPL.BAS'))
        pdict = basedata.read_parameters_from_basefile('EXPL.BAS', ['NrOfPro', 'MinJob'])
        self.assertEqual({'NrOfPro': '1', 'MinJob': '30'}, pdict)

    def test_overwrite_parameters_in_basefile(self):
        orig_fn = 'EXPL.BAS'
        mod_fn = 'EXPL_MOD.BAS'

        self.assertTrue(os.path.exists(orig_fn))

        nvals = {'NrOfPro': '2', 'Complexity': '2.0'}

        old_lines = utils.slurp_lines(orig_fn)

        basedata.overwrite_parameters_in_basefile(orig_fn, mod_fn, nvals)

        self.assertTrue(os.path.exists(orig_fn))
        self.assertTrue(os.path.exists(mod_fn))

        new_lines = utils.slurp_lines(orig_fn)
        self.assertEqual(old_lines, new_lines)

        modified_lines = utils.slurp_lines(mod_fn)

        for ix, line in enumerate(modified_lines):
            no_key = True
            for key in nvals.keys():
                if key in line:
                    no_key = False
                    k, v = basedata.extract_key_val_for_line(line)
                    self.assertEqual(key, k)
                    self.assertEqual(nvals[key], v)
            if no_key:
                self.assertEqual(old_lines[ix], line)
        utils.force_delete_file(mod_fn)
