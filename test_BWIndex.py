import unittest
import filecmp

from BWIndex import BWIndex

class TestBWIndex(unittest.TestCase):

    def test_small_index(self):
        BWIndex('small_index.txt', genomefile='genome.txt', countgap=100, suffixgap=100)
        self.assertTrue(filecmp.cmp('small_index.txt', 'small_index_baseline.txt'))
        
        
if __name__ == '__main__':
    unittest.main()
