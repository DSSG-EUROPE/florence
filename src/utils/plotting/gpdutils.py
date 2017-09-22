import pandas as pd
import geopandas as gpd
import shapely as sp
import numpy as np
from scipy.spatial import Voronoi


def convert_point_csv_to_data_frame(path, lat_key='lat', lon_key='lon',
                                    encoding='utf-8', separator='\t',
                                    decimal='.', index_col=None, epsg=4326):
    """
    Takes a CSV file with latitude and longitude columns and returns a Geopandas
    DataFrame object. This function accepts optional configuration params for
    the CSV

    Args:
        path (string): file path for the CSV file
        lat_key (string): name of the latitude column
        lon_key (string): name of the longitude column
        encoding (string): encoding of CSV file
        separator (string): separator value for the CSV
        decimal (string): character used for decimal place in the CSV
        index_col (string): name of the index column
        epsg (int): spatial reference system code for geospatial data

    Returns:
        GeoPandas.GeoDataFrame: the contents of the supplied CSV file in the
        format of a GeoPandas GeoDataFrame
    """

    csv_points = pd.read_csv(path, encoding=encoding, sep=separator,
                             index_col=index_col, decimal=decimal)

    zipped_data = zip(csv_points[lon_key], csv_points[lat_key])
    geo_points = [sp.geometry.Point(xy) for xy in zipped_data]
    crs = {'init': 'epsg:' + str(epsg)}

    return gpd.GeoDataFrame(csv_points, crs=crs, geometry=geo_points)\
        .to_crs(epsg=epsg)


def convert_point_data_to_data_frame(data, lat_key='lat', lon_key='lon',
                                     epsg=4326):
    """
    Takes a data set with latitude and longitude columns and returns a Geopandas
    GeoDataFrame object.

    Args:
        data (Pandas.DataFrame): the lat/lon data to convert to GeoDataFrame
        lat_key (string): name of the latitude column
        lon_key (string): name of the longitude column
        epsg (int): spatial reference system code for geospatial data

    Returns:
        GeoPandas.GeoDataFrame: the contents of the supplied data in the
        format of a GeoPandas GeoDataFrame
    """

    zipped_data = zip(data[lon_key], data[lat_key])
    geo_points = [sp.geometry.Point(xy) for xy in zipped_data]
    crs = {'init': 'epsg:' + str(epsg)}

    return gpd.GeoDataFrame(data, crs=crs, geometry=geo_points)\
        .to_crs(epsg=epsg)


def get_points_inside_shape(points, shape):
    """
    Takes a point geometry object and a polygon geometry shape file
    and returns all of the points within the boundaries of that shape

    Args:
        points (Geopandas.GeoDataFrame): Point geometry
        shape (Geopandas.GeoDataFrame): Polygon geometry shape file object

    Returns:
        Geopandas.GeoDataFrame: All of the points that are within the outline of
            the shape
    """

    return points[points.within(shape.unary_union)]


def create_voronoi(points, epsg=4326):
    """
    Make a voronoi diagram geometry out of point definitions

    Args:
        points (Geopandas.GeoDataFrame): The centroid points for the voronoi
        epsg (int): spatial reference system code for geospatial data

    Returns:
        Geopandas.GeoDataFrame: The polygon geometry for the voronoi diagram
    """

    np_points = [np.array([pt.x, pt.y]) for pt in np.array(points.geometry)]
    vor = Voronoi(np_points)

    lines = [
        sp.geometry.LineString(vor.vertices[line])
        for line in vor.ridge_vertices
        if -1 not in line
    ]

    voronoi_poly = sp.ops.polygonize(lines)
    crs = {'init': 'epsg:' + str(epsg)}
    return gpd.GeoDataFrame(crs=crs, geometry=list(voronoi_poly))\
        .to_crs(epsg=epsg)


def make_voronoi_in_shp(points, shape, epsg=4326):
    """
    Make a voronoi diagram geometry out of point definitions and embed it in a
    shape.

    Args:
        points (Geopandas.GeoDataFrame): The centroid points for the voronoi
        shape (Geopandas.GeoDataFrame): The shapefile to contain the voronoi
            inside
        epsg (int): spatial reference system code for geospatial data

    Returns:
        Geopandas.GeoDataFrame: The polygon geometry for the voronoi diagram
            embedded inside the shape
    """
    voronoi_geo = create_voronoi(points, epsg=epsg)
    voronoi_geo_in_shape = get_points_inside_shape(voronoi_geo, shape)

    shape_with_voronoi = gpd.sjoin(points, voronoi_geo_in_shape, how="inner",
                                   op='within')

    del shape_with_voronoi['geometry']

    return voronoi_geo_in_shape.merge(shape_with_voronoi, left_index=True,
                                      right_on='index_right')
