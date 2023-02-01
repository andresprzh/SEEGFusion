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
    """Get the euclidean distance between the point of the reference image 
    and the method using and a method that do no use a registration mask."""
    if len(sys.argv)<2:
        print('python generateData.py <data_file>')
        exit()
    path_file = sys.argv[1]
    data = {}
    with open(path_file, newline='') as csvfile:
        file_reader = csv.reader(csvfile, delimiter=',')
        image = 'image'
        dataset = 'default'
        for row in file_reader:
            if 'image' in row[0]:
                image = row[0]  
                data[dataset][image] = []
            elif len(row) == 1:
                dataset = row[0]
                data[dataset] = {}
            else:
                data[dataset][image].append(
                    [round(float(number), 4) for number in row]
                ) 

    euclidean_dis = {
        'NO MASK'   : {},
        'MASK'      : {}
    }

    euclidean_dis['NO MASK'] = getEuclideanDistance(data['REFERENCE'], data['NO MASK'])
    euclidean_dis['MASK'] = getEuclideanDistance(data['REFERENCE'], data['MASK'])
    #  euclidean_dis['DIFFERENCE'] = getDiferenceEuc(euclidean_dis['NO MASK'], euclidean_dis['MASK'])
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
    with open(f'{output_path}results.json', 'a',encoding="utf-8") as file:
        json.dump(euclidean_dis, file)

    #  pandas_data = {
    #      'No Mask': getPandasData(euclidean_dis['NO MASK']),
    #      'Mask': getPandasData(euclidean_dis['MASK'])
    #  }
    pandas_data = getPandasData(euclidean_dis)
    pandas_data = pd.DataFrame.from_dict(pandas_data)
    __import__('pdb').set_trace()

    pandas_data2 = getPandasData0(euclidean_dis)
    pandas_data2 = pd.DataFrame.from_dict(pandas_data2)
    fig = px.box(pandas_data, x="Method", y="Euclidean distance", points="all")
    fig.write_image(f'{output_path}results.png')
    fig.show()

def getPandasData0(euclidean_dis):
    output = {}
    for method in euclidean_dis:
        output[method] = []
        for image in euclidean_dis[method]:
            for distance in euclidean_dis[method][image]:
                output[method].append(distance)
    return output

def getPandasData(euclidean_dis):
    output = []
    #  for image in euclidean_dis:
    #      for distance in euclidean_dis[image]:
    #          output.append(distance)
    #  return output

    for dataset in euclidean_dis:
        for image in euclidean_dis[dataset]:
            for distance in euclidean_dis[dataset][image]:
                output.append({
                    'Euclidean distance': distance,
                    'Method' : dataset
                })
    return output
            

def getEuclideanDistance(dataset1, dataset2):
    output_data = {}
    for image in dataset1:
        output_data[image] = []
        for index,point1 in enumerate(dataset1[image]):
            point2 = dataset2[image][index]
            e_d = (point1[0]-point2[0])**2 + (point1[1]-point2[1])**2 + (point1[2]-point2[2])**2
            e_d = round(sqrt(e_d),4)
            output_data[image].append(e_d)


    return output_data

def getDiferenceEuc(dataset1, dataset2):
    output_data = {}
    for image in dataset1:
        output_data[image] = []
        for index,distance1 in enumerate(dataset1[image]):
            distance2 = dataset2[image][index]
            difference = round(distance1 -  distance2, 4)
            output_data[image].append(difference)
    return output_data

if __name__ == "__main__":
    main(sys.argv)
