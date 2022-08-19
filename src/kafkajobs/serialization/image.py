import imageio.v3 as iio
import numpy as np
import base64


def imageToRgbImage(image):
    rank = len(image.shape)
    if rank == 2:
        # monochrome
        # adding color channels
        return np.stack((image, image, image), axis=2)
    else:
        # coloured
        return image[:,:,:3] # discarding alpha channel if any    

def imageNpToB64SerializedStruct(npImage):
    rgbNumpyImage = imageToRgbImage(npImage)
    jpg_encoded_bytes = iio.imwrite("<bytes>", rgbNumpyImage, extension=".jpeg")    

    image = {
        'type': "jpg",
        'data': base64.encodebytes(jpg_encoded_bytes).decode("utf-8").replace("\n","")
    }
    return image    

def imagesNpToStrList(npImages):
    """Obsolete: left for backward compatibility"""
    return [imageNpToB64SerializedStruct(x) for x in npImages]

def imageB64SerializedStructToNp(b64SerializedStruct):
    imgType = b64SerializedStruct['type']
    image_b64 : str = b64SerializedStruct['data']
    imageData = base64.decodebytes(image_b64.encode("utf-8"))
    imNumpy = iio.imread(imageData, extension=f".{imgType}")
    # guard againes old version of encoders
    return imageToRgbImage(imNumpy)

def imagesFieldToNp(images):
    """Obsolete: left for backward compatibility"""
    return [imageB64SerializedStructToNp(x) for x in images]    
