
import smarttypes, sys, os
sys.path.append('/usr/local/lib/python2.7/site-packages')
from igraph import Graph, plot
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
        for following_vertex in vertex.successors():
            input_file.write('%s %s \n' % (vertex['name'], following_vertex['name']))
    input_file.close()
    #to recompile
    #$ cd smarttypes/smarttypes/graphreduce/LinLogLayout/src/
    #$ javac -d ../bin LinLogLayout.java
    os.system('cd LinLogLayout; java -cp bin LinLogLayout 2 %s %s;' % (
        '../io/%s.input' % root_user.screen_name,
        '../io/%s.output' % root_user.screen_name,
    ))
    f = open('io/%s.output' % root_user.screen_name)
    for line in f:
        line_pieces = line.split(' ')
        node_id = line_pieces[0]
        x_value = float(line_pieces[1])
        y_value = float(line_pieces[2])
        community_idx = int(line_pieces[4])
        g.vs.find(node_id)['x_y'] = (x_value, y_value)
        g.vs.find(node_id)['community_idx'] = community_idx
    return g

def reduce_and_save_communities(root_user, distance=10, return_graph_for_inspection=False):
    print 'starting reduce_and_save_communities'
    print 'root_user: %s,  following_in_our_db: %s, distance: %s' % (
        root_user.screen_name, len(root_user.following), distance)

    network = TwitterUser.get_rooted_network(root_user, postgres_handle, distance=distance)
    g = get_igraph_graph(network)
    g = reduce_with_linloglayout(g, root_user)
    if return_graph_for_inspection:
        return g

    #id communities
    #communities = defaultdict(lambda: ([], [], []))

    # print 'save final to disk'
    # twitter_reduction = TwitterReduction.create_reduction(root_user.id, postgres_handle)
    # postgres_handle.connection.commit()
    # for community_idx, id_rank_tup in communities.items():
    #     #params:
    #     #reduction_id, index, 
    #     #community_edges, member_ids, member_scores, postgres_handle
    #     if len(id_rank_tup[2]) > 5:
    #         TwitterCommunity.create_community(twitter_reduction.id, community_idx, 
    #             id_rank_tup[0], id_rank_tup[1], id_rank_tup[2], postgres_handle)
    #     postgres_handle.connection.commit()
    # TwitterCommunity.mk_tag_clouds(twitter_reduction.id, postgres_handle)
    # postgres_handle.connection.commit()


if __name__ == "__main__":

    #call like this:
    #python reduce_graph.py SmartTypes 0

    #to inspect the igraph g in ipython:
    #ipython -i reduce_graph.py SmartTypes 0 0

    start_time = datetime.now()
    postgres_handle = PostgresHandle(smarttypes.connection_string)

    if not len(sys.argv) > 2:
        raise Exception('Need a twitter handle and distance.')
    else:
        screen_name = sys.argv[1]
        distance = int(sys.argv[2])

    return_graph_for_inspection = False
    if len(sys.argv) > 3 and int(sys.argv[3]) == 0:
        print 'return_graph_for_inspection'
        return_graph_for_inspection = True

    root_user = TwitterUser.by_screen_name(screen_name, postgres_handle)
    if distance < 1:
        distance = 500 / len(root_user.following)
    g = reduce_and_save_communities(root_user, distance, return_graph_for_inspection)

    print datetime.now() - start_time




