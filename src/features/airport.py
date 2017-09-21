import pandas as pd
import matplotlib.pyplot as plt
import trip_segmenter as ts


def get_airport_arrivals(db_connection, csv_path=''):
    arrivals_data = pd.read_sql("""
        SELECT "day", SUM(total_passengers) AS passengers
        FROM optourism.florence_airport_arrivals GROUP BY "day"
        """, con=db_connection)

    if csv_path:
        arrivals_data.to_csv(csv_path)

    return arrivals_data


def get_near_airport(features, csv_path=''):
    at_airport_data = features.loc[features['trip'].isin(['first', 'trip']) &
                                   features['calls_near_airport'] > 0]

    data = at_airport_data.groupby('date_').nunique('cust_id')

    if csv_path:
        data.to_csv(csv_path)

    return data


def get_italians_near_airport(db_connection, csv_path=''):
    features = ts.get_italian_trips(db_connection, only_start=True)
    return get_near_airport(features, csv_path)


def get_foreigners_near_airport(db_connection, csv_path=''):
    features = ts.get_foreign_trips(db_connection, only_start=True)
    return get_near_airport(features, csv_path)


def get_tourist_center_visits(db_connection, csv_path=''):
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
    arrivals_data = get_airport_arrivals()
    arrivals_data.plot.line(x='day', y='passengers', **kwargs)


def plot_italians_near_airport_per_day(**kwargs):
    italians_data = get_italians_near_airport()
    italians_data['cust_id'] = italians_data['cust_id']
    italians_data.plot.line(y='cust_id', **kwargs)


def plot_foreigners_near_airport_per_day(**kwargs):
    foreigners_data = get_foreigners_near_airport()
    foreigners_data['cust_id'] = foreigners_data['cust_id']
    foreigners_data.plot.line(y='cust_id', **kwargs)


def plot_cdr_near_airport_per_day(**kwargs):
    foreigners_data = get_foreigners_near_airport()
    italians_data = get_italians_near_airport()
    total_data = foreigners_data.add(italians_data, fill_value=0)

    total_data['cust_id'] = total_data['cust_id'] * 11
    print(total_data.head())
    total_data.plot.line(y='cust_id', **kwargs)


def plot_tourist_center_visits_per_day(**kwargs):
    visits_data = get_tourist_center_visits()
    visits_data.plot.line(x='visit_date', y='total_visitors', **kwargs)


def get_normalized_data(data, column_name):
    min = data[column_name].min()
    max = data[column_name].max()
    data['%s_norm' % column_name] = ((data[column_name] - min) / (max - min))
    print(data.head())
    return data


if __name__ == '__main__':
    fig = plt.figure(figsize=(10, 8), dpi=300)
    ax = plt.gca()

    plot_airport_arrivals_per_day(ax=ax, color='black', style='-')
    # plot_italians_near_airport_per_day(ax=ax, color='yellow', style='.-')
    # plot_foreigners_near_airport_per_day(ax=ax, color='blue', style='-')
    # plot_cdr_near_airport_per_day(ax=ax, color='purple', style='-')
    # plot_tourist_center_visits_per_day(ax=ax, color='red', style='.-')

    fig.savefig('output/airport.png')
    plt.clf()
    plt.close()