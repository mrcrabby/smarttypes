
import smarttypes, sys, os
sys.path.append('/usr/local/lib/python2.7/site-packages')
from igraph import Graph, plot
from igraph.clustering import VertexClustering
from igraph.layout import Layout
from igraph.drawing import colors
import numpy as np
from scipy import spatial
from sklearn.cluster import DBSCAN
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_community import TwitterCommunity
from smarttypes.model.twitter_reduction import TwitterReduction
from smarttypes.model.twitter_tweet import TwitterTweet
from datetime import datetime, timedelta
from smarttypes.utils.postgres_handle import PostgresHandle
from collections import defaultdict


def get_igraph_graph(network):
    print 'load %s users into igraph' % len(network)
    g = Graph(directed=True)
    keys_set = set(network.keys())
    g.add_vertices(network.keys())
    print 'iterative load into igraph'
    edges = []
    for source in network:
        for target in network[source].intersection(keys_set):
            edges.append((source, target))
    g.add_edges(edges)
    g = g.simplify()
    print 'make sure graph is connected'
    connected_clusters = g.clusters()
    connected_cluster_lengths = [len(x) for x in connected_clusters]
    connected_cluster_max_idx = connected_cluster_lengths.index(max(connected_cluster_lengths))
    g = connected_clusters.subgraph(connected_cluster_max_idx)
    if g.is_connected():
        print 'graph is connected'
    else:
        print 'graph is not connected'
    return g

def write_to_pajek_file(g):
    g.vs["id"] = network.keys() #need this for pajek format
    print 'write to pajek format'
    root_file_name = root_user.screen_name
    f = open('io/%s.net' % root_file_name, 'w')
    g.write(f, format='pajek')

def reduce_with_linloglayout(g, root_user):
    input_file = open('io/%s.input' % root_user.screen_name, 'w') 
    for vertex in g.vs:
        for successor in vertex.successors():
            input_file.write('%s %s \n' % (vertex['name'], successor['name']))
    input_file.close()
    #to recompile
    #$ cd smarttypes/smarttypes/graphreduce/LinLogLayout/src/
    #$ javac -d ../bin LinLogLayout.java
    os.system('cd LinLogLayout; java -cp bin LinLogLayout 2 %s %s;' % (
        '../io/%s.input' % root_user.screen_name,
        '../io/%s.output' % root_user.screen_name,
    ))
    f = open('io/%s.output' % root_user.screen_name)
    layout_list = [None] * len(g.vs)
    for line in f:
        line_pieces = line.split(' ')
        node_id = line_pieces[0]
        node_idx = g.vs.find(node_id).index
        x_value = float(line_pieces[1])
        y_value = float(line_pieces[2])
        layout_list[node_idx] = (x_value, y_value)
    return layout_list

def id_communities(g, layout_list, eps=0.42, min_samples=10):
    layout_distance = spatial.distance.squareform(spatial.distance.pdist(layout_list))
    layout_similarity = 1 - (layout_distance / np.max(layout_distance))
    community_idx_list = DBSCAN().fit(layout_similarity, eps=eps, min_samples=min_samples).labels_
    community_idx_list = [int(x) for x in community_idx_list]
    if -1 in community_idx_list:
        community_idx_list = list(np.array(community_idx_list) + 1)
    vertex_clustering = VertexClustering(g, community_idx_list)
    #set color and shape
    color_step = 256 / len(set(community_idx_list))
    colors = np.array(community_idx_list) * color_step
    colors = 255 - colors
    g.vs['color'] = list(colors)
    g.vs['shape'] = ['hidden' if x == 0 else 'circle' for x in community_idx_list]
    return g, vertex_clustering

def get_community_stats(g, vertex_clustering, layout_list):
    layout_list = np.array(layout_list)
    global_pagerank = np.array(g.pagerank(damping=0.70))
    g.vs['size'] = list(global_pagerank / (max(global_pagerank) / 35))
    community_stats = defaultdict(lambda: {
        'center_coordinate':[0,0], 
        'member_ids':[],
        'global_pagerank':[],
        'community_pagerank':[],
        'hybrid_pagerank':[],
    })
    i = 0
    for community_graph in vertex_clustering.subgraphs():
        community_stats[i]['member_ids'] = community_graph.vs['name']
        community_stats[i]['global_pagerank'] = list(global_pagerank[vertex_clustering[i]])
        community_stats[i]['community_pagerank'] = community_graph.pagerank(damping=0.70)
        avg_global_pagerank = sum(community_stats[i]['global_pagerank']) / len(vertex_clustering[i])
        hybrid_pagerank = avg_global_pagerank * np.array(community_stats[i]['community_pagerank'])
        community_stats[i]['hybrid_pagerank'] = list(hybrid_pagerank)
        i += 1
    return community_stats

if __name__ == "__main__":

    #call like this:
    #python reduce_graph.py SmartTypes 0
    start_time = datetime.now()
    postgres_handle = PostgresHandle(smarttypes.connection_string)

    if not len(sys.argv) > 2:
        raise Exception('Need a twitter handle and distance.')
    else:
        screen_name = sys.argv[1]
        distance = int(sys.argv[2])
    root_user = TwitterUser.by_screen_name(screen_name, postgres_handle)
    if distance < 1:
        distance = 10000 / len(root_user.following[:1000])

    network = TwitterUser.get_rooted_network(root_user, postgres_handle, distance=distance)
    g = get_igraph_graph(network)
    layout_list = reduce_with_linloglayout(g, root_user)
    layout = Layout(layout_list)
    g, vertex_clustering = id_communities(g, layout_list, eps=0.62, min_samples=10)
    community_stats = get_community_stats(g, vertex_clustering, layout_list)

    # #palettes
    # #  'red-yellow-green','gray','red-purple-blue','rainbow',
    # #  'red-black-green','terrain','red-blue','heat','red-green'
    filepath = 'io/%s.png' % root_user.screen_name
    plot(g, filepath, (800, 800), layout=layout, palette=colors.palettes["rainbow"], 
        vertex_order_by=('size', True), edge_color="white", edge_width=0, edge_arrow_size=0.1, 
        edge_arrow_width=0.1)

    print 'save to disk'
    twitter_reduction = TwitterReduction.create_reduction(root_user.id, postgres_handle)
    postgres_handle.connection.commit()
    for community_idx, values_dict in community_stats.items():
        #params:
        #reduction_id, index, center_coordinate, member_ids, 
        #global_pagerank, community_pagerank, hybrid_pagerank
        if community_idx > 0:
            TwitterCommunity.create_community(twitter_reduction.id, community_idx, 
                values_dict['center_coordinate'], values_dict['member_ids'], values_dict['global_pagerank'], 
                values_dict['community_pagerank'], values_dict['hybrid_pagerank'], postgres_handle)
        postgres_handle.connection.commit()
    TwitterCommunity.mk_tag_clouds(twitter_reduction.id, postgres_handle)
    postgres_handle.connection.commit()

    os.system('scp io/%s.png cottie:/home/timmyt/projects/smarttypes/smarttypes/static/images/maps/.' % root_user.screen_name)

    print datetime.now() - start_time




