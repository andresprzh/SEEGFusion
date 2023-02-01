"""
Generate validation data from the transformed and reference point inside a .csv file 
"""
from os.path import join, dirname, abspath
import plotly.express as px
import pandas as pd
from math import sqrt
import json
import csv
import sys

def main(argv):
    """Get the euclidean distance between the points of the reference image 
    and the methods using and no using a registration mask."""
    if len(sys.argv)<2:
        path_file = join(
            dirname(
                dirname(
                    dirname(
                        dirname(abspath(__file__))
                    )
                )
            ),
            'data/validation_point.json'
        )
    else:
        path_file = sys.argv[1]
    with open(path_file) as json_file:
        data = json.load(json_file)
        euclidean_dis = {
            'NO_MASK'   : {},
            'MASK'      : {}
        }

        euclidean_dis['NO_MASK'] = getEuclideanDistance(data['REFERENCE'], data['NO_MASK'])
        euclidean_dis['MASK'] = getEuclideanDistance(data['REFERENCE'], data['MASK'])
        output_path = join(
            dirname(
                dirname(
                    dirname(
                        dirname(abspath(__file__))
                    )
                )
            ),
            'data/output/'
        )
        with open(f'{output_path}results_3.json', 'a',encoding="utf-8") as file:
            json.dump(euclidean_dis, file)

    pandas_data = getPandasData(euclidean_dis)
    pandas_data = pd.DataFrame.from_dict(pandas_data)
    pandas_data.to_csv(f'{output_path}results3.csv', index=False)
    
    
    fig = px.box(pandas_data, x="Method", y="Euclidean distance", points="all")
    fig.write_image(f'{output_path}results3.png')
    fig.show()

    #  pandas_data = pandas_data[pandas_data['Image']!='image_6']
    #
    #  fig2 = px.box(pandas_data, x="Method", y="Euclidean distance", points="all")
    #  fig2.write_image(f'{output_path}results2_2.png')
    #  fig2.show()


def getPandasData(euclidean_dis):
    r"""Convert a dictionary to a valid pandas data. Return `dict`.

    :param euclidean_dis: `dict` dictonary with the uclidean distances.
    """
    output = []
    for dataset in euclidean_dis:
        for image in euclidean_dis[dataset]:
            for ref_point_key in euclidean_dis[dataset][image]:
                euclidan_distance = euclidean_dis[dataset][image][ref_point_key]
                output.append({
                    'Euclidean distance': euclidan_distance,
                    'Ref Point': ref_point_key,
                    'Image': image,
                    'Method' : dataset
                })
    return output
            

def getEuclideanDistance(dataset1, dataset2):
    r"""Calculate the euclidean distance between dataset1 and dataset2. Return `dict`.

    :param dataset1: `dict` dictonary with the coordinates of reference points.
    :param dataset2: `dict` dictonary with the coordinates of reference points.
    """
    output_data = {}
    for image in dataset1:
        output_data[image] = {}
        for ref_point_key in dataset1[image]:
            point1 = [float(x) for x in dataset1[image][ref_point_key]]
            point2 = [float(x) for x in dataset2[image][ref_point_key]]
            e_d = (point1[0]-point2[0])**2 + (point1[1]-point2[1])**2 + (point1[2]-point2[2])**2
            e_d = round(sqrt(e_d),4)
            #  print(image, ref_point_key)
            #  __import__('pdb').set_trace()
            output_data[image][ref_point_key] = e_d

    return output_data

if __name__ == "__main__":
    main(sys.argv)
