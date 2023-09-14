from typing import List

import pandas as pd
import geopandas as gpd

from . import config
from . import enums


# Lazy loading
class Data:
    def __init__(self):
        self._data = None

    def load_data(self, city: enums.City, measurement: enums.Measurement):
        self._data = gpd.read_file(config.get_noise_data_file_path(city=city, measurement=measurement))
        self._data.to_crs(epsg=2154, inplace=True)

    def data(self, city: enums.City, measurement: enums.Measurement) -> pd.DataFrame:
        if self._data is None:
            self.load_data(city=city, measurement=measurement)
        return self._data


data = Data()