
import os
import smarttypes
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_credentials import TwitterCredentials
from smarttypes.model.twitter_reduction import TwitterReduction
from smarttypes.model.twitter_community import TwitterCommunity
from smarttypes.utils.postgres_handle import PostgresHandle
postgres_handle = PostgresHandle(smarttypes.connection_string)

if __name__ == "__main__":

    mk_these_maps = []
    for creds in TwitterCredentials.get_all(postgres_handle):
        root_user = creds.root_user
        if root_user and root_user.screen_name not in mk_these_maps:
            mk_these_maps.append(root_user.screen_name)

    for screen_name in mk_these_maps:
    	if screen_name not in ['CocaCola', 'pyohio', 'codemash', 'maxdemarzi']:
        	print 'making a map for %s' % screen_name
        	os.system('python reduce_graph.py %s 0' % screen_name)

