import pandas as pd
import logging as log
from ..utils.database import dbutils


def get_daily_call_counts(db_connection, timeseries_table):
    """
    Gets the time series data per customer from the database. This data
    contains every unique customer ID from the time series set along with
    the every unique call date for each customer with the associated number
    of calls made or received.

    Args:
        db_connection (Psycopg.connection): The database connection
        timeseries_table (string): The name of the database table that contains
                                   the time series data

    Returns:
        Pandas.DataFrame: The time series data for each unique user. It has the
                          columns cust_id, date, date_diff, calls,
                          calls_in_florence, calls_near_airport
    """

    log.info('Start reading from DB')

    query = """
        SELECT cust_id, 
        (cust_id - LAG(cust_id) OVER ())=0 AS same_cust, 
        date_ AS date, 
        EXTRACT(DAYS FROM date_ - LAG(date_) OVER ()) - 1 AS date_diff, 
        calls, 
        calls_in_florence_city AS calls_in_florence,
        calls_near_airport
        FROM %s
    """ % timeseries_table

    log.info('Finished reading from DB')

    return pd.read_sql(query, con=db_connection)


# TODO: cleanup or snip
def get_active_counts(counts):
    counts_agg = counts.groupby('cust_id')['date'].count().reset_index(name='days_active')
    counts['days_active'] = counts_agg['days_active']
    print(counts['days_active'].unique())
    print(counts['calls'].nun)
    counts_subset = counts[(counts['days_active'] > 1) | (counts['calls'] > 4)]

    return counts_subset


def get_italian_trips(db_connection):
    """
    Gets the time series data for all Italian visitors from the database

    Args:
        db_connection (Psycopg.connection): The database connection

    Returns:
        Pandas.DataFrame: The time series data for each unique Italian visitor.
                          It has the columns cust_id, date, date_diff, calls,
                          calls_in_florence, calls_near_airport
    """
    counts = get_daily_call_counts(db_connection,
                                   'optourism.italians_timeseries_daily')

    return get_trips(counts)


def get_foreign_trips(db_connection):
    """
    Gets the time series data for all Foreign visitors from the database

    Args:
        db_connection (Psycopg.connection): The database connection

    Returns:
        Pandas.DataFrame: The time series data for each unique Foreign visitor.
                          It has the columns cust_id, date, date_diff, calls,
                          calls_in_florence, calls_near_airport
    """
    counts = get_daily_call_counts(db_connection,
                                   'optourism.foreigners_timeseries_daily')

    return get_trips(counts)


def frequency(dataframe, column_name):
    """
    Gets the frequency of each unique value in a specified column.

    Args:
        dataframe (Pandas.DataFrame): The data that contains the column for the
                                      the frequency calculation
        column_name (string): Name of the column to calculate the frequency for

    Returns:
        Pandas.DataFrame: A new dataframe that has each unique value from the
                          specified column along with the percentage frequency,
                          the cumulative percentage, and the ccdf
    """

    out = dataframe[column_name].value_counts().to_frame()

    out.columns = ['frequency']
    out.index.name = column_name
    out.reset_index(inplace=True)
    out = out.sort_values(column_name)

    out['percentage'] = out['frequency'] / out['frequency'].sum()
    out['cumulative'] = out['frequency'].cumsum() / out['frequency'].sum()
    out['ccdf'] = 1 - out['cumulative']

    return out


def get_trips(counts, only_start=False, gap_length=3):
    counts.iloc[0, 1] = False

    same_cust_false = counts['same_cust'] == False
    same_cust_true = ~same_cust_false

    counts.loc[same_cust_false, 'date_diff'] = None
    gap_threshold = counts['date_diff'] < gap_length

    counts['in_florence'] = (counts['calls_in_florence'] > 0) | \
                            (counts['calls_near_airport'] > 0)

    in_florence_true = counts['in_florence'] == True

    counts['calls_out_florence'] = counts['calls'] - counts['calls_in_florence']
    counts['out_florence'] = counts['calls_out_florence'] > 0

    counts['was_in_florence'] = counts['in_florence'].shift(1)
    counts['willbe_in_florence'] = counts['in_florence'].shift(-1)
    counts.loc[same_cust_false, 'was_in_florence'] = None

    was_in_florence_true = counts['was_in_florence'] == True
    was_in_florence_false = ~was_in_florence_true
    willbe_in_florence_true = counts['willbe_in_florence'] == True
    willbe_in_florence_false = ~willbe_in_florence_true

    counts['was_out_florence'] = counts['out_florence'].shift(1)
    counts['willbe_out_florence'] = counts['out_florence'].shift(-1)
    counts.loc[same_cust_false, 'was_out_florence'] = None

    counts['trip'] = ''

    # Do less specific first
    counts.loc[
        same_cust_false &
        in_florence_true,
        'trip'
    ] = 'first'

    if not only_start:
        counts.loc[
            same_cust_true &
            (counts['same_cust'].shift(-1) == False) &
            in_florence_true,
            'trip'
        ] = 'last'

    # And more specific next
    counts.loc[
        same_cust_true &
        gap_threshold &
        was_in_florence_true &
        in_florence_true,
        'trip'
    ] = 'continue'

    if not only_start:
        counts.loc[
            same_cust_true &
            gap_threshold &
            was_in_florence_true &
            in_florence_true &
            willbe_in_florence_false,
            'trip'
        ] = 'end'

    counts.loc[
        same_cust_true &
        gap_threshold &
        was_in_florence_false &
        in_florence_true,
        'trip'
    ] = 'start'

    counts['on_trip'] = counts['trip'] != ''

    trips = counts[['cust_id', 'same_cust', 'date', 'date_diff',
                    'calls_in_florence', 'calls_out_florence', 'trip',
                    'on_trip']]

    num = ((trips['on_trip'].shift(1) != trips['on_trip']).astype(int).cumsum())
    trips['trip_id'] = num * (trips['on_trip']).astype(int)

    trips_group = trips[trips['trip_id'] != 0][['cust_id', 'trip_id']]
    trips_group = trips_group.groupby(['cust_id', 'trip_id']).size().to_frame()

    return counts, trips_group


def get_length_gaps_between_trips(grouped_counts):
    """
    Gets the frequency of length of gaps between trips for a customer

    Args:
        grouped_counts (Pandas.DataFrame): The grouped dataframe returned from
                                           a get_trips method call

    Returns:
        Pandas.DataFrame: the dataframe containing the frequencies for each
                          gap (in days) between trips
    """
    return frequency(grouped_counts[grouped_counts['date_diff'] > 0],
                     'date_diff')


def get_trip_length(grouped_counts):
    """
    Gets the frequency of the length of a trip for a customer

    Args:
        grouped_counts (Pandas.DataFrame): The grouped dataframe returned from
                                           a get_trips method call

    Returns:
        Pandas.DataFrame: the dataframe containing the frequencies for each
                          trip length (in days)
    """
    return frequency(grouped_counts, 0)


def get_number_trips(grouped_counts):
    """
    Gets the frequency of number of trips the customers make

    Args:
        grouped_counts (Pandas.DataFrame): The grouped dataframe returned from
                                           a get_trips method call

    Returns:
        Pandas.DataFrame: the dataframe containing the frequencies for each
                          number of trips
    """
    return frequency(grouped_counts.groupby('cust_id').count(), 0)


def get_trip_length_for_onetime_visitors(grouped_counts):
    """
    Gets the frequency of length of gaps between trips for a customer

    Args:
        grouped_counts (Pandas.DataFrame): The grouped dataframe returned from
                                           a get_trips method call

    Returns:
        Pandas.DataFrame: the dataframe containing the frequencies for each
                          gap (in days) between trips
    """
    df = grouped_counts[grouped_counts.groupby('cust_id').count() == 1]
    return frequency(df, 0)


def main():
    connection = dbutils.connect()

    italian_trips, italian_grouped = get_italian_trips(connection)
    foreign_trips, foreign_grouped = get_foreign_trips(connection)

    italian_lengths = get_trip_length_for_onetime_visitors(italian_grouped)
    foreign_lengths = get_trip_length_for_onetime_visitors(foreign_grouped)

    # TODO: check that new line works in this print statement
    print('----- Length of stay for Italian visitors ----- \n')
    print(italian_lengths.head(10))

    print('----- Length of stay for Foreign visitors -----')
    print(foreign_lengths.head(10))

if __name__ == '__main__':
    main()
