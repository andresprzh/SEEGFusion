import SimpleITK as sitk
import numpy as np
from Image import Image
   

class ImageRegistration():

    """Docstring for ImageRegistration. 
    Class for imageRegistration object, has the funtions 
    and atributes the registration of MRI and CT images 
    from an SEEG
    """

    def __init__(self, fix_path = None, mov_path = None):
        self.fix_image = Image(fix_path) 
        self.mov_image = Image(mov_path)


class ImageFusion(ImageRegistration):

    """Docstring for ImageFusion. 
    Class for imageFusion object, has the funtions and 
    atributes tofuse MRI and CT images from an SEEG
    """

    def __init__(self, fix_path = None, mov_path = None):
        pass
