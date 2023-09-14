import geopandas as gpd
import numpy as np
import pandas as pd

from .data import data
from . import enums


def get_noise_estimate(polygons: gpd.GeoDataFrame, city: enums.City = enums.City.PARIS, measurement: enums.Measurement = enums.Measurement.DAY_EVENING_NIGHT) -> gpd.GeoDataFrame:
    polygons_ = polygons.reset_index(names='polygon_id')
    noise_data_ = data.data(city=city, measurement=measurement)

    polygons_matched_with_noise_data = gpd.sjoin(polygons_, noise_data_, how='left', predicate='intersects')[['polygon_id', 'Classe', 'geometry', 'index_right']]
    polygons_matched_with_noise_data.reset_index(inplace=True, drop=True)
    polygons_matched_with_noise_data['intersection_area'] = _compute_intersection_area_polygons_and_noise_polygons(noise_data=noise_data_, polygons_matched_with_noise_data=polygons_matched_with_noise_data)
    polygons_with_noise_estimate = _aggregate_noise_data_to_polygon_level(polygons_matched_with_noise_data=polygons_matched_with_noise_data)

    polygons_.set_index('polygon_id', inplace=True)
    polygons_ = polygons_.merge(polygons_with_noise_estimate, left_index=True, right_index=True)
    polygons_ = gpd.GeoDataFrame(polygons_, geometry='geometry')
    return polygons_


def _compute_intersection_area_polygons_and_noise_polygons(noise_data: gpd.GeoDataFrame, polygons_matched_with_noise_data: gpd.GeoDataFrame) -> pd.Series:
    def intersection_area(x) -> float:
        if np.isnan(x['index_right']):
            return np.nan
        area = x['geometry'].intersection(noise_data.loc[x['index_right'], 'geometry']).area
        return area

    intersection_area = polygons_matched_with_noise_data.apply(lambda x: intersection_area(x=x), axis=1)
    return intersection_area


def _aggregate_noise_data_to_polygon_level(polygons_matched_with_noise_data: gpd.GeoDataFrame):
    def aggregation_function(x) -> float:
        polygon_noise_data = polygons_matched_with_noise_data.loc[x.index]
        if len(polygon_noise_data) == 1 and np.isnan(polygon_noise_data['intersection_area'].values[0]):
            return np.nan
        else:
            area = polygon_noise_data['intersection_area'].values
            decibels = polygon_noise_data['Classe'].values
            decibels_to_linear_scale = np.power(10, decibels / 10)
            weighted_average_decibels_linear_scale = np.average(decibels_to_linear_scale, weights=area)
            average_decibels = 10 * np.log10(weighted_average_decibels_linear_scale)
            rounded_average_decibels = np.round(average_decibels, decimals=0)
            return rounded_average_decibels

    polygons_with_noise_estimates = polygons_matched_with_noise_data.groupby('polygon_id').agg({'Classe': aggregation_function})
    return polygons_with_noise_estimates

