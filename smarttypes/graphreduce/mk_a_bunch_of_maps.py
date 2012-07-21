
import os
import smarttypes
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_reduction import TwitterReduction
from smarttypes.model.twitter_community import TwitterCommunity


if __name__ == "__main__":

	root_user_count_tups = TwitterReduction.get_user_reduction_counts(postgres_handle)
	for user, reduction_count in root_user_count_tups:
		print 'making map for %s' % user.screen_name
		os.system('python reduce_graph.py %s 0' % user.screen_name)

