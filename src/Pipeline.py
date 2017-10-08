
import yaml
from features.firenzecard import *
from utils.database import dbutils

def main():

    """
    This runs the main pipeline for all of the Optourism project.
    After running, there will be plots and csv exported to the output directory
    """

    # Connect to Optourism DB
    db_connection = dbutils.connect()

    # ---------------------------------------
    # CDR (Cristina)
    # todo Cristina add calls to your CDR functions so that CDR plots and analyses are generated.
    # ---------------------------------------

    cdr.filter_data(db_connection)
    cdr.extract_features(db_connection)
    cdr.analyze_movement(db_connection)

    # Create Voronoi heat maps per hour

    # ---------------------------------------
    # Firenze card Analysis (io)
    # ---------------------------------------

    # todo import yaml with plotly and mapbox cdredentials

    with open("firenzecard_params.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

    # connect to db get firenzecard_logs data and export to CSV
    get_firenze_data(db_connection, cfg.export_to_csv)

    # get firenzecard_locations data and export to CSV
    get_firenze_locations(db_connection, cfg.export_to_csv)

    # extract features from data and export to CSV
    df = extract_features(db_connection, cfg.path_firenzedata, cfg.path_firenzelocations_data,
                           cfg.export_to_csv, cfg.export_path)

    # How many cards are there?
    print('How many Firenzecards are there?', len(df['user_id'].unique()))

    # How many cards were activated?
    print('How many cards were activated?', df[(df['adults_first_use'] == 1)])

    # What is the most common day of activation?
    day_of_activation, plot_url_activation = plot_day_of_activation(df, plotname='DOA')
    print('What is the most common day of activation?', plot_url_activation)

    # How many users use the card for 24h or less? (not cumulative calculation)
    print('How many users use the card for 24h or less?',
          len(df[df['total_duration_card_use'] <= 24].user_id.unique()))

    # ... 24 - 48h?
    print('How many users use the card for 24h - 48h?',
          len(df[(df['total_duration_card_use'] > 24) & (df['total_duration_card_use'] <= 48)].user_id.unique()))

    # ... 48 - 72h?
    print('How many users use the card for 48 - 72h?',
          len(df[(df['total_duration_card_use'] > 48) & (df['total_duration_card_use'] <= 72)].user_id.unique()))

    # How many museums visited per card
    total_museums_per_card, plot_url2 = plot_museums_visited_per_card(df, plotname='Number-museums-per-card')
    print('Museums visited per card graph url: ', plot_url2)

    # What are the most popular museums?
    popular_museums, plot_url1 = plot_museum_aggregate_entries(df, plotname='PM')
    print('Most popular museums graph url:', plot_url1)

    # Plot aggregate national museum entries
    national_museum_entries, plot_url3 = plot_national_museum_entries(db_connection, cfg.export_to_csv,
                                                                      cfg.export_path)
    print('Aggregate National Museum Entries graph url:', plot_url3)

    # How many cards are entering museums with minors? What proportion of all cards is this?
    minors = df[df['is_card_with_minors'] == 1]
    minors = minors.groupby('user_id').size().to_frame()
    print('How many cards are entering museums with minors?', len(minors))

    # Date timeseries
    df_date, plot_urls = get_museum_entries_per_timedelta_and_plot(df, cfg.me_names, cfg.me_time,
                                                                   cfg.start_date,cfg.end_date,
                                                                   cfg.export_to_csv, cfg.export_path, plot=False)

    # todo: fix plotting function
    # Daily Museums entries
    # date, date_url = plot_timeseries_button_plot(df_date, cfg.date_time, plotname)
    # print('Daily Museum Timeseries url: ', date_url)

    # Hourly timeseries
    df_hour, plot_urls = get_museum_entries_per_timedelta_and_plot(df, cfg.me_names, cfg.hour_time,
                                                                   cfg.start_date,cfg.end_date,
                                                                   cfg.export_to_csv, cfg.export_path, plot=False)
    # todo: fix plotting function
    #  Hourly Museums entries
    # hour, hour_url = plot_timeseries_button_plot(df_hour, cfg.hour_time, plotname)
    # print('Hourly Museum Timeseries url: ', hour_url)

    # Day of Week timeseries
    df_dow, plot_urls = get_museum_entries_per_timedelta_and_plot(df, cfg.me_names, cfg.dow_time,
                                                                  cfg.start_date,cfg.end_date,
                                                                  cfg.export_to_csv,cfg.export_path, plot=False)

    # todo: fix plotting function
    # Day of Week museum entries
    # dow, dow_url = plot_timeseries_button_plot(df_dow, cfg.dow_time, plotname)
    # print('Day of the Week Museum Timeseries url: ', dow_url)

    # Timelines of usage / how many users on average in time per timedelta
    df2_date = df_date['All Museums']
    df2_dow = df_dow['All Museums']
    df2_hour = df_hour['All Museums']
    mean_entries_hour, mean_entries_dow, mean_entries_date = get_timelines_of_usage(df2_hour, df2_date, df2_dow)

    print('How many users are there per day on average across all museums, over the entire summer?',
          mean_entries_hour)
    print('How many users are there per hour on average across all museums, over the entire summer?',
          mean_entries_dow)
    print('How many users are there per daytype on average across all museums, over the entire summer?',
          mean_entries_date)

    # Which museums are full, and which are rather empty, at different times of the day?
    # Are they located next to each other?
#     data, geomap_plot_url = plot_geomap_timeseries(df, df2_hour, date_to_plot, plotname,
#                                                    mapbox_access_token=cfg.mapbox_token,
#                                                    min_timedelta, max_timedelta)
#     print('Geomap graph url: ', geomap_plot_url)

    # Which museums have inverse correlationns?
    # todo implement museum size (capacity) as a feature, and taking closure timesinto account in correlations
    lst = list(df.museum_id.unique())
    corr_matrix, high_corr, inverse_corr = get_correlation_matrix(df2_hour, lst, cfg.corr_method,
                                                                  cfg.hour_timedelta, cfg.hourdelta_subset,
                                                                  cfg.hourdeltamin, cfg.hourdeltamax,
                                                                  cfg.below_threshold, cfg.above_threshold,
                                                                  cfg.export_to_csv, cfg.export_path)

    print('Inversely correlated Museums IDs: ', inverse_corr)
    print('Highly correlated Museums IDs: ', high_corr)


    # ---------------------------------------
    # Network Analysis (Momin)
    # todo Momin add calls to your network analysis functions so that plots and analyses are generated.
    # ---------------------------------------

    # ---------------------------------------

if __name__ == '__main__':
    main()
