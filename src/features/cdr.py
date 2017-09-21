import pandas as pd


def filter_data(db_connection):
    """
    Input:
        db_connection - The database connection
        CDR foreigners preprocessed table
        optourism.iotest_cdr_foreigners_preprocessed

    Outputs:
        1) optourism.iotest_foreigners_preprocessed table
           (preprocessed CDR foreigners) with filtered:
            -- only CDR customers who have been in Florence city
            -- only CDR customers whose max number daily calls > 5

    """
    # TODO: check all filters and add missing ones
    # TODO: extract only features which will be used

    query = open("sql/cdr_filters.sql", "r").read()
    db_connection.cursor().execute(query)
    db_connection.commit()


def extract_features(db_connection):
    """
    Input:
        db_connection - The database connection
        CDR foreigners db table: optourism.cdr_foreigners

    Outputs:
        1) optourism.iotest_cdr_foreigners
           (copy of cdr_foreigners, for testing purposes)
        2) materialized view optourism.iotest_foreigners_daily_timeseries
        3) optourism.iotest_foreigners_call_count table
        4) optourism.iotest_foreigners_preprocessed table
           (preprocessed CDR foreigners) with added:
            -- in_florence_city variable
            -- days_active variable

    """
    # TODO: add is_bot feature to cdr main table
    # TODO: extract only features which will be used

    query = open("sql/cdr_extract_features.sql", "r").read()
    db_connection.cursor().execute(query)
    db_connection.commit()


def analyze_movements(db_connection):
    """
    CDR movement analysis

    Key numbers, distributions, and time series to describe tourist population
    Number of tourists per nationality per day in Florence
    Breakdown of tourists per hour and per tower area
    Length of stay
    Number of trips
    Flows between Florence and rest of Tuscany and Italy
    Flows within Florence

    """
    # TODO: All of this

    pass


def get_towers_in_florence(db_connection):
    """
    Gets the lat/lon of all of the telecom towers in Florence city

    Args:
        db_connection (Psycopg.connection): The database connection
        as_geo (bool): Whether or not to return a Geopandas DataFrame

    Returns:
        Pandas.DataFrame: The locations of all of the towers that are within
            Florence city
    """

    towers_data = pd.read_sql("""
        SELECT DISTINCT lat, lon
        FROM optourism.cdr_labeled_towers
        WHERE in_florence_city = TRUE
        """, con=db_connection)

    return towers_data
