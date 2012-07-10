
from igraph import Graph
import smarttypes, sys
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_tweet import TwitterTweet
from datetime import datetime, timedelta
from smarttypes.utils.postgres_handle import PostgresHandle



def mk_node_attrs_csv(g, file_like, postgres_handle):
    properties = ['screen_name', 'location_name', 'description', 'url']
    try:
        writer = csv.writer(file_like)
        writer.writerow(properties)
        for write_this_id in network:
            write_this_user = cls.get_by_id(write_this_id, postgres_handle)
            initial_stuff = []
            for x in properties:
                value = write_this_user.__dict__.get(x)
                value = value.encode('ascii', 'ignore')
                value = value.replace('\r\n', ' ').replace('\n', ' ')
                initial_stuff.append(value)
            following_ids_str = '::'.join(write_this_user.following_ids)
            writer.writerow(initial_stuff + [following_ids_str])
    finally:
        file_like.close()


if __name__ == "__main__":

    start_time = datetime.now()
    postgres_handle = PostgresHandle(smarttypes.connection_string)
    if not len(sys.argv) > 1:
        raise Exception('Need a twitter handle.')
    else:
        screen_name = sys.argv[1]
    #assumes you've already run reduce_graph
    g = Graph.Read_Pajek('io/%s.net' % screen_name)
    # write_to = open('io/%s.csv' % screen_name, 'w')
    # mk_node_attrs_csv(g, write_to, postgres_handle)
    # print "mk_user_csv took %s to execute" % (datetime.now() - start_time)



    