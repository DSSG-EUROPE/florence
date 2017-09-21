import pandas as pd
import igraph as ig

from ..utils.database import dbutils


# TODO: Cleanup
def hourly_graph():
    connection = dbutils.connect()

    foreigners = pd.read_sql("""
        SELECT 
          prev_tower_id, 
          tower_id, 
          count(*) AS weight 
        FROM optourism.foreigners_path_records_joined 
        WHERE tower_id != prev_tower_id 
          AND EXTRACT(HOUR FROM date_time_m) = 22 
          AND delta < (INTERVAL '30 minutes') 
        GROUP BY tower_id, prev_tower_id
    """, con=connection)

    tower_vertices = pd.read_sql("""
        SELECT DISTINCT tower_id, lat, lon 
        FROM optourism.foreigners_path_records_joined
    """, con=connection)

    connection.close()

    foreigners['tower_id'] = foreigners['tower_id'].apply(
        lambda x: 'tower-%s' % x)

    foreigners['prev_tower_id'] = foreigners['prev_tower_id'].apply(
        lambda x: 'tower-%s' % x)

    tower_vertices['tower_id'] = tower_vertices['tower_id'].apply(
        lambda x: 'tower-%s' % x)

    graph = ig.Graph()
    graph.add_vertices(tower_vertices.shape[0])
    graph.vs['name'] = tower_vertices['tower_id']
    graph.vs['x'] = tower_vertices['lat']
    graph.vs['y'] = tower_vertices['lon']

    edges = zip(foreigners['prev_tower_id'], foreigners['tower_id'])
    graph.add_edges(edges)
    graph.es['weight'] = foreigners['weight']
    graph.es.select(weight_lt=5).delete()

    visual_style = {'vertex_color': 'black',
                    'vertex_size': 3,
                    'edge_width': [.01 * i for i in
                                   graph.es["weight"]]}

    ig.plot(graph, bbox=(800, 800), **visual_style)


def dwell_time_graph():
    pass


if __name__ == '__main__':
    pass
