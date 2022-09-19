import argparse


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument('--file_path_employees', type=str, default='./input_repository/data_lake/ZHCMX_0799_03.XLSX',
                        help='Path for employees file from DataLake')
    parser.add_argument('--file_path_education', type=str, default='./input_repository/data_lake/ZHCMX_0799_05.XLSX',
                        help='Path for education file from DataLake')
    parser.add_argument('--path_educate_dict', type=str, default='./input_repository/data_lake/справочник_образований.XLSX',
                        help='Path for education dictionary')
    parser.add_argument('--file_path_courses', type=str, default='./input_repository/data_lake/ZHCMX_0799_06.XLSX',
                        help='Path for courses file from DataLake')



#    parser.add_argument('--gpu', type=int, default=0, help='GPU id')
#    parser.add_argument('--mode', type=str, default='train', choices=['train', 'test', 'valid'])
#    parser.add_argument('--data_path', type=str, default="./dataset", required=False,
#                        help='Path to image directories')
#    parser.add_argument('--classes_json', type=str, default="./dataset/cat_to_name.json", required=False,
#                        help='Path to json description file classes')


    args = parser.parse_args()

    return args