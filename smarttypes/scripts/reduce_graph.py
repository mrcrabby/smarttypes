

import smarttypes
from smarttypes.utils.postgres_handle import PostgresHandle
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.utils import graphreduce_utils

if __name__ == "__main__":

    postgres_handle = PostgresHandle(smarttypes.connection_string)

    simple_network = {
        'tim':['ang', 'eve', 'bud'],
        'ang':['tim', 'john', 'denise'],
        'eve':['tim',],
        'bud':['tim'],
        'john':['ang'],
        'denise':['ang'],
    }

    twitter_network = TwitterUser.get_network(postgres_handle)
    print len(twitter_network)
