import warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
import matplotlib.ticker as ticker
from pylab import *
import igraph as ig  # Need to install this in your virtual environment
import matplotlib.pyplot as plt
# import psycopg2
#
# conn = psycopg2.connect(conn_str)
# cursor = conn.cursor()
#
# # Read in table that gives lat-long, short names, and single-character codes
# nodes = pd.read_sql('select * from optourism.firenze_card_locations', con=conn)

# Read in main data, modify it
def prepare_firenzedata(firenzedata, nodes):
    """
    Function: Alter some columns in firenzedata data
    Input: firenzedata from SQL query
    Output: firenzedata data frame with short_name, single-character code, date only, and date+hour only columns
    :param firenzedata:
    :return:
    """
    firenzedata['museum_id'].replace(to_replace=39, value=38, inplace=True)  # We group Palazzo Pitti 2 and Palazzo Pitti Cumulativo together
    firenzedata['short_name'] = firenzedata['museum_id'].replace(dict(zip(nodes['museum_id'], nodes['short_name'])))  # Add "short name" as a column. We make the link now rather than later, even though doing it now is repetitive, because the short_name doesn't have unicode or special characters that can cause some problems.
    firenzedata['string'] = firenzedata['museum_id'].replace(dict(zip(nodes['museum_id'], nodes['string'])))  # Again, add the single-character 'string' column the same way
    firenzedata['date'] = pd.to_datetime(firenzedata['entry_time'],format='%Y-%m-%d %H:%M:%S').dt.date  # Convert the entry_time string to a datetime object
    firenzedata['hour'] = pd.to_datetime(firenzedata['date']) + pd.to_timedelta(pd.to_datetime(firenzedata['entry_time'], format='%Y-%m-%d %H:%M:%S').dt.hour, unit='h')  # Round each observation down to its hourly component. Adding a datetime and timedelta produces the desired format, just doing .dt.hour extracts only the hourly component.
    firenzedata['total_people'] = firenzedata['total_adults'] + firenzedata['minors']
    return firenzedata

# Note: can't drop "nodes" yet, we will later read it again for lat-long. Adding these columns now would also be a waste of space, with no benefit.


#################################
## MAKING COMPLETE TIME SERIES ##
#################################

# # # This is commented out because Io integrated this code
# # We can't just plot the hourly column, because it's not "complete"; hours with no observations are not present,
# # rather than having zero counts. Line plots will connect the observations that are there, skipping over all the
# # zero-count time periods.
# def fill_out_time_series(df,
#                          timeunitname='hour',
#                          timeunitcode='h',
#                          start_date='2016-06-01',
#                          end_date='2016-10-01',
#                          name='short_name',
#                          count='total_people'):
#     """
#     :param df: pandas data frame with a column for time
#     :param timeunitname: name of column with the time unit to fill out
#     :param timeunitcode: built-in encoding, either 'h' for hour, 'D' for day, or '6h', etc.
#     :param start_date: In any standard date format, the startpoint of the filling out
#     :param end_date: In any standard date format, the endpoint of the filling out
#     :param name: entities to aggregate on
#     :param count: column of counts (e.g., total people entering)
#     :return:
#     """
#     df1 = df.groupby([name, timeunitname]).sum()[count].to_frame()
#     df1 = df1.reindex(pd.MultiIndex.from_product([df[name].unique(),
#                                                   pd.date_range(start_date,
#                                                                 end_date,
#                                                                 freq=timeunitcode)]),
#                       fill_value=0)
#     df1.reset_index(inplace=True)
#     df1.columns = [name, timeunitcode, count]  # In case the column names got lost.
#     return df1


# Multi line plot with group_by(). But now that you have df1, you can visualize however
def time_series_full_plot(df1):
    """
    :param df1: a filled-out time series
    :return: A plot of all museums, by hour, for the whole time
    """
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 8), dpi=300)
    for key, grp in df1.groupby(['short_name']):
        if key in ['Accademia', 'Uffizi', 'Opera del Duomo']:  # Without this filter, the plot us unreadable
            ax.plot(grp['hour'], grp['total_people'], linewidth=.5, label=str(key))
    plt.legend(bbox_to_anchor=(1.1, 1), loc='upper right')
    ax.set_xlim(['2016-06-03', '2016-06-15'])
    ax.set_ylim([-1, 110])
    # plt.xticks(pd.date_range('2016-06-01','2016-06-15',freq='D'))
    ticks = pd.date_range('2016-06-03', '2016-06-15', freq='D').date
    plt.xticks(ticks, ticks, rotation='vertical')
    ax.set_xticks(pd.date_range('2016-06-03', '2016-06-15', freq='6h'), minor=True, )
    plt.show()


##########################
## BASIC FREQUENCY PLOT ##
##########################
def plot_frequencies_total(df):
    """
    :param df: the prepared firenzedata frame
    :return: Plot of total frequencies
    """
    df2 = df.groupby('museum_name').sum()[
        ['total_adults', 'minors']]  # Take only these two columns. Could use df1, but might as well go back to df.
    df2['total_people'] = df2['total_adults'] + df2[
        'minors']  # Again, add them. Note that we don't delete these columns, so they will be plotted as well.
    df2.sort_values('total_people', inplace=True, ascending=False)  # Sort the values for easy viewing

    # Plot, prettify as desired. Maybe a stacked bar chart, instead of side-by-side?
    df2.plot.bar(figsize=(16, 8))
    plt.title('Number of Firenze card visitors')
    plt.xlabel('Museum')
    plt.ylabel('Number of people')
    # plt.yscale('log')
    plt.show()


############################################
## ORIGIN-DESTINATION [TRANSITION] MATRIX ##
############################################

# Here's how to generate edges/paths. First see, we've sorted first by user_id and second by timestamp. What we
# want is to make a link between two locations when *people of ONE user_id* go from one location to the next
# *on the same day*, where the link has a weight of the number of people with that id (i.e., one adult, and zero
# to 19 minors on a single Florence card).
# We also use a dummy 'start' node for two reasons. First, it helps us mark the 'start' of a user-day instance.
# Second, by counting the connections from 'start' to each museum, we can count the number of times it is the
# first location visited on a given day.
# Make an index for where to make links, i.e. overwrite 'start' in the 'from' column. Overwrite when the user_id
# and date is the same as the *PREVIOUS* row, with the museum of the previous row (shift(1) means previous row,
# shift(-1) means next row).
def make_dynamic_firenze_card_edgelist(df, user_id='user_id', timestamp='entry_time', date='date', location='short_name', count='total_people'):
    """
    :param df: The firenzedata frame that includes the below columns (specify the names):
    :param user_id: A user_id column
    :param timestamp: The time when the user was marked at that location
    :param date: The day portion of of the timestamp
    :param location: The location between which the edges are made
    :param count: An counts column.
    :return: A pandas dataframe representing a dynamic edgelist: from, to, number of people, and timestamp
    """
    edges = df.groupby([user_id, timestamp, date, location]).sum()[count].to_frame()  # Need to group in this order
    edges.reset_index(inplace=True)
    edges['from'] = 'start'  # Initialize 'from' column with 'start'
    edges['to'] = edges[location]  # Copy 'to' column with row's location
    make_link = (edges[user_id].shift(1) == edges[user_id]) & (edges[date].shift(1) == edges[date])  # Row indexes at
    #  which to overwrite 'start' with actual origin of given edge
    edges['from'][make_link] = edges[location].shift(1)[make_link]  # Do the overwriting
    return edges[['from', 'to', count, timestamp]]  # Might want to drop 'count' column if it's all 1s


def make_static_firenze_card_edgelist(edges, source='from', target='to', count='total_people'):
    """
    :param edges: A dynamic edgelist as a pandas data frame (the timestamp column is aggregated over):
    :param source: The origin of an edge
    :param target: The destination of an edge
    :param count: The number of people moving along that edge at the instance
    :return: a dataframe that is a static edgelist (aggregated over time)
    """
    supp = edges[edges[source].shift(-1) == 'start'][[target, count]]  # Need to get an "end" of day node
    supp.columns = [source, count]
    supp[target] = 'end'
    supp = supp[[source, target, count]]
    supp_edges = supp.groupby([source, target])[count].sum().to_frame().reset_index()
    static = pd.concat([edges.groupby([source, target])[count].sum().to_frame().reset_index(), supp_edges])
    static.columns = ['from','to','weight']
    return static


# Didn't work, didn't take into account the number of people leaving the given museum
# def add_home_node_firenze_card_static_edgelist(from_to_home, edgelist):
#     """
#     :param from_to_home: data frame generated from from_to_home_firenze_card_edges_generator (below)
#     :param edgelist: data frame generated from make_static_firenze_card_edgelist above
#     :return: augmented static edgelist, with counts to and from a "home" node
#     """
#     from_to_home.reset_index(inplace=True)
#     supp_edges = pd.DataFrame({'from': ['start'] * from_to_home.shape[0] + from_to_home['short_name'].tolist(),
#                                'to': from_to_home['short_name'].tolist() + ['end'] * from_to_home.shape[0],
#                                'weight': from_to_home['home_to_node'].tolist() + from_to_home['node_to_home'].tolist()
#                                })
#     supp_edges.dropna(how='any', inplace=True)
#     out = pd.concat([edgelist, supp_edges])
#     out = out[out['from'] != 'start']
#     return out


def make_firenze_card_static_graph(df, nodes, name='short_name', x='longitude', y='latitude'):
    """
    :param df: A static edgelist from above
    :param nodes: A data frame containing longitude and latitude
    :param name: the name on which to link the two data frames
    :param x: the longitude column name
    :param y: the latitude column name
    :return: an igraph graph object
    """
    g = ig.Graph.TupleList(df.itertuples(index=False), directed=True, weights=True)
    g.vs['indeg'] = g.strength(mode='in', weights='weight') # Save weighted indegree with dummy "source" node
    g.vs['outdeg'] = g.strength(mode='out', weights='weight')  # Save weighted indegree with dummy "source" node
    # g.delete_vertices([v.index for v in g.vs if v['name'] == u'start']) # Delete the dummy "source" node
    g.simplify(loops=False, combine_edges=sum) # Get rid of the few self-loops, which can plot strangely
    g.vs['label'] = g.vs["name"] # Names imported as 'name', but plot labels default to 'label'. Copy over.
    # Get coordinates, requires this lengthy query
    xy = pd.DataFrame({name: g.vs['label']}).merge(nodes[[name, x, y]], left_index=True, how='left', on=name)
    g.vs['x'] = (xy[x]).values.tolist()
    g.vs['y'] = (-1 * xy[y]).values.tolist() # Latitude is flipped, need to multiply by -1 to get correct orientation
    return g


def delete_paired_edges(g,s='Torre di Palazzo Vecchio',t='M. Palazzo Vecchio'):
    """
    :param g: an igraph graph object
    :param s: the source node
    :param t: the target node
    :return: the graph, with the links from s to t and from t to s both deleted
    """
    g.delete_edges(g.es.find(_between=(g.vs(name_eq=s), g.vs(name_eq=t))))
    g.delete_edges(g.es.find(_between=(g.vs(name_eq=t), g.vs(name_eq=s))))
    return g


def plot_firenze_card_static_graph(g):
    """
    :param g: an igraph graph of firenze card locations
    :return: a plot. NOTE: THIS NEEDED SOURCE CODE EDITING. Change edges.py in igraph to have 100*precision.
    """
    visual_style = {}
    visual_style['edge_width'] = [np.log(.001 * i + .001) for i in
                                  g.es["weight"]]  # Scale weights. .001*i chosen by hand. Try also .05*np.sqrt(i)
    visual_style['edge_arrow_size'] = [.00025 * i for i in
                                       g.es["weight"]]  # .00025*i chosen by hand. Try also .01*np.sqrt(i)
    visual_style['vertex_size'] = [.00075 * i for i in g.vs['indeg']]  # .00075 is from hand-tuning
    visual_style['vertex_label_size'] = [.00025 * i for i in g.vs['indeg']]
    visual_style['vertex_color'] = "rgba(100, 100, 255, .75)"
    visual_style['edge_color'] = "rgba(0, 0, 0, .25)"
    visual_style["autocurve"] = True
    ig.plot(g, 'graph.svg', bbox=(1000, 1000), **visual_style)


def plot_firenze_card_static_graph_backup(g):
    """
    :param g: an igraph graph of firenze card locations
    :return: A graph that is not pretty but will work without source code editing
    """
    visual_style = {}
    visual_style['vertex_size'] = [.000075 * i for i in indeg]  # .00075 is from hand-tuning
    visual_style['vertex_label_size'] = [.00025 * i for i in indeg]
    visual_style['edge_width'] = [np.floor(.001 * i) for i in
                              g.es["weight"]]  # Scale weights. .001*i chosen by hand. Try also .05*np.sqrt(i)
    ig.plot(g.as_undirected(), **visual_style) # Positions, for reference


def make_origin_destination_matrix(g):
    """
    :param g: an igraph graph object for a weighted, directed graph
    :return: the corresponding transition matrix, ordered by column sums
    """
    transition_matrix = pd.DataFrame(g.get_adjacency(attribute='weight').data, columns=g.vs['name'], index=g.vs['name'])
    order = transition_matrix.sum(1).sort_values(ascending=False).to_frame().index
    transition_matrix = transition_matrix[order].reindex(order)
    return transition_matrix


def plot_origin_destination_matrix_heatmap(transition_matrix):
    """
    :param transition_matrix: a transition matrix from above
    :return: a plot of a heatmap of the matrix
    """
    fig = plt.figure(figsize=(10, 10))  # ,dpi=300)
    ax = fig.add_subplot(111)
    cmap = plt.cm.PuBu
    cax = ax.matshow(np.log(transition_matrix), cmap=cmap)
    fig.colorbar(cax)
    ax.set_xticklabels([''] + transition_matrix.index.tolist(), rotation=90)
    ax.set_yticklabels([''] + transition_matrix.index.tolist())
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    plt.show()


def make_firenze_card_daily_paths(df,
                                  user_id='user_id',
                                  timestamp='entry_time',
                                  date='date',
                                  code='string',
                                  count='total_people'):
    """
    :param df: the prepared firenze card data frame
    :param user_id: the name of a user_id column
    :param timestamp: the name of a timestamp column
    :param date: the name of a date column
    :param code: the name of a column with a single-character code for each node # TODO Rewrite allowing numbers
    :param count: the name of a column with counts
    :return: a data frame of paths
    """
    temp = df.groupby([user_id, timestamp, date, code]).sum()[count].to_frame()  # Need to group in this order
    temp.reset_index(inplace=True)
    temp['s'] = ' '  # Initialize 'from' column with empty string for 'start'
    temp['t'] = temp[code]  # Copy 'to' column with row's museum_name
    make_link = (temp[user_id].shift(1) == temp[user_id]) & (temp[date].shift(1) == temp[date]) # Row indexes at
    #  which to overwrite 's' with origin
    temp['s'][make_link] = temp[code].shift(1)[make_link]  # Do the overwriting
    # Concatenating the source column is not enough, it leaves out the last place in the path. Do this:
    temp['s'][temp['s'].shift(-1) == ' '] = (temp['s'] + temp['t'])[temp['s'].shift(-1) == ' ']
    # But the above line doesn't work for the very last row of data. So, do this as well:
    temp.iloc[-1:]['s'] = temp.iloc[-1:]['s'] + temp.iloc[-1:]['t']
    paths = temp.groupby('user_id')['s'].sum().to_frame()  # sum() on strings concatenates
    out = paths['s'].apply(lambda x: pd.Series(x.strip().split(' ')))  # Now split along strings. Takes a few seconds.
    # Note: 4 columns is correct, Firenze card is *72 hours from first use*, not from midnight of the day of first day!
    return out
    # TODO: Check to see how many cards have variable numbers of children entering


# # Didn't work, didn't take into account the number of people leaving the given museum
# def from_to_home_firenze_card_edges_generator(paths, nodes):
#     """
#     :param paths: data frame from make_firenze_card_daily_paths
#     :param nodes: nodes data frame
#     :return: data frame of short_name as index, columns for home_to_node, node to home
#     """
#     df9 = paths.fillna(' ')
#     df9['0_first'] = df9[0].apply(lambda x: pd.Series(x[0]))
#     df9['0_last'] = df9[0].apply(lambda x: pd.Series(x[-1]))
#     df9['0_len'] = df9[0].apply(lambda x: pd.Series(len(x)))
#     df9['1_first'] = df9[1].apply(lambda x: pd.Series(x[0]))
#     df9['1_last'] = df9[1].apply(lambda x: pd.Series(x[-1]))
#     df9['1_len'] = df9[1].apply(lambda x: pd.Series(len(x)))
#     df9['2_first'] = df9[2].apply(lambda x: pd.Series(x[0]))
#     df9['2_last'] = df9[2].apply(lambda x: pd.Series(x[-1]))
#     df9['2_len'] = df9[2].apply(lambda x: pd.Series(len(x)))
#     df9['3_first'] = df9[3].apply(lambda x: pd.Series(x[0]))
#     df9['3_last'] = df9[3].apply(lambda x: pd.Series(x[-1]))
#     df9['3_len'] = df9[3].apply(lambda x: pd.Series(len(x)))
#     df9.replace(' ', np.nan, inplace=True)
#     from_home = frequency(df9[['0_first', '1_first', '2_first', '3_first']].stack().to_frame(), 0)[[0, 'frequency']]
#     from_home.columns = ['0', 'from_home']
#     from_home.set_index('0', inplace=True)
#     only = frequency(pd.concat(
#         [df9[(df9['0_len'] == 1) & (df9['0_first'].notnull())]['0_first'],
#          df9[(df9['1_len'] == 1) & (df9['1_first'].notnull())]['1_first'],
#          df9[(df9['2_len'] == 1) & (df9['2_first'].notnull())]['2_first'],
#          df9[(df9['3_len'] == 1) & (df9['3_first'].notnull())]['3_first']
#          ], axis=0).to_frame()
#                      , 0)[[0, 'frequency']]
#     only.columns = ['0', 'only']
#     only.set_index('0', inplace=True)
#     to_home = frequency(df9[['0_last', '1_last', '2_last', '3_last']].stack().to_frame(), 0)[[0, 'frequency']]
#     to_home.columns = ['0', 'to_home']
#     to_home.set_index('0', inplace=True)
#     from_to_home = nodes.set_index('string')['short_name'].to_frame().join([from_home, to_home, only])
#     from_to_home.set_index('short_name', inplace=True)
#     from_to_home.columns = ['home_to_node', 'node_to_home', 'only_visit_of_day']
#     # from_to_home['from_home'] = from_to_home['home_to_node'] - from_to_home['only_visit_of_day']
#     # from_to_home['to_home'] = from_to_home['node_to_home'] - from_to_home['only_visit_of_day']
#     return from_to_home


def frequency(dataframe,columnname):
    """
    :param dataframe: a pandas dataframe
    :param columnname: a single column, with discrete (including integer) values
    :return: a frequency table, suitable for plotting the empirical PMF, empirical CDF, or empirical CCDF
    """
    out = dataframe[columnname].value_counts().to_frame()
    out.columns = ['frequency']
    out.index.name = columnname
    out.reset_index(inplace=True)
    out.sort_values('frequency',inplace=True,ascending=False)
    out['cumulative'] = out['frequency'].cumsum()/out['frequency'].sum()
    out['ccdf'] = 1 - out['cumulative']
    return out


# NOTE: NEED TO HAVE IMPORTED FREQUENCY!
def aggregate_firenze_card_daily_paths(df):
    """
    :param df: the paths data frame from above
    :return: A data frame of the paths aggregated across people and days
    """
    pt = pd.concat([frequency(df, 0), frequency(df, 1), frequency(df, 2), frequency(df, 3)])
    pt['daily_path'] = pt[0].replace(np.nan, '', regex=True) + \
                       pt[1].replace(np.nan, '', regex=True) + \
                       pt[2].replace(np.nan,'',regex=True) + \
                       pt[3].replace(np.nan, '', regex=True)
    pt.drop([0, 1, 2, 3, 'ccdf', 'cumulative'], axis=1, inplace=True)
    pt2 = pt.groupby('daily_path').sum()
    pt2.sort_values('frequency', inplace=True, ascending=False)
    return pt2


def plot_aggregate_firenze_card_daily_paths(pt2):
    """
    :param pt2: The aggregated paths data from above
    :return: A plot of the frequencies (still needs a legend)
    """
    pt2[pt2['frequency'] > 200].plot.bar(figsize=(16, 8))
    plt.title('Most common daily Firenze card paths across all days')
    plt.xlabel('x = Encoded path')
    plt.ylabel('Number of cards with daily path x')
    # plt.yscale('log')
    plt.show()

