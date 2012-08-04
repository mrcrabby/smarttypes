
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
    return vertex_clustering

def get_network_stats(network, g, layout_list, vertex_clustering):
    n = len(network)
    member_ids = np.array(g.vs['name'])
    coordinates = np.array(layout_list)
    global_pagerank = np.array(g.pagerank(damping=0.65))
    #community stats
    community_pagerank, community_score = np.zeros(n), np.zeros(n)
    for i in range(len(vertex_clustering)):
        if vertex_clustering[i].modularity > 0:
            member_idxs = vertex_clustering[i]
            community_graph = vertex_clustering.subgraph(i)
            community_pagerank[member_idxs] = community_graph.pagerank(damping=0.65)
            community_out = float(sum([len(network[x]) for x in community_graph.vs['name']]))
            community_graph_score = float(sum(community_graph.vs.indegree())) / community_out
            community_score[member_idxs] = community_graph_score
    return member_ids, coordinates, global_pagerank, community_pagerank, community_score

def calculate_hybrid_pagerank(global_pagerank, community_pagerank, community_score):
    #need to normalize this
    return (global_pagerank * 1) * (community_pagerank * 1) * (community_score * 1)


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
    vertex_clustering = id_communities(g, layout_list, eps=0.62, min_samples=12)

    #network_stats
    network_stats = get_network_stats(network, g, vertex_clustering, layout_list)
    member_ids, coordinates, global_pagerank, community_pagerank, community_score = network_stats
    hybrid_pagerank = calculate_hybrid_pagerank(global_pagerank, community_pagerank, community_score)

    #save reduction
    reduction = TwitterReduction.create_reduction(root_user.id, list(member_ids), list(coordinates), 
        list(global_pagerank), list(hybrid_pagerank), [0, 0, 0], postgres_handle)
    postgres_handle.connection.commit()

    #save communities
    for i in range(len(vertex_clustering)):
        if vertex_clustering[i].modularity > 0:
            
            member_idxs = vertex_clustering[i]

            print "community: %s, modularity: %s, community_score: %s" % (
                i, vertex_clustering[i].modularity, community_score[member_idxs][0])

            TwitterCommunity.create_community(reduction.id, i, list(member_ids[member_idxs]), 
                list(member_idxs), list(coordinates[member_idxs]), community_score[member_idxs][0], 
                list(community_pagerank), postgres_handle)
            postgres_handle.connection.commit()

    #how long
    print datetime.now() - start_time




