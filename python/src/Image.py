import SimpleITK as sitk
import numpy as np
import math

class Image():

    """Docstring for Image. 
    Class for image object using SimpleITK 
    """

    image = sitk.Image() 
    original_image = sitk.Image()

    def __init__(self,image = None):

        if image:
            if type(image).__name__=='image':
                self.image = image
                self.original_image = image
            else:
                self.image = self.readImage(image)
                self.original_image = self.image

    def set_image(self,image_path):
        self.image = self.readImage(image_path)
        self.original_image = self.readImage(image_path)

    def restoreImage(self):
        self.image = self.original_image

    def readImage(self, image_path):
        """Docstring for readImage.

        :function: Read image from a path
        :returns: sitk object imaage

        """
        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(image_path)

        if len(dicom_names) == 0:
            image = sitk.ReadImage(image_path, sitk.sitkFloat32)
        else:
            image = sitk.ReadImage(dicom_names, sitk.sitkFloat32)

        del reader
        del dicom_names

        return image

    def tiltCorection(self):
        """Docstring for tiltCorection.

        :function: Tilt Corection for CT images
        """
        image = self.image
        dimension = image.GetDimension()  # Get dimensions
        physical_size = [
            (sz - 1) * spc for sz, spc in zip(image.GetSize(), image.GetSpacing())
        ]  # get physical space

        reference_size = [int(sz / image.GetSpacing()[0]) + 1 for sz in physical_size]
        reference_spacing = [
            phys_sz / (sz - 1) for sz, phys_sz in zip(reference_size, physical_size)
        ]

        reference_image = sitk.Image(reference_size, image.GetPixelIDValue())

        reference_image.SetOrigin(image.GetOrigin())
        reference_image.SetSpacing(reference_spacing)
        reference_image.SetDirection(image.GetDirection())

        image_center = np.array(
            image.TransformContinuousIndexToPhysicalPoint(np.array(image.GetSize()) / 2.0)
        )  # Get physical center of the image
        transform = sitk.AffineTransform(dimension)

        z2 = image.GetDirection()[5]
        y2 = image.GetDirection()[4]
        rad_tilt = math.atan(z2 / y2)

        transform.SetCenter(image_center)
        transform.Shear(1, 2, rad_tilt)

        output_image = sitk.Resample(
            image, reference_image, transform, sitk.sitkLinear, -1000.0
        )

        self.image = output_image

    def normalizeImage(self):
        """Docstring for normalizeImage.

        :function: Normalize teh image 

        """
        max_min_filter = sitk.MinimumMaximumImageFilter()
        max_min_filter.Execute(self.image)
        max_img = max_min_filter.GetMaximum()
        min_img = max_min_filter.GetMinimum()
        self.image = sitk.IntensityWindowing(
            self.image,
            windowMinimum=min_img,
            windowMaximum=max_img,
            outputMinimum=0.0,
            outputMaximum=2 ** 16,
        )
        
        del max_min_filter
        del max_img
        del min_img

    def getSkull(self):
        """Docstring for getSkull.

        :function: Get the skull from a CT image
        :returns: Segmented skull image in sitk format

        """
        skull = sitk.BinaryThreshold(
            self.image, lowerThreshold=300, upperThreshold=1800, insideValue=1, outsideValue=0
        )

        skull = sitk.GrayscaleErode(skull, (2,) * 3, sitk.sitkCross)
        skull = sitk.GrayscaleMorphologicalClosing(skull, (4,) * 3, sitk.sitkBall)
        skull = sitk.GrayscaleFillhole(skull, False)
        skull = sitk.GrayscaleDilate(skull, (4,) * 3, sitk.sitkCross)

        return skull

    def getHeadCT(self):
        """Docstring for getHeadCT.

        :function: Get the head from a CT iamge
        :returns: Segmented head image in sitk format

        """
        head = sitk.OtsuThreshold(self.image, 0, 1, 128, True, 255, True)
        head = sitk.GrayscaleFillhole(head, False)
        head = sitk.GrayscaleErode(head, (3,) * 3, sitk.sitkCross)

        return head

    def getHeadMRI(self):
        """Docstring for getHeadMRI.

        :function: Get the head from a MRI image
        :returns: Segmented head image in sitk format

        """
        head = sitk.OtsuMultipleThresholds(
            self.image,
            numberOfThresholds=4,
            labelOffset=0,
            numberOfHistogramBins=128,
            valleyEmphasis=False,
            returnBinMidpoint=False,
        )
        head = sitk.BinaryThreshold(
            head, lowerThreshold=1, upperThreshold=3, insideValue=1, outsideValue=0
        )
        head = sitk.BinaryMorphologicalClosing(head, (2,) * 3, sitk.sitkBall)
        head = sitk.GrayscaleFillhole(head, False)

        return head

    def electodeSegmentation(self):
        """Docstring for electodeSegmentation.

        :function: Get the e electodes from a SEEG CT image
        :returns: Segmented electodes in sitk format

        """
        max_min_filter = sitk.MinimumMaximumImageFilter()
        max_min_filter.Execute(self.image)
        max_img = max_min_filter.GetMaximum()  # max voxel value image

        treshold_image = sitk.BinaryThreshold(
            self.image, lowerThreshold=1500, upperThreshold=max_img
        )

        skull = self.getSkull()
        head = self.getHeadCT()

        not_skull = sitk.Not(skull)

        mask = sitk.And(head, not_skull)

        electrodes = sitk.And(mask, treshold_image)

        electrodes = sitk.BinaryDilate(electrodes, (1,) * 3, sitk.sitkCross)

        del max_min_filter
        del max_img
        del not_skull
        del mask

        return treshold_image, skull, electrodes

    def resizeImage(self, new_size):
        """Docstring for resizeImage.

        :function: resize the image

        """
        resample = sitk.ResampleImageFilter()
        resample.SetInterpolator(sitk.sitkLinear)
        resample.SetOutputDirection(self.image.GetDirection())
        resample.SetOutputOrigin(self.image.GetOrigin())

        orig_spacing = np.array(self.image.GetSpacing())

        orig_size = np.array(self.image.GetSize())

        new_size = [int(s) for s in new_size]
        new_spacing = orig_spacing * (orig_size / new_size)  # Compute the new spacing
        resample.SetOutputSpacing(new_spacing)

        resample.SetSize(new_size)

        self.image = resample.Execute(self.image)
    
