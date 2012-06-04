

import smarttypes
from smarttypes.utils.postgres_handle import PostgresHandle
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.utils import graphreduce_utils

if __name__ == "__main__":

    adjanceny_matrix_file_path = '%s/graphreduce/io/adjanceny_matrix.csv' % smarttypes.root_dir
    similarity_matrix_file_path = '%s/graphreduce/io/similarity_matrix.csv' % smarttypes.root_dir
    reduction_file_path = '%s/graphreduce/io/reduction.csv' % smarttypes.root_dir

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

    adjanceny_matrix_file = open(adjanceny_matrix_file_path, 'w')
    graphreduce_utils.make_adjanceny_matrix_file(twitter_network, adjanceny_matrix_file)
    adjanceny_matrix_file.close()


