from SEEGFusion import ImageFusion
import SimpleITK as sitk
import json
import sys
from os.path import dirname, abspath, join

def main(argv):

    if len(sys.argv)<2:
        print('python Fuse.py ct_path mri_path')
        exit()
    elif len(sys.argv)<3:
        print('please especify MRi')
        exit()

    ct_path = sys.argv[1]
    mri_path = sys.argv[2]

    fusion = ImageFusion(ct_path,mri_path)

    output_image  = fusion.fuseImages()

    output_path = join(dirname(dirname(abspath(__file__))), 'data/output/fused_image.nii')

    import pdb; pdb.set_trace()
    sitk.WriteImage(output_image, output_path)

if __name__ == "__main__":
    main(sys.argv)
