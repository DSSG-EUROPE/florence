from utils.database import dbutils
import json
import requests
import polyline
import cPickle as pickle
import os


def get_routes(location_pairs, routes_path, get_time=False):
    """
    Gets the driving route from Open Street Routing Machine for an array
    of pairs of coordinates. Decodes the returned polyline routes into an
    array or lat/lon tuples. Saves the resulting paths as a pickle.

    Args:
        location_pairs (dictionary): The set of location pairs to query for
        routes_path (string): The file path for the routes pickle
        get_time (bool): whether or not to save the duration for route

    Returns:
        array: The routes between all of the supplied pairs of locations
    """

    # TODO: Change this to being walking directions. Use google maps routing.

    routes = {}
    if os.path.isfile(routes_path):
        routes = pickle.load(open(routes_path, 'rb'))

    for location_pair_key in location_pairs:
        if location_pair_key not in routes:
            location = location_pairs[location_pair_key]
            url = 'http://router.project-osrm.org/route/v1/driving/%s' % \
                  location
            response = requests.get(url)
            route = response.json()['routes'][0]

            if get_time:
                routes[location_pair_key] = {
                    'duration': route['duration'],
                    'distance': route['distance']
                }
            else:
                routes[location_pair_key] = polyline.decode(route['geometry'])

    pickle.dump(routes, open(routes_path, 'wb'))

    return routes


def get_tower_pairs(query):
    """
    Gets the pairs of sequential towers that exist in a set of CDR records.
    Only adds transitions between towers that exist in one users records.

    Args:
        query (string): The POSTGRES query to retrieve the set of CDR records

    Returns:
        array: The routes between all of the pairs of towers
    """

    conn = dbutils.connect()
    cursor = conn.cursor()

    cursor.execute(query)
    records = cursor.fetchall()

    prev_user = None
    prev_tower = None
    prev_lat = None
    prev_lon = None
    tower_pairs = {}

    for index in range(len(records)):
        user, lon, lat, hour, minute, tower = records[index]

        if prev_user == user and prev_tower is not None and prev_tower != tower:
            key = '{0},{1};{2},{3}'.format(prev_lon, prev_lat, lon, lat)
            tower_pairs[key] = key

        prev_user = user
        prev_tower = tower
        prev_lon = lon
        prev_lat = lat

    return get_routes(tower_pairs)


def museum_main(routes_path):
    """
    Calculates routes between every pair of museums that are visited in a row

    Args:
        routes_path (string): path for output museum routes pickle
    """

    # TODO: Finish this so that it creates paths. Need to complete walking
    # directions implementation for routes first

    conn = dbutils.connect()
    cursor = conn.cursor()

    museum_location_query = """
        SELECT latitude, longitude, string 
        FROM optourism.firenze_card_locations;
    """

    cursor.execute(museum_location_query)
    records = cursor.fetchall()

    museum_pairs = {}

    for start_museum in records:
        start_lat, start_lon, start_code = start_museum
        for end_museum in records:
            end_lat, end_lon, end_code = end_museum
            key = '{0}{1}'.format(start_code, end_code)
            reverse_key = '{1}{0}'.format(start_code, end_code)

            if end_code == start_code or reverse_key in museum_pairs:
                continue

            location = '{0},{1};{2},{3}'.format(start_lon, start_lat, end_lon,
                                                end_lat)
            museum_pairs[key] = location

    return get_routes(museum_pairs, routes_path, get_time=True)


def cdr_main(routes_path, output_path):
    """
    Retrieves a set of CDR records for users with notable paths and
    interpolates these paths with routes between their tower locations
    equally spaced over the time gap.
    Creates a JSON data file to feed into the deck.gl paths visualization.

    Args:
        routes_path (string): The file path for the routes pickle
        output_path (string): The file path for the output json
    """

    conn = dbutils.connect()
    cursor = conn.cursor()

    routes_query = """
        SELECT 
          paths.cust_id, 
          paths.lon, 
          paths.lat, 
          date_part('hour', paths.date_time_m) AS hour, 
          date_part('minute', paths.date_time_m) AS minute,
          paths.tower_id
        FROM optourism.foreigners_path_records_joined AS paths
          JOIN optourism.foreigners_features AS features
          ON features.cust_id = paths.cust_id
            AND (
              date_part('day', paths.date_time_m) = 27 
                OR 
              date_part('day', paths.date_time_m) = 28
            )
            AND date_part('month', paths.date_time_m) = 7
            AND features.days_active < 15
        ORDER BY cust_id ASC, hour ASC, minute ASC; 
    """

    cursor.execute(routes_query)
    records = cursor.fetchall()
    clean_records = []

    data = None
    prev_user = None
    prev_time = None
    prev_tower = None
    prev_lat = None
    prev_lon = None
    id_counter = 0

    routes = pickle.load(open(routes_path, 'rb'))

    for index in range(len(records)):
        user, lon, lat, hour, minute, tower = records[index]
        timestamp = hour * 60 + minute

        if prev_user is not None and prev_user != user:
            data['endTime'] = prev_time
            clean_records.append(data)

        if prev_user is None or prev_user != user:
            data = {
                'color': id_counter,
                'startTime': timestamp,
                'segments': []
            }

            id_counter += 1
        elif prev_tower is not None and prev_tower != tower:
            key = '{0},{1};{2},{3}'.format(prev_lon, prev_lat, lon, lat)

            if key in routes:

                route = routes[key]
                delta = (timestamp - prev_time) / (len(route) + 1)

                for i in range(len(route)):
                    stop_lat, stop_lon = route[i]
                    segment = [stop_lon, stop_lat, prev_time + delta * (i + 1)]
                    data['segments'].append(segment)

        data['segments'].append([lon, lat, timestamp])

        prev_user = user
        prev_time = timestamp
        prev_tower = tower
        prev_lat = lat
        prev_lon = lon

    with open(output_path, 'w') as outfile:
        json.dump(clean_records, outfile)


if __name__ == '__main__':
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    pickle_path = os.path.join(curr_dir, 'output', 'tower_routes.p')
    cdr_output_path = os.path.join(curr_dir, 'output', 'tower_routes.json')

    cdr_main(pickle_path, cdr_output_path)

    museum_pickle_path = os.path.join(curr_dir, 'output', 'museum_routes.p')
    museum_main(museum_pickle_path)
