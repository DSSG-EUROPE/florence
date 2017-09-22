import pandas as pd
import matplotlib.pyplot as plt
import trip_segmenter as ts


def get_airport_arrivals(db_connection, csv_path=''):
    """
    Gets airport arrival data from the database and optionally saves this data
    to CSV

    Args:
        db_connection (Psycopg.connection): The database connection
        csv_path (string): file path for where to save CSV data to

    Returns:
        Pandas.DataFrame: the DataFrame containing the number of passengers
            arriving per day at the Florence airport.
    """

    arrivals_data = pd.read_sql("""
        SELECT "day", SUM(total_passengers) AS passengers
        FROM optourism.florence_airport_arrivals GROUP BY "day"
        """, con=db_connection)

    if csv_path:
        arrivals_data.to_csv(csv_path)

    return arrivals_data


def get_near_airport(features, csv_path=''):
    """
    Filter trips data to being just trips whose first call originates from a
    tower near the airport.

    Args:
        features (Pandas.DataFrame): a set of user trips with features for
            trip number and when the call was placed in the timeline of the trip
        csv_path (string): file path for where to save CSV data to

    Returns:
        Pandas.DataFrame: The filtered subset of trip features for just trips
            whose first call is in the airport.
    """
    at_airport_data = features.loc[features['trip'].isin(['first', 'trip']) &
                                   features['calls_near_airport'] > 0]

    data = at_airport_data.groupby('date_').nunique('cust_id')

    if csv_path:
        data.to_csv(csv_path)

    return data


def get_italians_near_airport(db_connection, csv_path=''):
    """
    Filter Italian visitor trips data to being just trips that have a first call
    from a tower near the airport.

    Args:
        db_connection (Psycopg.connection): The database connection
        csv_path (string): file path for where to save CSV data to

    Returns:
        Pandas.DataFrame: The filtered subset of Italian trip features for just
        trips whose first call is in the airport.
    """

    features = ts.get_italian_trips(db_connection, only_start=True)
    return get_near_airport(features, csv_path)


def get_foreigners_near_airport(db_connection, csv_path=''):
    """
    Filter foreign visitor trips data to being just trips that have a first call
    from a tower near the airport.

    Args:
        db_connection (Psycopg.connection): The database connection
        csv_path (string): file path for where to save CSV data to

    Returns:
        Pandas.DataFrame: The filtered subset of foreign trip features for just
        trips whose first call is in the airport.
    """

    features = ts.get_foreign_trips(db_connection, only_start=True)
    return get_near_airport(features, csv_path)


def get_tourist_center_visits(db_connection, csv_path=''):
    """
    Get the logs for visits to the airport tourist information center by day.

    Args:
        db_connection (Psycopg.connection): The database connection
        csv_path (string): file path for where to save CSV data to

    Returns:
        Pandas.DataFrame: The data for number of visitors per day to the airport
            tourist information center.
    """

    visits = pd.read_sql("""
        SELECT * FROM optourism.info_center_ae_daily
        """, con=db_connection)

    columns = list(visits)
    columns.remove('visit_date')
    visits['total_visitors'] = visits[columns].sum(axis=1)

    if csv_path:
        visits.to_csv(csv_path)

    return visits


def plot_airport_arrivals_per_day(**kwargs):
    """
    Plots the line for airport arrivals per day.
    """

    arrivals_data = get_airport_arrivals()
    arrivals_data.plot.line(x='day', y='passengers', **kwargs)


def plot_italians_near_airport_per_day(**kwargs):
    """
    Plots the line for Italian visitors near the airport per day.
    """

    italians_data = get_italians_near_airport()
    italians_data['cust_id'] = italians_data['cust_id']
    italians_data.plot.line(y='cust_id', **kwargs)


def plot_foreigners_near_airport_per_day(**kwargs):
    """
    Plots the line for Foreign visitors near the airport per day.
    """

    foreigners_data = get_foreigners_near_airport()
    foreigners_data['cust_id'] = foreigners_data['cust_id']
    foreigners_data.plot.line(y='cust_id', **kwargs)


def plot_cdr_near_airport_per_day(**kwargs):
    """
    Plots the line for all visitors near the airport per day.
    """

    foreigners_data = get_foreigners_near_airport()
    italians_data = get_italians_near_airport()
    total_data = foreigners_data.add(italians_data, fill_value=0)

    total_data['cust_id'] = total_data['cust_id'] * 11
    print(total_data.head())
    total_data.plot.line(y='cust_id', **kwargs)


def plot_tourist_center_visits_per_day(**kwargs):
    """
    Plots the line for visits to the airport tourist information center per day.
    """

    visits_data = get_tourist_center_visits()
    visits_data.plot.line(x='visit_date', y='total_visitors', **kwargs)


def get_normalized_data(data, column_name):
    """
    Minimax normalize the data in a DataFrame column.

    Args:
        data (Pandas.DataFrame): The DataFrame with the column to normalize
        column_name (string): The name of the column to normalize

    Returns:
        Pandas.DataFrame: The DataFrame with a column added for the normalize
            column data.
    """

    min = data[column_name].min()
    max = data[column_name].max()
    data['%s_norm' % column_name] = ((data[column_name] - min) / (max - min))

    return data


if __name__ == '__main__':
    fig = plt.figure(figsize=(10, 8), dpi=300)
    ax = plt.gca()

    plot_airport_arrivals_per_day(ax=ax, color='black', style='-')
    plot_italians_near_airport_per_day(ax=ax, color='yellow', style='.-')
    plot_foreigners_near_airport_per_day(ax=ax, color='blue', style='-')
    plot_cdr_near_airport_per_day(ax=ax, color='purple', style='-')
    plot_tourist_center_visits_per_day(ax=ax, color='red', style='.-')

    fig.savefig('output/airport.png')
    plt.clf()
    plt.close()