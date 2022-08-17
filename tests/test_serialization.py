import unittest

import kafkajobs.serialization as serialization
import imageio.v2 as imageio

class TestSerialization(unittest.TestCase):
    def test_issue8(self):
        nparr = imageio.imread('tests/data/issue_8.png')
        #print(f'shape {nparr.shape}')        
        serialized = serialization.imagesNpToStrList([nparr])        


if __name__ == '__main__':
    unittest.main()
