from utils.database import dbutils
from features import network_analysis as na
from output import cdr_fountain as cdr
import json
import os
import pandas as pd
import math


def create_geojson(data, edgelist, region_density=None, geojson_path=None, props=None):
    location_dict = {
        'source': {
            'name': 'Unknown',
            'fullName': 'Unknown'
        },
        'start': {
            'name': 'Start',
            'fullName': 'Start'

        },
        'end': {
            'name': 'End',
            'fullName': 'End'

        }
    }

    edgelist['perc_to'] = edgelist['weight']
    group_sum = edgelist.groupby(['to', 'from', 'weight']).agg({'perc_to': 'sum'})
    group_perc = group_sum.groupby(level=0).apply(lambda x: 100 * x / float(x.sum()))
    group_perc = group_perc.reset_index()

    group_perc['perc_from'] = group_perc['weight']
    group_sum = group_perc.groupby(['from', 'to', 'weight', 'perc_to']).agg({'perc_from': 'sum'})
    group_both_perc = group_sum.groupby(level=0).apply(lambda x: 100 * x / float(x.sum()))

    final_edgelist = group_both_perc.reset_index()

    if geojson_path is None:
        features = [create_feature(f, final_edgelist, location_dict,
                                       props=props) for f in data]
    else:
        with open(geojson_path) as f:
            geometries = process_geometries_geojson(json.load(f))
            features = [create_feature(f, final_edgelist, location_dict,
                                       geometries=geometries,
                                       densities=region_density) for f in data]

    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }

    return geojson, location_dict


def process_geometries_geojson(geometries):
    geo_dict = {}

    for feature in geometries['features']:
        geo_dict[str(feature['properties']['id'])] = {
            'geometry': feature['geometry'],
            'area': feature['properties']['area']
        }

    return geo_dict


def create_feature(datum, edgelist, location_dict,
                   geometries=None, densities=None, props=None):

    id, lat, lon, name, full_name = datum
    lat = float(lat)
    lon = float(lon)
    id = str(id)

    edgelist['to'] = edgelist['to'].apply(
        lambda row: str(int(row)) if isinstance(row, float) else str(row))
    edgelist['from'] = edgelist['from'].apply(
        lambda row: str(int(row)) if isinstance(row, float) else str(row))

    edges = edgelist.loc[(edgelist['to'] == id) | (edgelist['from'] == id)]

    area = None
    if geometries is not None and id in geometries:
        geometry_obj = geometries[id]
        geometry = geometry_obj['geometry']
        area = geometry_obj['area']
    else:
        geometry = create_geometry(lat, lon)

    density = None
    if densities is not None:
        densities['tower_id'] = densities['tower_id'].apply(str)

        if area is not None and area > 0:
            densities['density'] = densities['density'] / area

        densities['density'] = densities['density'] / densities['density'].max()
        first_match = densities[densities['tower_id'] == id].head(1)
        if not first_match.empty:
            density = first_match['density'].iloc[0]

    total_visits = None
    total_fc_visits = None
    if props is not None:
        props['museum_id'] = props['museum_id'].apply(str)
        first_match = props[props['museum_id'] == id].head(1)

        if not first_match.empty:
            total_visits = first_match['visitors'].iloc[0]

        total_fc_visits = str(int(edgelist[(edgelist['to'] == id)].sum()['weight']))

    feature = {
        'type': 'Feature',
        'geometry': geometry,
        'properties': create_properties(id, name, full_name, [lon, lat],
                                        edges, location_dict,
                                        density=density, area=area,
                                        total_visits=total_visits,
                                        total_fc_visits=total_fc_visits)
    }

    return feature


def create_geometry(lat, lon):
    geometry = {
        'type': 'Polygon',
        'coordinates': [create_circle(lat, lon)]
    }

    return geometry


def create_square(lat, lon):
    rad = 0.0001
    return [
        [round(lon + rad, 7), round(lat + rad, 7)],
        [round(lon + rad, 7), round(lat - rad, 7)],
        [round(lon - rad, 7), round(lat - rad, 7)],
        [round(lon - rad, 7), round(lat + rad, 7)]
    ]


def create_circle(lat, lon):
    N = 20  # number of discrete sample points to be generated along the circle
    radius = 18

    # generate points
    points = []
    for k in range(N):
        # compute
        angle = math.pi * 2 * k / N
        dx = radius * math.cos(angle)
        dy = radius * math.sin(angle)

        new_lat = lat + (180 / math.pi) * (dy / 6378137)
        new_lon = lon + (180 / math.pi) * (dx / 6378137) / math.cos(
            lat * math.pi / 180)

        points.append([round(new_lon, 7), round(new_lat, 7)])

    return points


def create_properties(id, name, full_name, centroid, edges, location_dict,
                      density=None, area=None, total_visits=None,
                      total_fc_visits=None):
    in_flows, out_flows = create_flows(edges, id)

    props = {
        'name': name,
        'fullName': full_name,
        'id': str(id),
        'inFlows': in_flows,
        'outFlows': out_flows,
        'centroid': centroid,
        'density': density,
        'totalVisits': total_visits,
        'totalFcVisits': total_fc_visits,
        'area': area
    }

    location_dict[str(id)] = {
        'name': name,
        'fullName': full_name,
    }

    return props


def create_flows(edges, id):
    in_flows = {}
    out_flows = {}
    in_edges = edges.loc[(edges['to'] == id)]
    out_edges = edges.loc[(edges['from'] == id)]

    for index, edge in in_edges.iterrows():
        from_id = edge['from']
        if isinstance(from_id, float):
            from_id = int(from_id)
            in_flows[from_id] = {
                'weight': edge['weight'],
                'percentage': edge['perc_to']
            }
        else:
            in_flows[from_id] = {
                'weight': edge['weight'],
                'percentage': edge['perc_to']
            }

    for index, edge in out_edges.iterrows():
        to_id = edge['to']
        if isinstance(to_id, float):
            to_id = int(to_id)
            out_flows[to_id] = {
                'weight': edge['weight'],
                'percentage': edge['perc_from']
            }
        else:
            out_flows[to_id] = {
                'weight': edge['weight'],
                'percentage': edge['perc_from']
            }

    return in_flows, out_flows


def firenzecard_main(conn, output_path, dict_path):
    query = """
    SELECT 
      museum_id,
      latitude,
      longitude,
      short_name,
      museum_name
    FROM optourism.firenze_card_locations
    WHERE museum_id < 43
    ORDER BY museum_id ASC
    """

    cursor = conn.cursor()
    cursor.execute(query)
    records = cursor.fetchall()

    museum_totals_query = """
            SELECT 
              place,
              sum(total_visitors) as visitors,
              museum_id
            FROM optourism.state_national_museum_visits
            WHERE museum_id is not NULL 
            AND (
              visit_month = 'June'
                OR
              visit_month = 'July'
                OR
              visit_month = 'August'
                OR
              visit_month = 'September'
            )
            GROUP BY place, museum_id
            ORDER BY museum_id ASC
            """

    museum_totals = pd.read_sql(museum_totals_query, con=conn)

    network_query = """
    SELECT 
      museum_id,
      entry_time,
      date_trunc('day', entry_time) AS date,
      user_id
    FROM optourism.firenze_card_logs
    """

    network_df = pd.read_sql(network_query, con=conn)
    network_df['total_people'] = 1
    dynamic_edges = na.make_dynamic_firenze_card_edgelist(network_df,
                                                          location='museum_id')

    edges = na.make_static_firenze_card_edgelist(dynamic_edges)
    geojson, location_dict = create_geojson(records, edges, props=museum_totals)

    with open(output_path, 'w') as outfile:
        json.dump(geojson, outfile, indent=2)

    with open(dict_path, 'w') as outfile:
        json.dump(location_dict, outfile, indent=2)


def cdr_main(conn, table_name, output_path, dict_path,
             edges_pickle, density_pickle, end_nodes_path=None,
             start_nodes_path=None):

    query = """
    SELECT 
      id,
      lat,
      lon,
      id as name,
      main_attraction as longName
    FROM optourism.cdr_labeled_towers
    WHERE in_florence_city = TRUE or near_florence_airport = TRUE
    ORDER BY id ASC
    """

    cursor = conn.cursor()
    cursor.execute(query)
    records = cursor.fetchall()

    region_query = """
    SELECT 
      region_name,
      avg(lat),
      avg(lon),
      region_name as name,
      region_name as longName
    FROM optourism.cdr_labeled_towers
    WHERE region_name IS NOT NULL
    GROUP BY region_name
    """

    cursor.execute(region_query)
    region_records = cursor.fetchall()
    all_records = records + region_records

    if os.path.isfile(edges_pickle) and os.path.isfile(density_pickle):
        foreign_edges = pd.read_pickle(edges_pickle)
        foreign_region_density = pd.read_pickle(density_pickle)

        curr_dir = os.path.dirname(os.path.abspath(__file__))
        italian_edges_pickle = os.path.join(curr_dir, 'output',
                                    'italian_daytripper_edges.p')
        italian_density_pickle = os.path.join(curr_dir, 'output',
                                      'italian_daytripper_region_density.p')
        italian_edges = pd.read_pickle(italian_edges_pickle)
        italian_region_density = pd.read_pickle(italian_density_pickle)

        edges = pd.concat([foreign_edges, italian_edges]).groupby(['to', 'from'], as_index=False)[
            'weight'].sum()

        region_density = pd.concat([foreign_region_density, italian_region_density]).groupby(['tower_id'], as_index=False)[
            'density'].sum()
    else:
        edges, region_density = cdr.get_network_edges(conn, table_name,
                                                      end_file_path=end_nodes_path,
                                                      start_file_path=start_nodes_path)
        edges.to_pickle(edges_pickle)
        region_density.to_pickle(density_pickle)

    geojson_path = os.path.join(curr_dir, 'output', 'florence_voronoi_with_area.geojson')
    geojson, location_dict = create_geojson(all_records, edges,
                                            region_density=region_density,
                                            geojson_path=geojson_path)

    with open(output_path, 'w') as outfile:
        json.dump(geojson, outfile, indent=2)

    with open(dict_path, 'w') as outfile:
        json.dump(location_dict, outfile, indent=2)


if __name__ == '__main__':
    conn = dbutils.connect()

    curr_dir = os.path.dirname(os.path.abspath(__file__))
    # output_path = os.path.join(curr_dir, 'output', 'museum_fountain_wsource.json')
    # location_dict_path = os.path.join(curr_dir, 'output', 'museum_dict_wsource.json')
    #
    # firenzecard_main(conn, output_path, location_dict_path)

    cdr_path = os.path.join(curr_dir, 'output', 'cdr_daytripper_fountain.json')
    cdr_dict_path = os.path.join(curr_dir, 'output', 'cdr_daytripper_dict.json')

    edges_pickle = os.path.join(curr_dir, 'output', 'foreign_daytripper_edges.p')
    density_pickle = os.path.join(curr_dir, 'output', 'foreign_daytripper_region_density.p')

    end_node_csv = os.path.join(curr_dir, 'output', 'daytripper_end_nodes.csv')
    start_node_csv = os.path.join(curr_dir, 'output', 'daytripper_start_nodes.csv')

    table_name = 'optourism.foreigners_daytripper_dwell_time'

    cdr_main(conn, table_name, cdr_path, cdr_dict_path, edges_pickle,
             density_pickle, end_nodes_path=end_node_csv,
             start_nodes_path=start_node_csv)