from igraph import Graph
import smarttypes, sys, os
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_community import TwitterCommunity
from smarttypes.model.twitter_tweet import TwitterTweet
from datetime import datetime, timedelta
from smarttypes.utils.postgres_handle import PostgresHandle
from collections import defaultdict

def print_user_details(user_ids, postgres_handle):
	for user in TwitterUser.get_by_ids(user_ids, postgres_handle):
		try:
			print "%s -- %s -- %s " % (
				user.screen_name, 
				user.location_name,
				user.description[:100].replace('\n', ' ') if user.description else '',
			)
		except Exception, e:
			""

def do_igraph_community_detection():
    #see these:
    # - http://www.tp.umu.se/~rosvall/downloads/
    # - http://igraph.sourceforge.net/doc-0.6/html/ch22s08.html#igraph_community_infomap
    communities = g.community_infomap() #modularity: 0.354382989825
    #communities = g.community_fastgreedy().as_clustering() #undirected graphs only
    #communities = g.community_label_propagation() #modularity: 0.325206216866
    #communities = g.community_walktrap().as_clustering() #modularity: 0.417456600391
    #communities = g.community_spinglass() #modularity: 0.448054107192
    #communities = g.community_edge_betweenness().as_clustering() #modularity: 0.0039106707787
    print "modularity: %s" % communities.modularity
    print "sizes: %s" % communities.sizes()
    print "----------------------------------------"
    print ""
    for community_graph in communities.subgraphs():
        dyad_census = community_graph.dyad_census()
        if dyad_census[2]:
            dyad_score = float(dyad_census[0]) / float(dyad_census[2])
            print "%s : %s" % (len(community_graph.vs), dyad_score)
            member_ids = community_graph.vs["name"]
            print_user_details(member_ids, postgres_handle)
            print "--end---------------------------------------"


if __name__ == "__main__":

    start_time = datetime.now()
    postgres_handle = PostgresHandle(smarttypes.connection_string)
    if not len(sys.argv) > 1:
        raise Exception('Need a twitter handle.')
    else:
        screen_name = sys.argv[1]
    root_user = TwitterUser.by_screen_name(screen_name, postgres_handle)
    network = TwitterUser.get_rooted_network(root_user, postgres_handle, distance=5)
    #del network

    #load in igraph
    g = Graph(directed=True)
    g.add_vertices(network.keys())
    g.vs["id"] = network.keys()
    for source in network:
        for target in network[source]:
            if target in network:
                g.add_edge(source, target)

    #write to pajek format
    root_file_name = 'partition_0'
    f = open('io/%s.net' % root_file_name, 'w')
    g.write(f, format='pajek') #same as pajek
    os.system('infomap_dir/infomap 345234 io/%s.net 10' % root_file_name)

    #read memberships
    f = open('io/%s.tree' % root_file_name)
    i = 0
    communities = defaultdict(lambda: ([], []))
    for line in f:
        if i == 0:
            i += 1
            continue
        #looks like this: 
        #55:1 0.000542557 "506314355"
        community_num = line.split(':')[0]
        node_id = line.split('"')[1]
        page_rank = float(line.split(' ')[1])
        communities[community_num][0].append(node_id)
        communities[community_num][1].append(page_rank)
        i += 1
        
    #save
    for community_num, id_rank_tup in communities.items():
        TwitterCommunity.create_community(community_num, 
            id_rank_tup[0], id_rank_tup[1], postgres_handle)
        postgres_handle.connection.commit()