from os.path import dirname, abspath, join, exists
from os import makedirs
from SEEGFusion import ImageFusion
import SimpleITK as sitk
import json
import sys

def main(argv):

    if len(sys.argv)<2:
        print('python FuseManyImages.py <json_path> <output_path>')
        exit()
    if len(sys.argv)<3:
        output_path = join(
            dirname(
                dirname(
                    dirname(abspath(__file__))
                )
            ),
            'data/output'
        )
    else:
        output_path = sys.argv[2]

    json_path = sys.argv[1]

    with open(json_path) as json_file:
        images_path = json.load(json_file)["images"]

    i = 1
    for image_path in images_path:
        fusion = ImageFusion(image_path['fixed'],image_path['moving'])
        output_image = fusion.fuseImages(use_mask=True, sampling_perc=0.4, num_iter=200)

        output_image_path = join(output_path, str(i))
        if not exists(output_image_path):
            makedirs(output_image_path)
        sitk.WriteImage(output_image, join(output_image_path,'fused_image.nii'))
        sitk.WriteImage(fusion.aligned_mri.image, join(output_image_path,'registered.nii'))
        sitk.WriteTransform(fusion.registration_transform, join(output_image_path, 'registration_transform.txt'))

        print(f'Image {i} fused in : {output_image_path}')

        i+=1


if __name__ == "__main__":
    main(sys.argv)
