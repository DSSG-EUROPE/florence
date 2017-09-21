import pandas as pd
import numpy as np
import os
import json
from ..utils.database import dbutils


def get_dwell_time_df(db_connection, table_name):
    query = """
      SELECT
          cust_id,
          prev_cust_id,
          tower_id,
          prev_tower_id,
          dwell_time,
          near_airport,
          in_florence_comune
        FROM %(name)s
    """ % {'name': table_name}

    users = pd.read_sql(query, con=db_connection)

    users['key'] = (
    (users['tower_id'] != users['prev_tower_id']) | (
    users['cust_id'] != users['prev_cust_id'])).astype(int).cumsum()
    groups = users.groupby(
        ['cust_id', 'tower_id', 'near_airport', 'in_florence_comune', 'key'],
        sort=False)['dwell_time'].sum().reset_index()

    transitions = groups.loc[groups['dwell_time'] >= pd.Timedelta('20 minutes')]
    transitions['in_florence'] = transitions.apply(
        lambda x: (x['in_florence_comune'] | x['near_airport']), axis=1)
    del transitions['in_florence_comune']
    del transitions['key']

    curated = transitions.loc[(transitions['in_florence'] == True) |
                              ((transitions['cust_id'] == transitions[
                                  'cust_id'].shift(1)) &
                               (transitions['in_florence'] != transitions[
                                   'in_florence'].shift(1))) |
                              ((transitions['cust_id'] == transitions[
                                  'cust_id'].shift(-1)) &
                               (transitions['in_florence'] != transitions[
                                   'in_florence'].shift(-1)))]
    return curated


def get_most_common_location(dataframe):
    grouped = dataframe.groupby(['tower_region']).count().reset_index()
    grouped.rename(columns={'dwell_time': 'weight'}, inplace=True)
    grouped = grouped.sort_values('weight', ascending=False)

    return grouped.filter(['tower_region', 'weight'], axis=1)


def get_tower_vertices(db_connection, table_name):
    query = """
      SELECT DISTINCT cdr.tower_id, cdr.lat, cdr.lon, towers.region_name
        FROM %(name)s as cdr
        JOIN optourism.cdr_labeled_towers as towers
        ON towers.id = cdr.tower_id
    """ % {'name': table_name}

    return pd.read_sql(query, con=db_connection)


def get_network_edges(connection,
                      table_name='optourism.foreigners_daytripper_dwell_time',
                      end_file_path=None,
                      start_file_path=None,
                      density_file_path=None):

    users = get_dwell_time_df(connection, table_name)
    tower_vertices = get_tower_vertices(connection, table_name)

    users['tower_region'] = users.apply(lambda x: tower_vertices.loc[
        tower_vertices['tower_id'] == x['tower_id']].iloc[0]['region_name'] if
    x['in_florence'] == False else x['tower_id'], axis=1)

    users['prev_tower_id'] = users['tower_region'].shift(1)

    users.loc[(users['cust_id'] != users['cust_id'].shift(
        1)), 'prev_tower_id'] = 'source'

    filtered = users.loc[(users['in_florence'] == True) &
                              (users['tower_region'] != users['prev_tower_id'])]

    grouping = filtered.groupby(
        ['tower_region', 'prev_tower_id']).count().reset_index()

    grouping.rename(columns={'cust_id': 'weight', 'tower_region': 'to', 'prev_tower_id': 'from'}, inplace=True)
    edges = grouping.filter(['to', 'from', 'weight'], axis=1)

    users['dwell_time_minutes'] = users['dwell_time'] / np.timedelta64(1, 'm')
    relative_region_density = users.loc[users['in_florence'] == True].groupby(
        'tower_id').sum()

    filtered_density = relative_region_density.filter(
        ['tower_id', 'dwell_time_minutes'])
    sorted_density = filtered_density.sort_values('dwell_time_minutes',
                                                  ascending=False)

    sorted_density = sorted_density.reset_index('tower_id')
    sorted_density.rename(columns={'dwell_time_minutes': 'density'}, inplace=True)

    if density_file_path:
        sorted_density.to_csv(density_file_path, index=False)

    if end_file_path:
        ending = users[users['in_florence'] == True].groupby(['cust_id']).last()
        end_weights = get_most_common_location(ending)
        end_weights['percentage'] = end_weights['weight'] / end_weights[
            'weight'].sum()

        end_weights.to_csv(end_file_path, index=False)

    if start_file_path:
        beginning = users[users['in_florence'] == True].groupby(['cust_id']).first()
        start_weights = get_most_common_location(beginning)
        start_weights['percentage'] = start_weights['weight'] / start_weights['weight'].sum()

        start_weights.to_csv(start_file_path, index=False)

    return edges, sorted_density


if __name__ == '__main__':
    connection = dbutils.connect()
    edges, densities = get_network_edges(connection)
