
def livorno_analysis(df):

    #### TO DO: make this into a function. Clean up code so when it is called as a function, it returns key descriptive stats and simple basic graphs

    June = livorno_data[livorno_data.Month == 'Giu']
    July = livorno_data[livorno_data.Month == 'Lug']
    August = livorno_data[livorno_data.Month == 'Ago']
    September = livorno_data[livorno_data.Month == 'Set']

    ## TO DO: GROUPBY DAY AND SUM COUNT OF PASSENGERS ON A GIVEN DAY
    june_pass_ts = pd.DataFrame(June.groupby(['Arrival_Date']).sum()['PassTrans'])
    june_pass_ts['date'] = june_pass_ts.index

    july_pass_ts = pd.DataFrame(July.groupby(['Arrival_Date']).sum()['PassTrans'])
    july_pass_ts['date'] = july_pass_ts.index

    august_pass_ts = pd.DataFrame(August.groupby(['Arrival_Date']).sum()['PassTrans'])
    august_pass_ts['date'] = august_pass_ts.index

    sept_pass_ts = pd.DataFrame(September.groupby(['Arrival_Date']).sum()['PassTrans'])
    sept_pass_ts['date'] = sept_pass_ts.index

    # How many people arriving in June, July, August, September?
    print(june_pass_ts['PassTrans'].sum())
    print(july_pass_ts['PassTrans'].sum())
    print(august_pass_ts['PassTrans'].sum())
    print(sept_pass_ts['PassTrans'].sum())
    print(livorno_data['PassTrans'].sum())


    # How many ships arriving per day, on average?
    daily_ships = pd.DataFrame(livorno_data.groupby(['Arrival_Date']).count()['Ship'])
    daily_ships.Ship.mean()

    # How many ships total
    livorno_data.Ship.count()

    # Avg passengers per day arriving in Livorno
    pass_ts = pd.DataFrame(livorno_data.groupby(['ArrivalTime']).sum()['PassTrans'])
    pass_ts['time'] = pass_ts.index

    livorno_data.PassTrans.mean()

    # How many total passengers over summer?
    livorno_data.PassTrans.sum()

    #### Total days & hours in port
    departtimes = pd.to_datetime(livorno_data['DepartureTime'], format="%H:%M:%S")
    arrivaltimes = pd.to_datetime(livorno_data['ArrivalTime'], format="%H:%M:%S")
    livorno_data['hours_in_port'] = departtimes - arrivaltimes

    departdays = pd.to_datetime(livorno_data['Departure_Date'])
    arrivaldays = pd.to_datetime(livorno_data['Arrival_Date'])
    livorno_data['days_in_port'] = departdays - arrivaldays

    grouped_by_arrivaltime = livorno_data.groupby(['ArrivalTime']).sum()
    grouped_by_departuretime = livorno_data.groupby(['DepartureTime']).sum()
    grouped_by_arrivaltime
    ## we see that Most boats arrive morning, leave in late evening

    # How many passengers on ships that stay 2 days?
    two_day_ships = livorno_data[livorno_data['days_in_port'] == '2 days']
    two_day_ships['PassTrans'].sum()

    ### How many overnight boats? 8
    overnight_boats = livorno_data[(livorno_data['PassOver']).notnull()]
    not_overnight_boats = livorno_data[(livorno_data['PassOver']).isnull()]

    # How many people total on these overnight boats? 3990
    overnight_boats.PassTrans.sum()

    # On overnight boats, do passengers sleep on the boats? YES!
    sleep_on_ship = overnight_boats.ix[:, ['PassOver','PassTrans']]
    sleep_on_ship


    mean_time = not_overnight_boats['hours_in_port'].mean()
    max_time = not_overnight_boats['hours_in_port'].max()

    print(mean_time)
    print(max_time)

    ### Who are the main shipowners?
    livorno_data['Ship'].value_counts()

    return
