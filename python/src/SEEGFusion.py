import SimpleITK as sitk
import numpy as np
from Image import Image
import gc
   

class ImageRegistration():

    """Docstring for ImageRegistration. 
    Class for imageRegistration object, has the funtions 
    and atributes the registration of MRI and CT images 
    from an SEEG
    """

    transform = None

    def __init__(self, ct = None, mri = None):
        self.fixed_img = Image(ct) 
        self.moving_img = Image(mri)

    def rigidRegistration(self, initial_transform, mask_sampling = None, sampling_perc = 0.1, num_iter = 100):
        registration_method = sitk.ImageRegistrationMethod()

        # Similarity ct_image settings MI.
        registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=128)
        registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
        registration_method.SetMetricSamplingPercentage(sampling_perc)

        if mask_sampling:
            registration_method.SetMetricFixedMask(mask_sampling)

        registration_method.SetInterpolator(sitk.sitkBSpline)

        # Optimizer settings.
        registration_method.SetOptimizerAsGradientDescent(
            learningRate=1.0,
            numberOfIterations=num_iter,
            convergenceMinimumValue=1e-6,
            convergenceWindowSize=10,
        )
        registration_method.SetOptimizerScalesFromPhysicalShift()

        # Setup for the multi-resolution framework.
        registration_method.SetShrinkFactorsPerLevel(shrinkFactors=[4, 2, 1])
        registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[2, 1, 0])

        registration_method.SetInitialTransform(initial_transform, inPlace=False)

        final_transform = registration_method.Execute(
            sitk.Cast(self.fixed_img, sitk.sitkFloat32),
            sitk.Cast(self.moving_img, sitk.sitkFloat32),
        )

        print("Final metric value: {0}".format(registration_method.GetMetricValue()))
        print(
            "Optimizer's stopping condition, {0}".format(
                registration_method.GetOptimizerStopConditionDescription()
            )
        )

        del registration_method

        gc.collect()

        self.transform = final_transform

        return final_transform

    def preProsImage(self):
        """preProsImage: Docstring for preProsImage.
        :function: Pre prosessing of the images before registration
        """
        self.fixed_img.image = sitk.IntensityWindowing(self.fixed_img.image, windowMinimum=-300, windowMaximum=2000, outputMinimum=0.0, outputMaximum=2**16)
        self.moving_img.normalizeImage()
        self.moving_img.image = sitk.CurvatureAnisotropicDiffusion(self.moving_img.image, timeStep=0.03, conductanceParameter=2, conductanceScalingUpdateInterval=1, numberOfIterations=5)


class ImageFusion(ImageRegistration):

    """Docstring for ImageFusion. 
    Class for imageFusion object, has the funtions and 
    atributes tofuse MRI and CT images from an SEEG
    """

    def __init__(self, ct = None, mri = None, atlas=None):
        super().__init__(ct, mri)
        self.fixed_img.tiltCorection()
        self.atlas = Image(atlas)
        self.aligned_mri = Image()

    def setAtlat(self,atlas):
        self.atlas = Image(atlas)

    def alignHead(self, thresh, electrodes_image, skull):

        self.atlas.resizeImage(np.array(self.aligned_mri.image.GetSize()))


        registration = ImageRegistration(self.atlas.image, self.aligned_mri.image)
        reg_transform = sitk.CenteredTransformInitializer(self.atlas.image, self.aligned_mri.image, sitk.Euler3DTransform(), sitk.CenteredTransformInitializerFilter.GEOMETRY)
        
        align_head_transform = registration.rigidRegistration(reg_transform, None, 0.05, 60)

        self.aligned_mri = sitk.Resample(self.aligned_mri.image, self.atlas, align_head_transform, sitk.sitkLinear, 0.0, self.aligned_mri.image.GetPixelID())
        self.mri = sitk.Resample(self.fixed_img, self.atlas, align_head_transform, sitk.sitkLinear, 0.0, self.fixed_img.image.GetPixelID())
        thresh = sitk.Resample(thresh, self.atlas, align_head_transform, sitk.sitkLinear, 0.0, thresh.GetPixelID())
        skull = sitk.Resample(skull, self.atlas, align_head_transform, sitk.sitkLinear, 0.0, skull.GetPixelID() )
        electrodes_image = sitk.Resample(electrodes_image, self.atlas, align_head_transform, sitk.sitkLinear, 0.0, electrodes_image.GetPixelID())

        return (thresh, skull, electrodes_image, align_head_transform,)

    def fuseImages(self, transform = sitk.AffineTransform(3), use_mask = True, align_head = False):
        """Docstring for fuseImages.

        :function: Fuse the images using rigid registration
        :returns: Fused image

        """
        treshold_image, skull, electrodes_image = self.fixed_img.electodeSegmentation()

        if use_mask:
            mask_electrodes = sitk.Not(electrodes_image)
        else:
            mask_electrodes = None

        # pre prosses the input images
        super().preProsImage()

        # Make the registration
        reg_transform = sitk.CenteredTransformInitializer(
            self.fixed_img.image, self.moving_img.image, 
            transform,
            sitk.CenteredTransformInitializerFilter.GEOMETRY
        )
        align_moving_transform = super().rigidRegistration(reg_transform, mask_electrodes, 1.0, 100)

        del mask_electrodes

        # Register MRI using the transform
        self.aligned_mri.image = sitk.Resample(self.moving_img.image, self.fixed_img.image, align_moving_transform, sitk.sitkLinear, 0.0, self.moving_img.image.GetPixelID())
        
        if align_head:
            (treshold_image, skull, electrodes_image, align_head_transform ) = self.alignHead(treshold_image, electrodes_image, skull)
