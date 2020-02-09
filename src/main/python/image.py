'''
Wrapper for PIL's Image module to mimick necessary functions in Wand API.
'''

import io

from PIL import Image as PIL_Image


def make_black_or_white(threshold):
    black = 0
    white = 255
    return lambda pix_val: black if pix_val < white * threshold else white


class Image():
    '''
    Wraps for PIL's Image module to mimick necessary functions in Wand API.
    '''

    def __init__(self, filepath):

        self.image = PIL_Image.open(filepath)
        self.image = self.image.convert('RGB')

        self.filepath = filepath
        self.compression_quality = 90

    def clone(self):
        '''
        Makes a copy/clone of the current Image by
        returning a new instance of the Image with current filepath.
        '''

        return Image(filepath=self.filepath)

    def make_blob(self):
        '''
        Returns the current Image in binary format.
        '''

        buffer = io.BytesIO()
        self.image.save(
            buffer,
            format='JPEG',
            quality=self.compression_quality,
            optimize=True
        )

        return buffer.getvalue()

    def threshold(self, threshold_value=0.5):
        '''
        Does thresholding to the current Image with the given threshold value.
        '''

        self.image = self.image.convert('L').point(
            make_black_or_white(threshold_value)
        )

    def save(self, filepath):
        '''
        Saves the current Image to the given filepath.
        '''

        self.image.save(
            filepath,
            quality=self.compression_quality
        )
