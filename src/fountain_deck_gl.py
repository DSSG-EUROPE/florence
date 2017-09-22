"""
Takes Pandas formatted data and creates JSON data files formatted to be consumed
by the fountain visualization made with Deck.GL
"""

from utils.database import dbutils
from features import network_analysis as na
from output import cdr_fountain as cdr
import json
import os
import pandas as pd
import math


class FountainType:
    MUSEUM = 1
    CDR = 2


def create_geojson(
        nodes,
        edges,
        to_col_name="to",
        from_col_name="from",
        weight_col_name="weight",
        geometries=None,
        props=None,
        fountain_type=FountainType.CDR
):
    """
    Create a geojson file that is formatted to be consumed by the Deck.GL
    fountain visualization. Makes a dictionary of all of the names and printable
    names of the locations in a separate file.

    Args:
        nodes (list): The list of nodes that will be used for the visualization.
            Each node in the list is a tuple of (id, lat, lon, name, full_name)

        edges (Pandas.DataFrame): The weight for each edge to and from a pair
            of nodes contained in the node list. Should contain a column for to,
            from, and weight of that edge. Optional args for those column names.

        to_col_name (string): Name of the edges DataFrame column for the weight
        from_col_name (string): Name of the edges DataFrame column for from node
        weight_col_name (string): Name of the edges DataFrame column for to node
            Only used for creating geojson from CDR data, not museums
        geometries (dict): polygon geometry and area for each unique region id
        props (dict): Additional properties to include in a geojson Feature
        fountain_type (int): Type of fountain to create feature for

    Returns:
        tuple (dict, dict): the geojson object containing all of the feature
            definitions and the object containing all the location names by id
    """
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

    groupby_names = [to_col_name, from_col_name, weight_col_name]
    group_perc = create_percentage_column(edges, 'perc_to', weight_col_name,
                                          groupby_names)
    groupby_names = [from_col_name, to_col_name, weight_col_name, 'perc_to']
    updated_edges = create_percentage_column(group_perc, 'perc_from',
                                             weight_col_name, groupby_names)

    features = [create_feature(f, updated_edges, location_dict,
                               geometries=geometries,
                               props=props,
                               fountain_type=fountain_type) for f in nodes]

    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }

    return geojson, location_dict


def create_percentage_column(df, perc_col_name, weight_col_name, group_names):
    """
    Takes a dataframe with a weight column and calculates what percentage each
    weight is of the total sum of all of the weights.

    Args:
    df (Pandas.DataFrame): dataframe to add a percentage column to
    perc_col_name (string): name to give to the new percentage column
    weight_col_name (string): name of the column to be used for the percentage
        calculation
    group_names (list): list of the names of the columns on which to groupby

    Returns:
    """
    df[perc_col_name] = df[weight_col_name]
    group_sum = df.groupby(group_names).agg({perc_col_name: 'sum'})

    group_perc = group_sum.groupby(level=0) \
        .apply(lambda x: 100 * x / float(x.sum()))

    return group_perc.reset_index()


def process_geometries_geojson(geometries):
    """
    Args:
        geometries (dict): The loaded geometries json object

    Returns:
        dict: a new object containing the geojson geometries from the original
            object now formatted as a dictionary where the keys are the feature
            id and the value is an object with the geometry and the area.
    """
    geo_dict = {}

    for feature in geometries['features']:
        geo_dict[str(feature['properties']['id'])] = {
            'geometry': feature['geometry'],
            'area': feature['properties']['area']
        }

    return geo_dict


def create_feature(
        datum,
        edges,
        location_dict,
        geometries=None,
        props=None,
        to_col_name="to",
        from_col_name="from",
        weight_col_name="weight",
        fountain_type=FountainType.CDR
):
    """
    Create a feature geojson object for the specified node in the fountain

    Args:
        datum (list): one fountain node with an node_id, latitude, longitude,
            name, and printable name.
        edges (Pandas.DataFrame): The weight for each edge to and from a pair
            of nodes contained in the node list. Should contain a column for to,
            from, and weight of that edge. Optional args for those column names.
        location_dict (dict): dictionary of all of the names and printable names
            for every location by node_id.
        geometries (dict): polygon geometry and area for each unique node_id
        props (dict): Additional properties to include in a geojson Feature
        to_col_name (string): Name of the edges DataFrame column for the weight
        from_col_name (string): Name of the edges DataFrame column for from node
        weight_col_name (string): Name of the edges DataFrame column for to node
            Only used for creating geojson from CDR data, not museums
        fountain_type (int): Type of fountain to create feature for

    Returns (dict): a geojson feature definition object for the supplied datum
    """

    node_id, lat, lon, name, full_name = datum
    lat = float(lat)
    lon = float(lon)
    node_id = str(node_id)

    edges[to_col_name] = edges[to_col_name].apply(
        lambda row: str(int(row)) if isinstance(row, float) else str(row))
    edges[from_col_name] = edges[from_col_name].apply(
        lambda row: str(int(row)) if isinstance(row, float) else str(row))

    edges = edges.loc[(edges[to_col_name] == node_id) | (edges[from_col_name] == node_id)]

    if geometries is not None and node_id in geometries:
        geometry = geometries[node_id]['geometry']
    else:
        geometry = create_geometry(lat, lon)

    start_props = None
    if props is not None and node_id in props:
        start_props = props[node_id]

    if fountain_type is FountainType.MUSEUM:
        total_fc_visits = edges[(edges[to_col_name] == node_id)].sum()
        total_fc_visits = str(int(total_fc_visits[weight_col_name]))
        if start_props is not None:
            start_props['totalFcVisits'] = total_fc_visits
        else:
            start_props = {'totalFcVisits': total_fc_visits}

    feature = {
        'type': 'Feature',
        'geometry': geometry,
        'properties': create_properties(node_id, name, full_name, [lon, lat],
                                        edges, location_dict, props=start_props)
    }

    return feature


def create_geometry(lat, lon):
    """
    Create a geojson Polygon geometry object with a circular Polygon that has
    a centroid at the specified latitude and longitude.

    Args:
        lat (float): the latitude for the center of the circle
        lon (float: the longitude for the center of the circle

    Returns:
        dict: the newly created Polygon geojson object
    """

    geometry = {
        'type': 'Polygon',
        'coordinates': [create_circle(lat, lon)]
    }

    return geometry


def create_square(lat, lon, radius=0.0001):
    """
    Create the a geojson square polygon

    Args:
        lat: the center latitude for the polygon
        lon: the center longitude for the polygon
        radius (int): half of the length of the edge of the square

    Returns:
        list: a list of lat/lon points defining a square polygon
    """
    return [
        [round(lon + radius, 7), round(lat + radius, 7)],
        [round(lon + radius, 7), round(lat - radius, 7)],
        [round(lon - radius, 7), round(lat - radius, 7)],
        [round(lon - radius, 7), round(lat + radius, 7)]
    ]


def create_circle(lat, lon, radius=18, num_points=20):
    """
    Create the approximation or a geojson circle polygon

    Args:
        lat: the center latitude for the polygon
        lon: the center longitude for the polygon
        radius (int): the radius of the circle polygon
        num_points (int): number of discrete sample points to be generated along
            the circle

    Returns:
        list: a list of lat/lon points defining a somewhat circular polygon
    """

    points = []
    for k in range(num_points):
        # compute
        angle = math.pi * 2 * k / num_points
        dx = radius * math.cos(angle)
        dy = radius * math.sin(angle)

        new_lat = lat + (180 / math.pi) * (dy / 6378137)
        new_lon = lon + (180 / math.pi) * (dx / 6378137) / math.cos(
            lat * math.pi / 180)

        points.append([round(new_lon, 7), round(new_lat, 7)])

    return points


def create_properties(
        node_id,
        name,
        full_name,
        centroid,
        edges,
        location_dict,
        props=None
):
    """
    Create the additional properties object for the geojson. This contains
    the id, name, printable name, centroid lat/lon, edges in and out, density
    in the node, area of the node, total visits to the node, and total
    firenze card visits to the node. Some of the properties are null for the non
    applicable value.

    Args:
        node_id (string): the unique id for the node
        name (string): the shorthand name of the node
        full_name: the long version of the name of the node
        centroid (list): the center lat/lon of the node
        edges (Pandas.DataFrame): The weight for each edge to and from a pair
            of nodes contained in the node list. Should contain a column for to,
            from, and weight of that edge.
        location_dict (dict): dictionary of all of the names and printable names
            for every location by id.
        props (dict): the optional starting properties for each unique id node

    Returns:
        dict: the newly created properties object for the geojson feature
    """
    in_flows, out_flows = create_flows(edges, node_id)

    if props is None:
        props = {}

    props.update({
        'name': name,
        'fullName': full_name,
        'id': str(node_id),
        'inFlows': in_flows,
        'outFlows': out_flows,
        'centroid': centroid
    })

    location_dict[str(node_id)] = {
        'name': name,
        'fullName': full_name,
    }

    return props


def create_flows(edges, node_id, to_col_name="to", from_col_name="from",
                 weight_col_name="weight"):
    """
    Create the geojson property object that enumerates the flow volume to and
    from a location for the fountain.

    Args:
        edges (Pandas.DataFrame): The weight for each edge to and from a pair
            of nodes contained in the node list. Should contain a column for to,
            from, and weight of that edge. Optional args for those column names.
        node_id (string): identifier of node for which to map in and out flows
        to_col_name (string): Name of the edges DataFrame column for the weight
        from_col_name (string): Name of the edges DataFrame column for from node
        weight_col_name (string): Name of the edges DataFrame column for to node
            Only used for creating geojson from CDR data, not museums

    Returns:
        tuple (dict, dict): the objects for the flows in and out of the node to
            each other node in the fountain for which there is a directed edge
    """
    in_flows = {}
    out_flows = {}
    in_edges = edges.loc[(edges[to_col_name] == node_id)]
    out_edges = edges.loc[(edges[from_col_name] == node_id)]

    for index, edge in in_edges.iterrows():
        from_id = edge[from_col_name]
        if isinstance(from_id, float):
            from_id = int(from_id)

        in_flows[from_id] = {
            'weight': edge[weight_col_name],
            'percentage': edge['perc_to']
        }

    for index, edge in out_edges.iterrows():
        to_id = edge[to_col_name]
        if isinstance(to_id, float):
            to_id = int(to_id)

        out_flows[to_id] = {
            'weight': edge[weight_col_name],
            'percentage': edge['perc_from']
        }

    return in_flows, out_flows


def format_cdr_properties(
        geometries,
        densities,
        id_col_name="tower_id",
        density_col_name="density"
):
    """
    Converts the format of additional CDR properties from being in a DataFrame
    to being in a dictionary indexed by the tower node id

    Args:
        geometries (dict): object where the keys are the node id and the value
            is an object with the geometry and the area.
        densities (Pandas.DataFrame): DataFrame with column with node id and
            corresponding density of visitors at that node
        id_col_name (string): Name of the densities DataFrame column for node id
        density_col_name (string): Name of the densities DataFrame column for
            density.

    Returns:
        (dict): object with a key for each tower node id and a value that is an
            object with values for area and density of that node
    """

    props = {}
    ids = densities[id_col_name].unique()

    for tower_id in ids:
        area = None
        tower_id = str(int(tower_id))

        if tower_id in geometries:
            area = geometries[tower_id]['area']

        density = None
        densities[id_col_name] = densities[id_col_name].apply(int).apply(str)

        if area is not None and area > 0:
            densities[density_col_name] = densities[density_col_name] / area

        maximum = densities[density_col_name].max()
        densities[density_col_name] = densities[density_col_name] / maximum

        first_match = densities[densities[id_col_name] == tower_id].head(1)
        if not first_match.empty:
            density = first_match[density_col_name].iloc[0]

        props[tower_id] = {'area': area, 'density': density}

    return props


def format_firenzecard_properties(
        museums,
        id_col_name="museum_id",
        visitors_col_name="visitors"
):
    """
    Converts the format of additional museum properties from being in a
    DataFrame to being in a dictionary indexed by the museum node id

    Args:
        museums (Pandas.DataFrame): DataFrame with column with museum id and
            corresponding number of visitors at that museum node
        id_col_name (string): Name of the museums DataFrame column for node id
        visitors_col_name (string): Name of the museums DataFrame column for
            number of visitors.

    Returns:
        (dict): object with a key for each museum node id and a value that is an
            object with value for number of state and national museum visitors,
            aka total visitors, to that museum.
    """

    props = {}
    ids = museums[id_col_name].unique()

    for museum_id in ids:
        museum_id = str(int(museum_id))
        museums[id_col_name] = museums[id_col_name].apply(str)
        first_match = museums[museums[id_col_name] == museum_id].head(1)

        total_visits = None
        if not first_match.empty:
            total_visits = first_match[visitors_col_name].iloc[0]

        props[str(museum_id)] = {'totalVisits': total_visits}

    return props


def firenzecard_main(db_connection, fountain_json_path, dict_path):
    """
    Main function for producing the appropriate JSON files to feed into the
    Firenze card museum fountain visualization made with Deck.GL

    Args:
        db_connection (Psycopg.connection): The database connection
        fountain_json_path (string): file path for the fountain JSON output
        dict_path (string): file path for the node name dictionary JSON output
    """

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

    cursor = db_connection.cursor()
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

    museum_totals = pd.read_sql(museum_totals_query, con=db_connection)
    props = format_firenzecard_properties(museum_totals)

    network_query = """
    SELECT 
      museum_id,
      entry_time,
      date_trunc('day', entry_time) AS date,
      user_id
    FROM optourism.firenze_card_logs
    """

    network_df = pd.read_sql(network_query, con=db_connection)
    network_df['total_people'] = 1
    dynamic_edges = na.make_dynamic_firenze_card_edgelist(network_df,
                                                          location='museum_id')

    edges = na.make_static_firenze_card_edgelist(dynamic_edges)
    geojson, location_dict = create_geojson(records, edges, props=props,
                                            fountain_type=FountainType.MUSEUM)

    with open(fountain_json_path, 'w') as outfile:
        json.dump(geojson, outfile, indent=2)

    with open(dict_path, 'w') as outfile:
        json.dump(location_dict, outfile, indent=2)


def cdr_main(db_connection, table_name, fountain_json_path, dict_path,
             edges_pickle, density_pickle, end_nodes_path=None,
             start_nodes_path=None, geojson_path=None):
    """
    Main function for producing the appropriate JSON files to feed into the
    Telecom CDR fountain visualization made with Deck.GL

    Args:
        db_connection (Psycopg.connection): The database connection
        table_name (string): The name of the table that contains the data from
            which to make the nodes and edges
        fountain_json_path (string): file path for the fountain JSON output
        dict_path (string): file path for the node name dictionary JSON output
        edges_pickle (string): file path for pickle object with edges
        density_pickle (string): file path for pickle object with node densities
        end_nodes_path (string): file path for output csv of most common end
            nodes in ranked order
        start_nodes_path (string): file path for output csv of most common start
            nodes in ranked order
        geojson_path (string): file path for tower voronoi geojson definitions
    """

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

    cursor = db_connection.cursor()
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
        edges = pd.read_pickle(edges_pickle)
        density = pd.read_pickle(density_pickle)

    else:
        edges, density = cdr.get_network_edges(db_connection, table_name,
                                               end_file_path=end_nodes_path,
                                               start_file_path=start_nodes_path)
        edges.to_pickle(edges_pickle)
        density.to_pickle(density_pickle)

    with open(geojson_path) as f:
        voronoi_geometries = process_geometries_geojson(json.load(f))

    props = format_cdr_properties(voronoi_geometries, density)
    geojson, location_dict = create_geojson(all_records, edges,
                                            props=props,
                                            geometries=voronoi_geometries)

    with open(fountain_json_path, 'w') as outfile:
        json.dump(geojson, outfile, indent=2)

    with open(dict_path, 'w') as outfile:
        json.dump(location_dict, outfile, indent=2)


if __name__ == '__main__':
    conn = dbutils.connect()

    curr_dir = os.path.dirname(os.path.abspath(__file__))

    output_path = os.path.join(curr_dir, 'output',
                               'museum_fountain.json')
    location_dict_path = os.path.join(curr_dir, 'output',
                                      'museum_dict.json')
    firenzecard_main(conn, output_path, location_dict_path)

    cdr_path = os.path.join(curr_dir, 'output', 'cdr_daytripper_fountain.json')
    cdr_dict_path = os.path.join(curr_dir, 'output', 'cdr_daytripper_dict.json')
    geojson_path = os.path.join(curr_dir, 'output',
                                'florence_voronoi_with_area.geojson')

    edges_pickle = os.path.join(curr_dir, 'output',
                                'foreign_daytripper_edges.p')
    density_pickle = os.path.join(curr_dir, 'output',
                                  'foreign_daytripper_region_density.p')

    end_node_csv = os.path.join(curr_dir, 'output', 'daytripper_end_nodes.csv')
    start_node_csv = os.path.join(curr_dir, 'output',
                                  'daytripper_start_nodes.csv')

    table_name = 'optourism.foreigners_daytripper_dwell_time'

    cdr_main(conn, table_name, cdr_path, cdr_dict_path, edges_pickle,
             density_pickle, end_nodes_path=end_node_csv,
             start_nodes_path=start_node_csv, geojson_path=geojson_path)
