from igraph import Graph
import smarttypes, sys
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_tweet import TwitterTweet
from datetime import datetime, timedelta
from smarttypes.utils.postgres_handle import PostgresHandle


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

if __name__ == "__main__":

    start_time = datetime.now()
    postgres_handle = PostgresHandle(smarttypes.connection_string)
    if not len(sys.argv) > 1:
        raise Exception('Need a twitter handle.')
    else:
        screen_name = sys.argv[1]
    root_user = TwitterUser.by_screen_name(screen_name, postgres_handle)
    network = TwitterUser.get_rooted_network(root_user, postgres_handle, distance=50)
    g = Graph(directed=True)
    g.add_vertices(network.keys())
    for source in network:
    	for target in network[source]:
    		if target in network:
    			g.add_edge(source, target)
    del network

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