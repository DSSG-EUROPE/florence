import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import logging as log
import os

from ..features import firenzecard, cdr
from ..utils.plotting import gpdutils
from ..utils.database import dbutils

# TODO: put these shapefiles in the DB
SHAPEFILE_DIR = '/mnt/data/shared/aws-data/public-data/Shapefiles'
museum_pts_path = '%s/firenzecard-shapefile/firenzecard.shp' % SHAPEFILE_DIR


def get_florence_shape(epsg=4326):
    italy_regions_path = '%s/boundaries-regions-2015/Com2015_WGS84_g/IT_com_WGS84.shp' % SHAPEFILE_DIR
    italy_regions_shp = gpd.read_file(italy_regions_path).to_crs(epsg=epsg)

    return italy_regions_shp[italy_regions_shp['COMUNE'] == 'Firenze']


def get_voronoi(db_connection, florence_shp=None, pts=None):
    if florence_shp is None:
        florence_shp = get_florence_shape()

    if pts is None:
        pts = get_towers_in_florence(db_connection)

    return gpdutils.make_voronoi_in_shp(pts, florence_shp)


def get_attractions_in_florence(db_connection, florence_shp=None):
    if florence_shp is None:
        florence_shp = get_florence_shape()

    data = firenzecard.get_firenze_locations(db_connection, export_to_csv=False)
    pts = gpdutils.convert_point_data_to_data_frame(data,
                                                    lat_key='latitude',
                                                    lon_key='longitude')

    return gpdutils.get_points_inside_shape(pts, florence_shp)


def get_towers_in_florence(db_connection):
    towers_data = cdr.get_towers_in_florence(db_connection)

    return gpdutils.convert_point_data_to_data_frame(towers_data,
                                                     lat_key='lat',
                                                     lon_key='lon')


def get_voronoi_with_counts(db_connection, hour, voronoi_geo=None,
                            tower_pts=None):

    tower_counts = pd.read_sql((
        'SELECT SUM(foreign_users) AS total_foreign, '
        'SUM(italian_users) AS total_italian, '
        'lat, lon, tower_id '
        'FROM optourism.city_towers_hourly '
        'WHERE date_part(\'hour\', date_hour) = %s '
        'GROUP BY tower_id, lat, lon') % hour, con=db_connection)

    if voronoi_geo is None:
        voronoi_geo = get_voronoi(db_connection, pts=tower_pts)

    voronoi_with_counts = pd.merge(voronoi_geo,
                                   tower_counts,
                                   how='left',
                                   left_on=['lat', 'lon'],
                                   right_on=['lat', 'lon'])

    voronoi_with_counts = voronoi_with_counts.assign(
        count_area=lambda x: (x.total_italian + x.total_foreign) / x.geometry.area)

    voronoi_with_counts = voronoi_with_counts.assign(
        count_area_log=lambda x: np.log(x.total_italian + x.total_foreign) / x.geometry.area)

    return voronoi_with_counts


def plot_polygon_collection(ax, geoms, values=None, colormap='Greens',
                            facecolor=None, edgecolor=None, alpha=0.7,
                            linewidth=1.0, **kwargs):

    """ Plot a collection of Polygon geometries """

    patches = []

    for poly in geoms:
        a = np.asarray(poly.exterior)
        patches.append(Polygon(a))

    patches = PatchCollection(patches,
                              facecolor=facecolor,
                              linewidth=linewidth,
                              edgecolor=edgecolor,
                              alpha=alpha,
                              **kwargs)

    if values is not None:
        patches.set_array(values)
        patches.set_cmap(colormap)

    ax.add_collection(patches, autolim=True)
    # ax.autoscale_view()
    return patches


def plot_voronoi_per_hour(db_connection):
    florence_shp = get_florence_shape()

    towers = get_towers_in_florence(db_connection)

    attractions = get_attractions_in_florence(db_connection,
                                              florence_shp=florence_shp)

    fig = plt.figure(figsize=(10, 8), dpi=300)
    ax = plt.gca()
    plt.axes().set_aspect('equal', 'datalim')

    florence_shp.plot(ax=ax, color='lightblue')
    # towers.plot(ax=ax, color='navy')
    attractions.plot(ax=ax, color='red')

    voronoi_with_counts = None
    col = None

    for hour in range(24):
        if voronoi_with_counts is None:
            voronoi_with_counts = get_voronoi_with_counts(db_connection, hour,
                                                          tower_pts=towers)

            col = plot_polygon_collection(ax, voronoi_with_counts.geometry, values=voronoi_with_counts['count_area'])
        else:
            voronoi_with_counts = get_voronoi_with_counts(db_connection, hour,
                                                          tower_pts=towers)
            col.set_array(voronoi_with_counts['count_area'])

        curr_dir = os.path.dirname(os.path.abspath(__file__))
        filename = 'hour_%s.png' % hour
        path = os.path.join(curr_dir, 'choropleth', filename)

        fig.savefig(path, dpi=300)
        print('saved image for hour ' + str(hour))

    plt.clf()
    plt.close()


if __name__ == '__main__':
    connection = dbutils.connect()
    plot_voronoi_per_hour(connection)
    connection.close()

