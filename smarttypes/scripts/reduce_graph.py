

import smarttypes
from smarttypes.graphreduce import graphreduce as gr
from smarttypes.utils.postgres_handle import PostgresHandle
from smarttypes.model.twitter_user import TwitterUser

if __name__ == "__main__":

    reduction_file_path = '%s/graphreduce/io/reduction.csv' % smarttypes.root_dir
    postgres_handle = PostgresHandle(smarttypes.connection_string)
    simple_network = {
        'tim':['ang', 'eve', 'bud'],
        'ang':['tim', 'john', 'denise'],
        'eve':['tim',],
        'bud':['tim'],
        'john':['ang'],
        'denise':['ang'],
        'dean':['dean'],
    }
    twitter_network = TwitterUser.get_network(postgres_handle)
    gr.make_sparse_adjanceny_matrix(twitter_network)


