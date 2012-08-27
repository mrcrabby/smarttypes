
import smarttypes, sys, os
import numpy as np
from igraph import Graph
from scipy import spatial
from scipy.stats import scoreatpercentile
from igraph.clustering import VertexClustering
from sklearn.cluster import DBSCAN
from datetime import datetime, timedelta
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_reduction import TwitterReduction
from smarttypes.model.twitter_reduction_user import TwitterReductionUser
from smarttypes.model.twitter_community import TwitterCommunity
from smarttypes.model.ppygis import Point, MultiPoint
from smarttypes.utils.postgres_handle import PostgresHandle

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
    return np.array(layout_list)

def reproject_to_spherical_mercator(coordinates):
    spherical_mercator_bb = np.array([[-175, -80], [175, 80]])
    current_projection_bb = np.array([coordinates.min(0), coordinates.max(0)])
    reprojection = (spherical_mercator_bb / current_projection_bb).min(0)
    return coordinates * reprojection

def id_communities(g, coordinates, eps=0.42, min_samples=10):
    layout_distance = spatial.distance.squareform(spatial.distance.pdist(coordinates))
    layout_similarity = 1 - (layout_distance / np.max(layout_distance))
    community_idx_list = DBSCAN().fit(layout_similarity, eps=eps, min_samples=min_samples).labels_
    if -1 in community_idx_list:
        community_idx_list = list(np.array(community_idx_list) + 1)
    community_idx_list = [int(x) for x in community_idx_list]
    return VertexClustering(g, community_idx_list)

def get_network_stats(network, g, vertex_clustering):
    n = len(g.vs)
    global_pagerank = np.array(g.pagerank(damping=0.75))
    #community stats
    community_pagerank, community_score = np.zeros(n), np.zeros(n)
    for i in range(len(vertex_clustering)):
        #idxs and community_graph
        member_idxs = vertex_clustering[i]
        community_graph = vertex_clustering.subgraph(i)

        #community_pagerank
        tmp_community_pagerank = community_graph.pagerank(damping=0.85)
        community_pagerank[member_idxs] = tmp_community_pagerank / np.max(tmp_community_pagerank)

        #community_score
        community_out = float(sum([len(network[x]) for x in community_graph.vs['name']]))
        community_graph_score = float(sum(community_graph.vs.indegree())) / community_out
        if i != 0:
            community_score[member_idxs] = community_graph_score * (2 + np.log10(len(member_idxs)))
        else:
            community_score[member_idxs] = community_graph_score * 0.01

    #normalize
    global_pagerank = global_pagerank / np.max(global_pagerank)
    community_pagerank = community_pagerank / np.max(community_pagerank)
    community_score = community_score / np.max(community_score)
    return global_pagerank, community_pagerank, community_score

def calculate_hybrid_pagerank(global_pagerank, community_pagerank, community_score):
    hybrid_pagerank = community_pagerank * community_score
    hybrid_pagerank = hybrid_pagerank / scoreatpercentile(hybrid_pagerank, 97)
    return hybrid_pagerank

if __name__ == "__main__":

    #call like this:
    #python reduce_graph.py SmartTypes 0
    start_time = datetime.now()
    postgres_handle = PostgresHandle(smarttypes.connection_string)

    #parse and set inputs
    if len(sys.argv) < 3:
        raise Exception('Need to specify twitter handle and search distance.')
    else:
        screen_name = sys.argv[1]
        distance = int(sys.argv[2])
    root_user = TwitterUser.by_screen_name(screen_name, postgres_handle)
    if distance < 1:
        distance = 10000 / len(root_user.following[:1000])

    #get network and reduce
    if smarttypes.config.IS_PROD:
        start_here = datetime.now()
    else:
        start_here = datetime(2012, 8, 1)
    network = TwitterUser.get_rooted_network(root_user, postgres_handle, 
        start_here=start_here, distance=distance)
    g = get_igraph_graph(network)
    member_ids = np.array(g.vs['name'])
    coordinates = reduce_with_linloglayout(g, root_user)
    
    #id_communities
    vertex_clustering = id_communities(g, coordinates, eps=0.55, min_samples=12)
    #vertex_clustering = id_communities(g, coordinates, eps=0.52, min_samples=18)

    #do this after community detection because it causes distortion
    coordinates = reproject_to_spherical_mercator(coordinates)

    #network_stats
    network_stats = get_network_stats(network, g, vertex_clustering)
    global_pagerank, community_pagerank, community_score = network_stats
    hybrid_pagerank = calculate_hybrid_pagerank(global_pagerank, community_pagerank, community_score)

    #save reduction
    reduction = TwitterReduction.create_reduction(root_user.id, [0, 0, 0], False, postgres_handle)
    postgres_handle.connection.commit()

    #save reduction users
    reduction_users = []
    for i in range(len(member_ids)):
        tru = TwitterReductionUser(postgres_handle=postgres_handle)
        tru.reduction_id = reduction.id
        tru.user_id = member_ids[i]
        tru.coordinates = Point(coordinates[i][0], coordinates[i][1])
        tru.pagerank = global_pagerank[i]
        tru.hybrid_pagerank = hybrid_pagerank[i]
        reduction_users.append(tru.save())
        postgres_handle.connection.commit()

    #save communities
    communities = []
    for i in range(len(vertex_clustering)):
        member_idxs = vertex_clustering[i]
        if i != 0:
            print "community: %s, community_score: %s, members: %s" % (i, 
                community_score[member_idxs][0], len(member_idxs))
            community = TwitterCommunity.create_community(reduction.id, i, member_idxs, 
                member_ids[member_idxs].tolist(), MultiPoint(coordinates[member_idxs]), 
                community_score[member_idxs][0], community_pagerank[member_idxs].tolist(), postgres_handle)
            communities.append(community)
            postgres_handle.connection.commit()
        else:
            print 'community 0 has %s members' % len(member_idxs)

    #render tiles
    os.system('python render_tiles.py')

    #how long
    print datetime.now() - start_time




