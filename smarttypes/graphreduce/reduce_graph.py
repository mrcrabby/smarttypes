
import smarttypes, sys, os
import numpy as np
from scipy import spatial
from igraph.clustering import VertexClustering
from sklearn.cluster import DBSCAN
from datetime import datetime, timedelta
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_community import TwitterCommunity
from smarttypes.model.twitter_reduction import TwitterReduction
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
    if -1 in community_idx_list:
        community_idx_list = list(np.array(community_idx_list) + 1)
    community_idx_list = [int(x) for x in community_idx_list]
    vertex_clustering = VertexClustering(g, community_idx_list)
    return g, community_idx_list, vertex_clustering

def get_community_stats(network, g, vertex_clustering, layout_list):
    global_pagerank = np.array(g.pagerank(damping=0.65))
    community_stats = defaultdict(lambda: {
        'center_coordinate':[0,0],
        'member_idxs':[], 
        'member_ids':[],
        'global_pagerank':[],
        'community_pagerank':[],
        'hybrid_pagerank':[],
    })
    i = 0
    for community_graph in vertex_clustering.subgraphs():
        community_stats[i]['member_idxs'] = vertex_clustering[i]
        community_stats[i]['member_ids'] = community_graph.vs['name']
        community_stats[i]['global_pagerank'] = list(global_pagerank[vertex_clustering[i]])
        community_stats[i]['community_pagerank'] = community_graph.pagerank(damping=0.65)
        avg_global_pagerank = sum(community_stats[i]['global_pagerank']) / len(vertex_clustering[i])
        community_out = float(sum([len(network[x]) for x in community_graph.vs['name']]))
        community_closeness_score = float(sum(community_graph.vs.indegree())) / community_out
        hybrid_pagerank = (community_closeness_score * 1) * (avg_global_pagerank * 1) * \
            (np.array(community_stats[i]['community_pagerank']) * 2)
        community_stats[i]['hybrid_pagerank'] = list(hybrid_pagerank)
        i += 1
    return community_stats

if __name__ == "__main__":

    #call like this:
    #python reduce_graph.py SmartTypes 0
    start_time = datetime.now()
    postgres_handle = PostgresHandle(smarttypes.connection_string)

    #parse and set inputs
    if len(sys.argv) < 3:
        raise Exception('Need a twitter handle and distance.')
    else:
        screen_name = sys.argv[1]
        distance = int(sys.argv[2])
    root_user = TwitterUser.by_screen_name(screen_name, postgres_handle)
    if distance < 1:
        distance = 10000 / len(root_user.following[:1000])

    #get network and reduce
    network = TwitterUser.get_rooted_network(root_user, postgres_handle, distance=distance)
    g = get_igraph_graph(network)
    layout_list = reduce_with_linloglayout(g, root_user)
    
    #id_communities
    g, community_idx_list, vertex_clustering = id_communities(g, layout_list, eps=0.62, 
        min_samples=12)

    #community_stats
    community_stats = get_community_stats(network, g, vertex_clustering, layout_list)

    #save reduction
    TwitterReduction.create_reduction(root_user_id, member_ids, coordinates, pagerank, 
        hybrid_pagerank, translate_rotate_mask, postgres_handle)
    postgres_handle.connection.commit()

    #save communities
    for community_idx, values_dict in community_stats.items():
        TwitterCommunity.create_community(reduction_id, index, member_ids, member_idxs, 
            coordinates, community_score, community_pagerank, postgres_handle)
        postgres_handle.connection.commit()

    #how long
    print datetime.now() - start_time




