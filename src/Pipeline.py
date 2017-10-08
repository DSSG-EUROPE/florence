
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
    
    # connect to db get firenzecard_logs data and export to CSV
    firenzedata = get_firenze_data(db_connection, export_to_csv=True)

    # get firenzecard_locations data and export to CSV
    firenzedata_locations = get_firenze_locations(db_connection, export_to_csv=True)

    # extract features from data and export to CSV
    df = extract_features(db_connection, path_firenzedata='../src/output/firenzedata_raw.csv',
                           path_firenzelocations_data='../src/output/firenzedata_locations.csv',
                           export_to_csv=True, export_path='../src/output/')

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
    total_museums_per_card, plot_url2 = plot_museums_visited_per_card(df, plotname1='Number-museums-per-card')
    print('Museums visited per card graph url: ', plot_url2)

    # What are the most popular museums?
    popular_museums, plot_url1 = plot_museum_aggregate_entries(df, plotname='PM')
    print('Most popular museums graph url:', plot_url1)

    # Plot aggregate national museum entries
    national_museum_entries, plot_url3 = plot_national_museum_entries(connection, export_to_csv=True,
                                                                      export_path='../src/output/')
    print('Aggregate National Museum Entries graph url:', plot_url3)

    # How many cards are entering museums with minors? What proportion of all cards is this?
    minors = df[df['is_card_with_minors'] == 1]
    minors = minors.groupby('user_id').size().to_frame()
    print('How many cards are entering museums with minors?', len(minors))

    museum_list = ['Santa Croce', 'Opera del Duomo', 'Uffizi', 'Accademia',
                   'M. Casa Dante', 'M. Palazzo Vecchio', 'M. Galileo', 'M. Bargello',
                   'San Lorenzo', 'M. Archeologico', 'Pitti', 'Cappelle Medicee',
                   'M. Santa Maria Novella', 'M. San Marco', 'Laurenziana',
                   'M. Innocenti', 'Palazzo Strozzi', 'Palazzo Medici',
                   'Torre di Palazzo Vecchio', 'Brancacci', 'M. Opificio',
                   'La Specola', 'Orto Botanico', 'V. Bardini', 'M. Stefano Bardini',
                   'M. Antropologia', 'M. Ebraico', 'M. Marini', 'Casa Buonarroti',
                   'M. Horne', 'M. Ferragamo', 'M. Novecento', 'M. Palazzo Davanzati',
                   'M. Geologia', 'M. Civici Fiesole', 'M. Stibbert', 'M. Mineralogia',
                   'M. Preistoria', 'M. Calcio', 'Primo Conti', 'All Museums']

    # Date timeseries
    df_date, plot_urls = get_museum_entries_per_timedelta_and_plot(df, museum_list, timedelta='date',
                                                                   start_date='2016-06-01',
                                                                   end_date='2016-09-30', plot=False,
                                                                   export_to_csv=False,
                                                                   export_path='../src/output/')

    # Daily Museums entries
    date, date_url = plot_timeseries_button_plot(df_date, timedelta='date', plotname='timeseries')
    print('Daily Museum Timeseries url: ', date_url)

    # Hourly timeseries
    df_hour, plot_urls = get_museum_entries_per_timedelta_and_plot(df, museum_list, timedelta='hour',
                                                                   start_date='2016-06-01',
                                                                   end_date='2016-09-30', plot=False,
                                                                   export_to_csv=False,
                                                                   export_path='../src/output/')
    # Hourly Museums entries
    hour, hour_url = plot_timeseries_button_plot(df_hour, timedelta='hour', plotname='timeseries')
    print('Hourly Museum Timeseries url: ', hour_url)

    # Day of Week timeseries
    df_dow, plot_urls = get_museum_entries_per_timedelta_and_plot(df, museum_list, timedelta='day_of_week',
                                                                  start_date='2016-06-01',
                                                                  end_date='2016-09-30', plot=False,
                                                                  export_to_csv=False,
                                                                  export_path='../src/output/')

    # Day of Week museum entries
    dow, dow_url = plot_timeseries_button_plot(df_dow, timedelta='day_of_week', plotname='timeseries')
    print('Day of the Week Museum Timeseries url: ', dow_url)

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
#     data, geomap_plot_url = plot_geomap_timeseries(df, df2_hour, date_to_plot='2016-07-10',
#                                                    plotname='map',
#                                                    mapbox_access_token='',
#                                                    min_timedelta=7,
#                                                    max_timedelta=23)
#     print('Geomap graph url: ', geomap_plot_url)

    # Which museums have inverse correlationns?
    # todo implement museum size (capacity) as a feature, and taking closure timesinto account in correlations
    lst = list(df.museum_id.unique())
    corr_matrix, high_corr, inverse_corr = get_correlation_matrix(df=df2_hour, lst=lst, corr_method='spearman',
                                                                  timedelta='hour', timedelta_subset=False,
                                                                  timedeltamin=0, timedeltamax=3,
                                                                  below_threshold=-0.7, above_threshold=0.7,
                                                                  export_to_csv=True, export_path='../src/output/')

    print('Inversely correlated Museums IDs: ', inverse_corr)
    print('Highly correlated Museums IDs: ', high_corr)


    # ---------------------------------------
    # Network Analysis (Momin)
    # todo Momin add calls to your network analysis functions so that plots and analyses are generated.
    # ---------------------------------------

    # ---------------------------------------

if __name__ == '__main__':
    main()
