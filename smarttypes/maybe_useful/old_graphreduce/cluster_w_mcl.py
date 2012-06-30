
import os
import numpy as np
from scipy.stats import scoreatpercentile
from collections import OrderedDict
from cogent.maths.distance_transform import dist_euclidean
from sklearn.cluster import DBSCAN, KMeans, Ward
import smarttypes
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.utils.postgres_handle import PostgresHandle


def load_network_from_the_db(postgres_handle, distance):
    network = OrderedDict()
    def add_user_to_network(user):
        network[user.id] = {}
        network[user.id]['following_ids'] = set(user.following_ids)
        network[user.id]['follower_ids'] = set([])
        network[user.id]['following_count'] = user.following_count
        network[user.id]['followers_count'] = user.followers_count
    twitter_user = TwitterUser.by_screen_name('SmartTypes', postgres_handle)
    add_user_to_network(twitter_user)
    for following in twitter_user.following:
        add_user_to_network(following)
        for following_following in following.following[:distance]:
            add_user_to_network(following_following)
    return network


def mk_similarity_matrix(network):
    def scoring_function(intersect_group, intersect_node_discount):
        total_score = 0
        for intersect_id in intersect_group:
            intersect_node = network.get(intersect_id)
            if intersect_node:
                intersect_node_popularity = intersect_node[intersect_node_discount]
                if intersect_node_popularity < 2:
                    intersect_node_popularity = 2
                try:
                    total_score += 1.0 / np.log(intersect_node_popularity) #/ (np.log(len_following_difference) / 2)
                except FloatingPointError, ex:
                    print "This shouldnt happen"
                    print intersect_id, intersect_node_popularity, intersect_node[intersect_node_discount], 
        return total_score

    similarity_matrix = []
    for node_id, node in network.items():
        landmark_similarities = []
        for landmark_id, landmark_node in network.items():
            total_score = 0.0
            following_intersect = node['following_ids'].intersection(landmark_node['following_ids'])
            follower_intersect = node['follower_ids'].intersection(landmark_node['follower_ids'])
            total_score += (scoring_function(following_intersect, 'followers_count') * 1)
            total_score += (scoring_function(follower_intersect, 'following_count') * 1)
            landmark_similarities.append(total_score)
        similarity_matrix.append(landmark_similarities)
    similarity_matrix = np.array(similarity_matrix)

    #clean up some loose ends + normalize
    floor = scoreatpercentile(similarity_matrix, 20)[1]
    ceiling = scoreatpercentile(similarity_matrix, 90)[1]
    print floor, ceiling
    #similarity_matrix[similarity_matrix < floor] = floor
    similarity_matrix[similarity_matrix > ceiling] = ceiling
    similarity_matrix = similarity_matrix / ceiling
    return similarity_matrix


def cluster_w_mcl(network, similarity_matrix):
    #http://www.micans.org/mcl/man/clmprotocols.html
    mcl_input_file = open('io/mcl_input.abc', 'w') 
    for i in range(len(network)):
        node_id = network.keys()[i]
        for j in range(len(network)):
            following_id = network.keys()[j]
            similarity_score = similarity_matrix[i,j]
            if following_id in network:
              mcl_input_file.write('%s %s %s \n' % (node_id, following_id, similarity_score))

    mcl_input_file.close()
    os.system('cd io; mcxload -abc mcl_input.abc -write-tab data.tab -o data.mci')
    os.system('cd io; mcl data.mci -I 5')
    os.system('cd io; mcxdump -icl out.data.mci.I50 -tabr data.tab -o dump.data.mci.I50')

    communities = OrderedDict()
    mcl_output_file = open('io/dump.data.mci.I50')
    i = 1
    for line in mcl_output_file:
        communities[i] = line.split()
        i += 1
    return communities


def cluster_w_else(network, similarity_matrix, number_of_communities=20):
  raw_communities = Ward(n_clusters=number_of_communities).fit(similarity_matrix).labels_
  #raw_communities = KMeans(k=number_of_communities).fit(similarity_matrix).labels_
  #raw_communities = DBSCAN().fit(similarity_matrix, eps=eps, min_samples=min_samples).labels_
  communities = OrderedDict([(x,[]) for x in range(number_of_communities)])
  for i in range(len(network)):
    community_idx = raw_communities[i]
    if community_idx != -1:
      communities[community_idx].append(network.keys()[i])
  return communities



def print_user_details(user_ids, postgres_handle):
  for user in TwitterUser.get_by_ids(user_ids, postgres_handle):
    try:
        print "%s -- %s" % (user.screen_name, 
          user.description[:100].replace('\n', ' ') if user.description else '')
    except Exception, e:
        ''


if __name__ == "__main__":
    postgres_handle = PostgresHandle(smarttypes.connection_string)
    network = load_network_from_the_db(postgres_handle, 5)
    similarity_matrix = mk_similarity_matrix(network)
    #communities = cluster_w_mcl(network, similarity_matrix)
    communities = cluster_w_else(network, similarity_matrix)
    for community_idx, member_ids in communities.items():
        print "community: %s -- members: %s" % (community_idx, len(member_ids))
        print_user_details(member_ids, postgres_handle)
        print ""


