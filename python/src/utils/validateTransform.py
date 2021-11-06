from time import strftime,localtime
from os.path import join, dirname, abspath
import SimpleITK as sitk
import pathlib
import glob
import sys
import os

TRANSFORM_FILES = []
def main(argv):

    if len(sys.argv)<2:
        print('python validateTransform.py <transforms_path>')
        exit()
    
    transforms_path = sys.argv[1]

    findTransforms(transforms_path)

    i = 1
    for transform in TRANSFORM_FILES:
        #  transformPoints(transform, i)
        transformPoints2(transform, i)
        i+=1

    
def findTransforms(paths):
    paths=glob.glob(paths+'/*', recursive=True)

    # if the subpath are files
    if len(paths) and os.path.isfile(paths[0]):
        for  path in paths:
            file_extension = pathlib.Path(path).suffix
            if file_extension in ['.txt','.mat']:
                try:
                    transform = {
                        'path': path, 
                        'transform': sitk.ReadTransform(path)
                    }
                    TRANSFORM_FILES.append(transform)
                except Exception as e:
                    print(f'Error loading file {path} \n{e}')
    else: 
        for path in paths:
            findTransforms(path)

def transformPoints2(transform, i):

    output_file = join(
        dirname(
            dirname(
                dirname(
                    dirname(abspath(__file__))
                )
            )
        ),
        'data/output/results.csv'
    )

    points = [
        (0.0000, 0.0000, 0.0000),
        (333.9870, 0.0000, 0.0000),
        (0.0000, 333.9870, 0.0000),
        (333.9870, 333.9870, 0.0000),
        (0.0000, 0.0000, 112.0000),
        (333.9870, 0.0000, 112.0000),
        (0.0000, 333.9870, 112.0000),
        (333.9870, 333.9870, 112.0000),
    ]

    os.system(f'echo "image {i}" >> {output_file}')

    for point in points:
        resulting_point = transform['transform'].TransformPoint(point)
        os.system(
            'echo "{:f},{:f},{:f}" >> {:s}'.format(
                resulting_point[0],
                resulting_point[1],
                resulting_point[2],
                output_file
            )
        )



def transformPoints(transform, i):

    output_file  = join(dirname(transform['path']),'validation.txt')

    transform_inverse = transform['transform'].GetInverse()

    points = [
        (0.0000, 0.0000, 0.0000),
        (333.9870, 0.0000, 0.0000),
        (0.0000, 333.9870, 0.0000),
        (333.9870, 333.9870, 0.0000),
        (0.0000, 0.0000, 112.0000),
        (333.9870, 0.0000, 112.0000),
        (0.0000, 333.9870, 112.0000),
        (333.9870, 333.9870, 112.0000),
    ]
    os.system(
        f'echo "--------------------------------------------------------------------------------------------" > {output_file}'
    )
    os.system(f'echo "Transformation Parameters" >> {output_file}')
    os.system(f'echo " " >> {output_file}')
    os.system(f'echo "Investigator(s): Perez Jaime Andres" >> {output_file}')
    os.system(f'echo "Site: Universidad del Valle, Cali, Colombia" >> {output_file}')
    os.system(f'echo "Method: MRI-CT image Registration for SEEG " >> {output_file}')
    os.system(f'echo "Date: {strftime("%d %B %Y, %H:%M:%S", localtime())}" >> {output_file}')
    os.system(f'echo "Patient number: {i}" >> {output_file}')
    os.system(f'echo "From: CT" >> {output_file}')
    os.system(f'echo "To: mr_T1" >> {output_file}')
    os.system(f'echo " " >> {output_file}')
    os.system(
        f'echo "Point      x              y              z              new_x          new_y          new_z" >> {output_file}'
    )
    os.system(f'echo " " >> {output_file}')
    for (index, point) in enumerate(points):
        resulting_point = transform_inverse.TransformPoint(point)
        os.system(
            'echo "{:d}   {:12.4f}   {:12.4f}   {:12.4f}   {:12.4f}   {:12.4f}   {:12.4f}" >> {:s}'.format(
                index+1,
                point[0],
                point[1],
                point[2],
                resulting_point[0],
                resulting_point[1],
                resulting_point[2],
                output_file
            )
        )
    os.system(f'echo " " >> {output_file}')
    os.system(
        f'echo "(All distances are in millimeters.)" >> {output_file}'
    )
    os.system(
        f'echo "--------------------------------------------------------------------------------------------" >> {output_file}'
    )


if __name__ == "__main__":
    main(sys.argv)
