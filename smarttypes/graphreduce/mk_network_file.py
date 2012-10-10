
import smarttypes, sys
from smarttypes.model.twitter_user import TwitterUser
from datetime import datetime, timedelta
from smarttypes.utils.postgres_handle import PostgresHandle
from smarttypes.graphreduce import reduce_graph

if __name__ == "__main__":

    start_time = datetime.now()
    postgres_handle = PostgresHandle(smarttypes.connection_string)
    if not len(sys.argv) > 1:
        raise Exception('Need a twitter handle.')
    else:
        screen_name = sys.argv[1]

    if smarttypes.config.IS_PROD:
        start_here = datetime.now()
    else:
        start_here = datetime(2012, 8, 1)
    root_user = TwitterUser.by_screen_name(screen_name, postgres_handle)
    #distance = 25000 / len(root_user.following[:1000])
    distance = 0
    network = TwitterUser.get_rooted_network(root_user, postgres_handle, start_here=start_here, distance=distance)
    print "writing %s nodes to disk" % len(network)
    g = reduce_graph.get_igraph_graph(network)

    lang_names = []
    loc_names = []
    for node_id in g.vs['name']:
        user = TwitterUser.get_by_id(node_id, postgres_handle)
        lang_names.append(user.lang.encode('ascii', 'ignore'))
        loc_names.append(user.location_name.encode('ascii', 'ignore'))
    g.vs['lang_name'] = lang_names
    g.vs['loc_name'] = loc_names
    reduce_graph.write_to_graphml_file(root_user, g, network)
    # print "mk_user_csv took %s to execute" % (datetime.now() - start_time)



    