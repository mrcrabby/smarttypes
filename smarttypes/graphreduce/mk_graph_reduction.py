from igraph import Graph
import smarttypes, sys
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_tweet import TwitterTweet
from datetime import datetime, timedelta
from smarttypes.utils.postgres_handle import PostgresHandle


def print_user_details(user_ids, postgres_handle):
	for user in TwitterUser.get_by_ids(user_ids, postgres_handle):
		try:
			print "%s -- %s" % (user.screen_name, user.description[:100].replace('\n', ' ') 
				if user.description else '')
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
    network = TwitterUser.get_rooted_network(root_user, postgres_handle, distance=10)
    g = Graph(directed=True)
    g.add_vertices(network.keys())
    for source in network:
    	for target in network[source]:
    		if target in network:
    			g.add_edge(source, target)
    del network
    communities = g.community_infomap()

    for community_graph in communities.subgraphs():
    	print ""
    	print "----------------------------------------"
    	member_ids = community_graph.vs["name"]
    	print_user_details(member_ids, postgres_handle)
    