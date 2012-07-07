from igraph import Graph
import smarttypes, sys, os
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_community import TwitterCommunity
from smarttypes.model.twitter_reduction import TwitterReduction
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
    g.vs["id"] = network.keys() #need this for pajek format
    for source in network:
        for target in network[source]:
            if target in network:
                g.add_edge(source, target)

    #write to pajek format
    root_file_name = 'partition_0'
    f = open('io/%s.net' % root_file_name, 'w')
    g.write(f, format='pajek')

    #run infomap
    #infomap_command = 'infomap_dir/infomap 345234 io/%s.net 10'
    infomap_command = 'conf-infomap_dir/conf-infomap 344 io/%s.net 15 10 0.50'
    os.system(infomap_command % root_file_name)

    #read into memory
    f = open('io/%s.smap' % root_file_name)

    section_header = ''
    communities = defaultdict(lambda: ([], [], []))
    for line in f:
        if line.startswith('*Modules'):
            section_header = 'Modules'
            continue
        if line.startswith('*Insignificants'):
            section_header = 'Insignificants'
            continue
        if line.startswith('*Nodes'):
            section_header = 'Nodes'
            continue
        if line.startswith('*Links'):
            section_header = 'Links'
            continue

        if section_header == 'Modules':
            #looks like this:
            #1 "26000689,..." 0.130147 0.0308866
            #The names under *Modules are derived from the node with the highest 
            #flow volume within the module, and 0.25 0.0395432 represent, respectively, 
            #the aggregated flow volume of all nodes within the module and the per 
            #step exit flow from the module.
            continue

        if section_header == 'Nodes':
            #looks like this: 
            #1:10 "2335431" 0.00365772
            #or w/ a semicolon instead, semicolon means not significant
            #see http://www.tp.umu.se/~rosvall/code.html
            if ';' in line:
                continue
            community_idx = line.split(':')[0]
            node_id = line.split('"')[1]
            final_volume = float(line.split(' ')[2])
            communities[community_idx][1].append(node_id)
            communities[community_idx][2].append(final_volume)

        if section_header == 'Links':
            #community_edges
            #looks like this:
            #1 4 0.0395432
            community_idx = line.split(' ')[0]
            target_community_idx = line.split(' ')[1]
            edge_weight = line.split(' ')[2]
            communities[community_idx][0].append('%s:%s' % (target_community_idx, edge_weight))
        
    #insert into the db
    twitter_reduction = TwitterReduction.create_reduction(root_user.id, postgres_handle)
    postgres_handle.connection.commit()
    for community_idx, id_rank_tup in communities.items():
        #params:
        #reduction_id, index, 
        #community_edges, member_ids, member_scores, postgres_handle
        if len(id_rank_tup[2]) > 3:
            TwitterCommunity.create_community(twitter_reduction.id, community_idx, 
                id_rank_tup[0], id_rank_tup[1], id_rank_tup[2], postgres_handle)
        postgres_handle.connection.commit()
    TwitterCommunity.mk_tag_clouds(twitter_reduction.id, postgres_handle)
    postgres_handle.connection.commit()



