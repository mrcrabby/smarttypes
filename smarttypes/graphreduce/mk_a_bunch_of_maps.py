
import os
import smarttypes
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_reduction import TwitterReduction
from smarttypes.model.twitter_community import TwitterCommunity
from smarttypes.utils.postgres_handle import PostgresHandle

if __name__ == "__main__":

	mk_these_maps = [
		'maxdemarzi',
		'utopiah',
		# 'stamen',
		# 'CocaCola',
		# 'lojak',
		# 'cgtheoret',
		# 'davidseymour',
		# 'bmabey',
		# 'davemcclure',
		# 'snikolov',
		# 'socialphysicist',
		# 'ogrisel',
		# 'jessykate',
		# 'mchelem',
		# 'realkevinroth',
		# 'twarko',
		# 'swixHQ',
		# 'sfi_news',
	]
	for screen_name in mk_these_maps:
		os.system('python reduce_graph.py %s 0' % screen_name)

