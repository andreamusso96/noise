import os
from . import enums

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_dir = f'{base_dir}/data'


def get_noise_data_file_path(city: enums.City, measurement: enums.Measurement) -> str:
    file_name = f'A_Multi_L{measurement.value}_Agglo/A_Multi_L{measurement.value}_Agglo.shp'
    return f'{data_dir}/{city.value}/{file_name}'
