"""Fuse Many image of CT and RMI using a json file """
from os.path import dirname, abspath, join, exists
from os import makedirs
from SEEGFusion import ImageFusion
import SimpleITK as sitk
import json
import sys

def main(argv):

    output_path = join(
        dirname(
            dirname(
                dirname(abspath(__file__))
            )
        ),
        'data/output'
    )
    use_mask = True
    if len(sys.argv)<2:
        print('python FuseManyImages.py <json_path> <output_path> <use_mask>')
        exit()
    if len(sys.argv)>=3:
        output_path = sys.argv[2]
    if len(sys.argv)>=4:
        use_mask = json.loads(sys.argv[3].lower())

    json_path = sys.argv[1]

    with open(json_path) as json_file:
        images_path = json.load(json_file)["images"]

    fuse_images(images_path, output_path, use_mask)



def fuse_images(images_path, output_path, use_mask=True):
    i = 1
    name_pos = '_mask' if use_mask else '_no_mask'
    for image_path in images_path:
        fusion = ImageFusion(image_path['fixed'],image_path['moving'])
        output_image = fusion.fuseImages(use_mask=True, sampling_perc=0.4, num_iter=200)

        output_image_path = join(output_path, str(i))
        if not exists(output_image_path):
            makedirs(output_image_path)
        sitk.WriteImage(output_image, join(output_image_path,f'fused_image{name_pos}.nii'))
        sitk.WriteImage(fusion.aligned_mri.image, join(output_image_path,f'registered{name_pos}.nii'))
        sitk.WriteTransform(fusion.registration_transform, join(output_image_path, f'registration_transform{name_pos}.txt'))
        print(f'Image {i} fused with {name_pos} in : {output_image_path}')
        i+=1


if __name__ == "__main__":
    main(sys.argv)
