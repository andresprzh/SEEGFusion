from SEEGFusion import ImageFusion
import SimpleITK as sitk
import sys
from os.path import dirname, abspath, join

def main(argv):

    if len(sys.argv)<2:
        print('python Fuse.py ct_path mri_path output_path')
        exit()
    elif len(sys.argv)<3:
        print('please especify MRi')
        exit()
    elif len(sys.argv)<4:
        output_path = join(
            dirname(
                dirname(
                    dirname(abspath(__file__))
                )
            ), 
            'data/output'
        )
    else :
        output_path = sys.argv[3]

    ct_path = sys.argv[1]
    mri_path = sys.argv[2]
    
    fusion = ImageFusion(ct_path,mri_path)

    output_image  = fusion.fuseImages()

    sitk.WriteImage(output_image, join(output_path,'fused_image.nii'))
    sitk.WriteImage(fusion.aligned_mri.image, join(output_path,'registered.nii'))
    sitk.WriteTransform(fusion.registration_transform, join(output_path, 'registration_transform.txt'))

    print(f'Image fused in {output_path}')

if __name__ == "__main__":
    main(sys.argv)
