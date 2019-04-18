import unittest
from BWMatch import BWMatch
import filecmp
from BWMatch import parse_command_line_arguments

class TestBWMatch(unittest.TestCase):
    """
    see https://stackoverflow.com/questions/3942820/how-to-do-unit-testing-of-functions-writing-files-using-python-unittest/3943697#3943697
    """

    def test_e_coli(self):
        B = BWMatch('e_coli_index.txt')
        B.match_all_patterns(patternfile='e_coli_1000.fa', outputfile='ecoli_matches.txt')
        self.assertTrue(filecmp.cmp('ecoli_matches.txt', 'ecoli_matches_baseline.txt'))
        
    def test_string_argument(self):
        B = BWMatch('test_index.txt')
        self.assertEqual(B.find_matches('CAT'), [14, 3, 17])


if __name__ == '__main__':
    unittest.main()
    
    
