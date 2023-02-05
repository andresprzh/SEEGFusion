from os.path import join, dirname, abspath
import plotly.express as px
from math import sqrt
import pandas as pd
import glob
import json
import sys
import re



class ValidateData():

    """Classfor the image fusion method validation using structure points in the fixed images."""

    REFERENCE_POINTS = {
        'patient_1':{
            'ct':{}, 'mask':{}, 'no_mask':{},
        },
        'patient_2':{
            'ct':{}, 'mask':{}, 'no_mask':{},
        },
        'patient_3':{
            'ct':{}, 'mask':{}, 'no_mask':{}, 
        },
        'patient_4':{
            'ct':{}, 'mask':{}, 'no_mask':{},
        },
    }
    
    EUCLIDEAN_DISTANCE = {
        'patient_1':{
            'mask':{}, 'no_mask':{},
        },
        'patient_2':{
            'mask':{}, 'no_mask':{},
        },
        'patient_3':{
            'mask':{}, 'no_mask':{}, 
        },
        'patient_4':{
            'mask':{}, 'no_mask':{},
        },
    }

    def __init__(self, folder_path, output_path=None):

        #  self.folder_path = dirname(abspath(__file__))

        self.folder_path = folder_path

        self.output_path = join(
            dirname(
                dirname(
                    dirname(
                        dirname(abspath(__file__))
                    )
                )
            ),
            'data/output/'
        )
        if output_path:
            self.output_path = output_path

        
    def get_json_files(self):
        f'''Get all the json files from an specific path. return an `array` of `str` '''

        pattern = ".*patient_[1-9]_(ct|mask|no_mask)_ref.*\.json$"
        return [file_path for file_path in glob.glob(join(self.folder_path, '*.json')) if re.search(pattern, file_path)]

    def generate_validation_data(self):
        f'''Generate the validation data using the reference points.'''

        self.format_reference_points()

        self.compute_euclidean_distance()

        pandas_data = self.get_pandas_data()
        
        pandas_data = pd.DataFrame.from_dict(pandas_data)
        pandas_data.to_csv(f'{self.output_path}reference_points.csv', index=False)


        fig = px.box(pandas_data, x="Method", y="Euclidean distance", points="all")
        fig.write_image(f'{self.output_path}reference_points_box_plot.png')
        fig.show()


    def format_reference_points(self):
        f'''Organiaze all points of all files in the class variable REFERENCE_POINTS.'''

        json_paths = self.get_json_files()

        for json_path in json_paths:
            with open(json_path) as json_file:
                data = json.load(json_file)
                points = data['markups'][0]['controlPoints']
                self.get_points_by_file(points)

        with open(f"{self.output_path}reference_points.json", "w") as f:
            json.dump(self.REFERENCE_POINTS, f)

    def get_points_by_file(self, points):
        f'''Organize the points of a file in  the class variable REFERENCE_POINTS.'''

        for point in points:
            label_point = point['label']
            label_array = label_point.split('_')
            patient_no = f'patient_{label_array[0]}'
            point_label = label_array[1]
            image_label = '_'.join(label_array[2:])
            #  point_position = point['position']
            point_position = [
                round(point['position'][0]*point['orientation'][0], 3),
                round(point['position'][1]*point['orientation'][4], 3),
                round(point['position'][2]*point['orientation'][-1], 3),
            ]


            self.REFERENCE_POINTS[patient_no][image_label][point_label] = point_position

    def compute_euclidean_distance(self):
        f'''Compute The uclidean distance for the mask and no mask method agains the CT points.'''


        #  Get the patient key from the reference points dictionary
        for patient in self.REFERENCE_POINTS:
            ct_points = self.REFERENCE_POINTS[patient]['ct']
            mask_points = self.REFERENCE_POINTS[patient]['mask']
            no_mask_points = self.REFERENCE_POINTS[patient]['no_mask']
            #  Get the key of the localized reference structures
            for ref_point_key in ct_points:
                ct_point = ct_points[ref_point_key]
                mask_point = mask_points[ref_point_key]
                no_mask_point = no_mask_points[ref_point_key]

                euclidean_distance_mask = (ct_point[0]-mask_point[0])**2 + (ct_point[1]-mask_point[1])**2 + (ct_point[2]-mask_point[2])**2
                euclidean_distance_mask = round(sqrt(euclidean_distance_mask),3)

                euclidean_distance_no_mask = (ct_point[0]-no_mask_point[0])**2 + (ct_point[1]-no_mask_point[1])**2 + (ct_point[2]-no_mask_point[2])**2
                euclidean_distance_no_mask = round(sqrt(euclidean_distance_no_mask),3)

                self.EUCLIDEAN_DISTANCE[patient]['mask'][ref_point_key] = euclidean_distance_mask
                self.EUCLIDEAN_DISTANCE[patient]['no_mask'][ref_point_key] = euclidean_distance_no_mask

        with open(f"{self.output_path}euclidean_distance_reference_points.json", "w") as f:
            json.dump(self.EUCLIDEAN_DISTANCE, f)


    def get_pandas_data(self):
        r"""Convert a dictionary to a valid pandas data. Return `dict`. """

        output = []
        for patient in self.EUCLIDEAN_DISTANCE:
            for method in self.EUCLIDEAN_DISTANCE[patient]:
                for ref_point_key in self.EUCLIDEAN_DISTANCE[patient][method]:
                    euclidan_distance = self.EUCLIDEAN_DISTANCE[patient][method][ref_point_key]
                    output.append({
                        'Euclidean distance': euclidan_distance,
                        'Ref Point': ref_point_key,
                        'patient' : patient,
                        'Method': method,
                    })
        return output

def main():

    #  if len(sys.argv)<1:
    if len(sys.argv)<2:
        print('python generateValidationData.py <path_json_files> <output_path>')
        exit()

    folder_path = sys.argv[1]
    output_path = None
    if len(sys.argv)>=3:
        output_path = sys.argv[2]


    validation_obj = ValidateData(folder_path, output_path)
    validation_obj.generate_validation_data()

if __name__ == "__main__":
    main()
