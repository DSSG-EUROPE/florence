import pandas as pd
import matplotlib.ticker as ticker
from pylab import *
import igraph as ig
import matplotlib.pyplot as plt


def prepare_firenzedata(records, nodes):
    """
    Alter type and format of some columns from firenze card log database results

    Args:
        records (Pandas.DataFrame): records from the firenze card logs SQL query
        nodes:

    Returns:
        Pandas.DataFrame: records DataFrame augmented with columns for
        museum short name, museum single-character code, entry date only, and
        entry date + hour only
    """

    records['short_name'] = records['museum_id']\
        .replace(dict(zip(nodes['museum_id'], nodes['short_name'])))

    records['string'] = records['museum_id']\
        .replace(dict(zip(nodes['museum_id'], nodes['string'])))

    records['date'] = pd.to_datetime(records['entry_time'],
                                     format='%Y-%m-%d %H:%M:%S').dt.date

    records['hour'] = pd.to_datetime(records['date']) + \
        pd.to_timedelta(pd.to_datetime(
            records['entry_time'],
            format='%Y-%m-%d %H:%M:%S').dt.hour, unit='h')

    records['total_people'] = records['total_adults'] + \
        records['minors']

    return records


def time_series_full_plot(data, start_date='2016-06-03', end_date='2016-06-15'):
    """
    Plots a multi line plot for the full time series of all of the museums
    for the whole period specified by start and end dates. Plot is shown with
    matplotlib and nothing is returned.

    Args:
        data (Pandas.DataFrame): the time series data for every museum to plot
        start_date (string): the start date for the timeseries date range
        end_date (string): the end date for the timeseries date range
    """

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 8), dpi=300)

    for key, grp in data.groupby(['short_name']):

        # Filter the largest museums to make graph readable
        if key in ['Accademia', 'Uffizi', 'Opera del Duomo']:
            ax.plot(grp['hour'], grp['total_people'], linewidth=.5,
                    label=str(key))

    plt.legend(bbox_to_anchor=(1.1, 1), loc='upper right')

    ax.set_xlim([start_date, end_date])
    ax.set_ylim([-1, 110])

    ticks = pd.date_range(start_date, end_date, freq='D').date
    plt.xticks(ticks, ticks, rotation='vertical')
    ax.set_xticks(pd.date_range(start_date, end_date, freq='6h'), minor=True)

    plt.show()


def plot_frequencies_total(data, use_log_scale=False):
    """
    Plot the basic frequencies plot for the firenze card visit logs. The graph
    is made with Matplotlib and is bar chart of number of visitors per museum.

    Args:
        data (Pandas.DataFrame): the firenze card logs data prepared by
            prepare_firenzedata
        use_log_scale (bool): whether or not to plot the y-axis in log scale
    """

    df = data.groupby('museum_name').sum()[
        ['total_adults', 'minors']]

    df['total_people'] = df['total_adults'] + df[
        'minors']

    df.sort_values('total_people', inplace=True, ascending=False)

    df.plot.bar(figsize=(16, 8))
    plt.title('Number of Firenze card visitors')
    plt.xlabel('Museum')
    plt.ylabel('Number of people')

    if use_log_scale:
        plt.yscale('log')

    plt.show()


def make_dynamic_firenze_card_edgelist(
        data,
        user_id='user_id',
        timestamp='entry_time',
        date='date',
        location='short_name',
        count='total_people'
):
    """
    Make an edge list for all of the sequential visits of one museum to the next
    in a day per user. Each edge is directed. There is a dummy start node to
    indicate the transition from being home to the first museum visited that day

    Args:
        data (Pandas.DataFrame): The firenze card logs data includes the
        columns specified below.
        user_id (string): name of the user id column in data.
        timestamp (string): name of the column in data that has the time when
            the user was marked at that location.
        date (string): name of the column in data that had the day portion of
            the timestamp.
        location (string): name of the column in data containing the name of the
            museum between which the edges are made.
        count: the name of the counts column in data.

    Returns:
        Pandas.DataFrame: A dataframe representing a dynamic edgelist:
            from, to, number of people, and timestamp
    """

    edges = data.groupby([user_id, timestamp, date, location]) \
        .sum()[count].to_frame()

    edges.reset_index(inplace=True)

    # start is the name of the dummy node for edges from home to the first
    # location visited
    edges['from'] = 'start'

    edges['to'] = edges[location]
    make_link = (edges[user_id].shift(1) == edges[user_id]) & \
                (edges[date].shift(1) == edges[date])

    edges['from'][make_link] = edges[location].shift(1)[make_link]

    # TODO: drop the 'count' column if it's all 1s
    return edges[['from', 'to', count, timestamp]]


def make_static_firenze_card_edgelist(edges, source='from', target='to',
                                      count='total_people'):
    """
    Create a static edge list for the firenze card entry logs from the dynamic
    edge list.

    Args:
        edges (Pandas.DataFrame): dynamic edgelist created by
            make_dynamic_firenze_card_edgelist.
        source (string): name of column for the origin of an edge
        target (string): name of column for the destination of an edge
        count (string): name of the column for the number of people moving along
            that edge at the instance
    Returns:
        Pandas.DataFrame: a dataframe that is a static edgelist aggregated over
            time.
    """

    # TODO: Need to create an "end" of day node
    supp = edges[edges[source].shift(-1) == 'start'][[target, count]]

    supp.columns = [source, count]
    supp[target] = 'end'
    supp = supp[[source, target, count]]

    supp_edges = supp.groupby([source, target])[count].sum().to_frame() \
        .reset_index()

    static = pd.concat([edges.groupby([source, target])[count].sum()
                       .to_frame().reset_index(), supp_edges])

    static.columns = ['from', 'to', 'weight']

    return static


def make_firenze_card_static_graph(data, nodes, join_column='short_name',
                                   lon='longitude', lat='latitude'):
    """
    Create an iGraph network graph from the static edge list created from the
    firenze card entry logs.

    Args:
        data (Pandas.DataFrame): A static edgelist created from
            make_static_firenze_card_edgelist.
        nodes (Pandas.DataFrame): A data frame containing longitude and latitude
            for each museum location.
        join_column (string): the name of the column on which to link the two
            data frames.
        lon (string): the longitude column name
        lat (string): the latitude column name

    Returns:
        igraph.Graph: the museum network graph instance
    """

    g = ig.Graph.TupleList(data.itertuples(index=False), directed=True,
                           weights=True)

    g.vs['indeg'] = g.strength(mode='in', weights='weight')
    g.vs['outdeg'] = g.strength(mode='out', weights='weight')

    # Get rid of the few self-loops, which can plot strangely
    g.simplify(loops=False, combine_edges=sum)

    g.vs['label'] = g.vs["name"]

    # Get coordinates, requires this lengthy query
    location = pd.DataFrame({join_column: g.vs['label']}) \
        .merge(nodes[[join_column, lon, lat]], left_index=True, how='left',
               on=join_column)

    g.vs['x'] = (location[lon]).values.tolist()

    # Latitude is flipped, need to multiply by -1 to get correct orientation
    g.vs['y'] = (-1 * location[lat]).values.tolist()

    return g


def delete_paired_edges(graph, source='Torre di Palazzo Vecchio',
                        target='M. Palazzo Vecchio'):
    """
    Delete both directions of edge between a source and target location. This
    mutates the graph object supplied to this function.

    Args:
        graph (igraph.Graph): the graph to remove the edges from
        source: the source node for the edge to be removed
        target: the target node for the edge to be removed

    Returns:
        igraph.Graph: the graph with the edges from source to target and from
            target to source both deleted
    """

    graph.delete_edges(graph.es.find(_between=(graph.vs(name_eq=source),
                                               graph.vs(name_eq=target))))

    graph.delete_edges(graph.es.find(_between=(graph.vs(name_eq=target),
                                               graph.vs(name_eq=source))))

    return graph


def plot_firenze_card_static_graph(
        graph,
        edge_scale=0.001,
        arrow_scale=0.00025,
        vertex_scale=0.00075,
        label_scale=.00025,
        vertex_color='rgba(100, 100, 255, .75)',
        edge_color='rgba(0, 0, 0, .25)'
):
    """
    Plots the igraph network graph for the firenze card locations network.
    Doesn't return anything.

    Args:
        graph (igraph.Graph): a network graph of firenze card locations
        edge_scale (float): the scaling factor for the edge weight
        arrow_scale (float): the scaling factor for the arrow head size
        vertex_scale (float): the scaling factor for the vertex size
        label_scale (float): the scaling factor for the vertex label size
        vertex_color (string): the color for the vertices in the graph
        edge_color (string): the color for the edges in the graph
    """

    visual_style = {}
    visual_style['edge_width'] = [np.log(edge_scale * i + edge_scale) for i in
                                  graph.es["weight"]]

    visual_style['edge_arrow_size'] = [arrow_scale * i for i in
                                       graph.es["weight"]]

    visual_style['vertex_size'] = [vertex_scale * i for i in graph.vs['indeg']]
    visual_style['vertex_label_size'] = [label_scale * i for i in graph.vs['indeg']]
    visual_style['vertex_color'] = vertex_color
    visual_style['edge_color'] = edge_color
    visual_style["autocurve"] = True

    ig.plot(graph, 'graph.svg', bbox=(1000, 1000), **visual_style)


def make_origin_destination_matrix(graph):
    """
    Create a transition matrix for all possible transitions between pairs of
    museums from the igraph network graph.

    Args:
        graph (igraph.Graph): the graph object for a weighted, directed graph

    Return:
        Pandas.DataFrame: the corresponding transition matrix for the graph,
            ordered by column sums
    """

    transition_matrix = pd.DataFrame(
        graph.get_adjacency(attribute='weight').data,
        columns=graph.vs['name'],
        index=graph.vs['name']
    )

    order = transition_matrix.sum(1).sort_values(ascending=False) \
        .to_frame().index

    return transition_matrix[order].reindex(order)


def plot_origin_destination_matrix_heatmap(transition_matrix):
    """
    Plot the heat map for the transition matrix created from the network graph

    Args:
        transition_matrix (Pandas.DataFrame): a transition matrix
    """

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111)

    cmap = plt.cm.PuBu
    cax = ax.matshow(np.log(transition_matrix), cmap=cmap)
    fig.colorbar(cax)

    ax.set_xticklabels([''] + transition_matrix.index.tolist(), rotation=90)
    ax.set_yticklabels([''] + transition_matrix.index.tolist())

    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))

    plt.show()


def make_firenze_card_daily_paths(
        data,
        user_id='user_id',
        timestamp='entry_time',
        date='date',
        code='string',
        count='total_people'
):
    """
    Creates a DataFrame that has paths, which are a string of single-character
    codes concatenated, for a user per day from the Firenze card logs.

    Args:
        data (Pandas.DataFrame): the prepared augumented firenze card data frame
        user_id (string): the name of a user id column
        timestamp (string): the name of a timestamp column
        date (string): the name of a date column
        code (string): the name of a column with a single-character code for
            each node.
        count (string): the name of a column with the counts

    Returns:
        Pandas.DataFrame: a data frame of daily paths per used
    """

    temp = data.groupby([user_id, timestamp, date, code]).sum()[count].to_frame()
    temp.reset_index(inplace=True)

    temp['start'] = ' '
    temp['target'] = temp[code]

    make_link = (temp[user_id].shift(1) == temp[user_id]) & \
                (temp[date].shift(1) == temp[date])

    temp['start'][make_link] = temp[code].shift(1)[make_link]
    temp['start'][temp['start'].shift(-1) == ' '] = \
        (temp['start'] + temp['target'])[temp['start'].shift(-1) == ' ']

    temp.iloc[-1:]['start'] = temp.iloc[-1:]['start'] + temp.iloc[-1:]['target']

    paths = temp.groupby('user_id')['start'].sum().to_frame()

    return paths['start'].apply(lambda x: pd.Series(x.strip().split(' ')))
    # TODO: Check to see how many cards have variable numbers of children entering


def frequency(data, column_name):
    """
    Creates a frequency table from a dataframe column that is suitable for
    plotting the empirical PMF, empirical CDF, or empirical CCDF.

    Args:
        data (Pandas.DataFrame): dataframe containing column to calculate
            the frequency table for.
        column_name (string): name of a single column, with discrete, including
        integer, values.

    Returns:
        Pandas.DataFrame: the frequency table
    """

    out = data[column_name].value_counts().to_frame()

    out.columns = ['frequency']
    out.index.name = column_name
    out.reset_index(inplace=True)
    out.sort_values('frequency', inplace=True, ascending=False)

    out['cumulative'] = out['frequency'].cumsum()/out['frequency'].sum()
    out['ccdf'] = 1 - out['cumulative']

    return out


def aggregate_firenze_card_daily_paths(data):
    """
    Creates an dataframe with daily paths per user aggregated across all users
    and all days.

    Args:
        data (Pandas.DataFrame): the paths data frame from
            make_firenze_card_daily_paths.

    Returns:
        Pandas.DataFrame: data frame of  paths aggregated across people and days
    """
    # TODO: NEED TO HAVE IMPORTED FREQUENCY!

    pt = pd.concat([frequency(data, 0), frequency(data, 1), frequency(data, 2),
                    frequency(data, 3)])

    pt['daily_path'] = pt[0].replace(np.nan, '', regex=True) + \
                       pt[1].replace(np.nan, '', regex=True) + \
                       pt[2].replace(np.nan,'',regex=True) + \
                       pt[3].replace(np.nan, '', regex=True)

    pt.drop([0, 1, 2, 3, 'ccdf', 'cumulative'], axis=1, inplace=True)

    pt_grouped = pt.groupby('daily_path').sum()
    pt_grouped.sort_values('frequency', inplace=True, ascending=False)

    return pt_grouped


def plot_aggregate_firenze_card_daily_paths(data, use_log_scale=False):
    """
    Plot the frequency of each daily path aggregated across all days and all
    users.

    Args:
        data (Pandas.DataFrame): The aggregated paths for firenzecard for all
            all users and all days created by aggregate_firenze_card_daily_paths
    """
    # TODO: Add a legend to this graph

    data[data['frequency'] > 200].plot.bar(figsize=(16, 8))
    plt.title('Most common daily Firenze card paths across all days')
    plt.xlabel('x = Encoded path')
    plt.ylabel('Number of cards with daily path x')

    if use_log_scale:
        plt.yscale('log')

    plt.show()
