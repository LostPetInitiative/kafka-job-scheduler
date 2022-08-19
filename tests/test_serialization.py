import unittest
import base64


import kafkajobs.serialization as serialization

import imageio.v2 as imageio
import numpy as np

class TestSerialization(unittest.TestCase):
    def test_image_round_trip(self):
        nparr = imageio.imread('tests/data/343911.jpg')
        shape = nparr.shape
        
        roundTripped = serialization.imageB64SerializedStructToNp(serialization.imageNpToB64SerializedStruct(nparr))

        assert roundTripped.shape == shape, f'shape {roundTripped.shape} is not {shape}'        

    def test_issue8(self):
        nparr = imageio.imread('tests/data/issue_8.png')
        #print(f'shape {nparr.shape}')        
        serialized = serialization.imagesNpToStrList([nparr])

    def test_deserializing_monochrome(self):
        # manual encoding
        with open('tests/data/monochrome.png', 'rb') as photoFile:
            photo = photoFile.read()

            image = {
                'type': "jpg",
                'data': base64.encodebytes(photo).decode("utf-8").replace("\n","")
            }
        
        deserialized = serialization.imageB64SerializedStructToNp(image) # this one creates 3 colour channels        
        assert deserialized.shape == (400, 400, 3), f'shape {deserialized.shape}'

if __name__ == '__main__':
    unittest.main()
