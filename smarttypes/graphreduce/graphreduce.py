
import copy, csv, os
import numpy as np
from cogent.cluster.nmds import NMDS
from cogent.cluster.approximate_mds import nystrom
from cogent.maths.distance_transform import dist_euclidean
from sklearn.cluster import DBSCAN, KMeans, Ward
from collections import OrderedDict
import numpy.random as nprnd
from scipy.stats import describe
from scipy.stats import scoreatpercentile

import smarttypes
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.utils.postgres_handle import PostgresHandle

def summary_stats(a):
  #use this instead: describe
  print "max: %s, min: %s, mean: %s, std: %s" % (
    np.max(a), np.min(a), np.mean(a), np.std(a))

def load_network_from_the_db(postgres_handle, distance):
  network = OrderedDict()
  def add_user_to_network(user):
    network[user.id] = {}
    network[user.id]['following_ids'] = set(user.following_ids)
    #network[user.id]['following_ids'].add(user.id)
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

def reduce_with_linloglayout(network):
    input_file = open('io/graph_reduction_input.csv', 'w') 
    for node_id in network:
        for following_id in network[node_id]['following_ids']:
            if following_id in network:
              input_file.write('%s %s \n' % (node_id, following_id))
    input_file.close()
    #to recompile
    #$ cd smarttypes/smarttypes/graphreduce/LinLogLayout/src/
    #$ javac -d ../bin LinLogLayout.java
    os.system('cd LinLogLayout; java -cp bin LinLogLayout 2 %s %s;' % (
        '../io/graph_reduction_input.csv',
        '../io/graph_reduction_output.csv'
    ))

def load_linlog_reduction_from_file():
    communities = OrderedDict()
    f = open('io/graph_reduction_output.csv')
    graph_reduction = []
    for line in f:
        line_pieces = line.split(' ')
        node_id = line_pieces[0]
        x_value = float(line_pieces[1])
        y_value = float(line_pieces[2])
        graph_reduction.append([x_value, y_value])
        group_num = int(line_pieces[4])
        if group_num in communities:
          communities[group_num].append(node_id)
        else:
          communities[group_num] = [node_id]
    return np.array(graph_reduction), communities

def store_follower_ids(network):
  for user_id in network:
    for following_id in network[user_id]['following_ids']:
      if following_id in network:
        network[following_id]['follower_ids'].add(user_id)

def get_landmarks(network):
  """
  figure out how to pick good landmarks
  """
  node_ids = np.array(network.keys())
  return node_ids
  # num_of_landmarks = len(node_ids) / 4
  # random_idxs = nprnd.randint(len(network), size=num_of_landmarks)
  # return node_ids[random_idxs]

def mk_similarity_matrix(network, landmarks):
  """
  similarity_matrix is len(network) x len(landmarks)
  """

  #where the magic happens
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
          return 0
    return total_score

  similarity_matrix = []
  for node_id, node in network.items():

    landmark_similarities = []
    for landmark_id in landmarks:
      total_score = 0.0
      landmark_node = network[landmark_id]
      following_intersect = node['following_ids'].intersection(landmark_node['following_ids'])
      follower_intersect = node['follower_ids'].intersection(landmark_node['follower_ids'])
      total_score += (scoring_function(following_intersect, 'followers_count') * 1)
      total_score += (scoring_function(follower_intersect, 'following_count') * .75)
      # following_difference = node['following_ids'].symmetric_difference(landmark_node['following_ids'])
      # len_following_difference = len(following_difference)
      # if len_following_difference == 0:
      #   len_following_difference = 2
      landmark_similarities.append(total_score)
    similarity_matrix.append(landmark_similarities)
  similarity_matrix = np.array(similarity_matrix)

  # #clean up some loose ends + normalize
  # floor = scoreatpercentile(similarity_matrix, 20)[1]
  # ceiling = scoreatpercentile(similarity_matrix, 80)[1]
  # print floor, ceiling
  # #similarity_matrix[similarity_matrix < floor] = floor
  # similarity_matrix[similarity_matrix > ceiling] = ceiling
  # similarity_matrix = similarity_matrix / ceiling
  return similarity_matrix

def write_similarity_matrix_to_csv(similarity_matrix):
  similarity_matrix_file = open('io/similarity_matrix.csv', 'w')  
  writer = csv.writer(similarity_matrix_file)
  for row in similarity_matrix:
    writer.writerow(row)

def reduce_similarity_matrix(similarity_matrix):
  #distance_matrix = dist_euclidean(similarity_matrix)
  distance_matrix = 1 - similarity_matrix
  return NMDS(distance_matrix).getPoints()
  # distance_matrix = 1 - similarity_matrix
  # return nystrom(distance_matrix.T, 2)

def write_reduction_to_csv(network, graph_reduction):
  graph_reduction_file = open('io/graph_reduction.csv', 'w')  
  writer = csv.writer(graph_reduction_file)
  writer.writerow(['node_id', 'x_coordinate', 'y_coordinate'])
  for i in range(len(network)):
    node_id = network.keys()[i]
    x_y = list(graph_reduction[i])
    writer.writerow([node_id] + x_y)

def identify_communities(number_of_communities, similarity_matrix, node_ids):
  raw_communities = Ward(n_clusters=number_of_communities).fit(similarity_matrix).labels_
  #raw_communities = KMeans(k=number_of_communities).fit(similarity_matrix).labels_
  #raw_communities = DBSCAN().fit(similarity_matrix, eps=eps, min_samples=min_samples).labels_
  num_communities = len(set(raw_communities)) - (1 if -1 in raw_communities else 0)
  communities = OrderedDict([(x,[]) for x in range(num_communities)])
  for i in range(len(node_ids)):
    community_idx = raw_communities[i]
    if community_idx != -1:
      communities[community_idx].append(node_ids[i])
  return communities

def print_user_details(user_ids, postgres_handle):
  for user in TwitterUser.get_by_ids(user_ids, postgres_handle):
    print "%s -- %s" % (user.screen_name, 
      user.description[:100].replace('\n', ' ') if user.description else '')

def do_linlog_reduction():
  postgres_handle = PostgresHandle(smarttypes.connection_string)
  network = load_network_from_the_db(postgres_handle, 5)
  reduce_with_linloglayout(network)
  graph_reduction, communities = load_linlog_reduction_from_file()
  write_reduction_to_csv(network, graph_reduction)

def write_distance_matrix_to_csv():
  postgres_handle = PostgresHandle(smarttypes.connection_string)
  network = load_network_from_the_db(postgres_handle, 5)
  landmarks = get_landmarks(network)
  similarity_matrix = mk_similarity_matrix(network, landmarks)
  distance_matrix = dist_euclidean(similarity_matrix)
  write_similarity_matrix_to_csv(distance_matrix)

if __name__ == "__main__":

  #do_linlog_reduction()
  write_distance_matrix_to_csv()

  # # #reduce
  # # graph_reduction = reduce_similarity_matrix(similarity_matrix)

  # #communities
  # communities = identify_communities(20, similarity_matrix, network.keys())
  # #communities = identify_communities(20, graph_reduction, network.keys())
  # print "%s communities" % len(communities)
  # for community_idx, member_ids in communities.items():
  #   print "community: %s" % community_idx
  #   print_user_details(member_ids, postgres_handle)
  #   print ""

  # #test similarity_matrix
  # twitter_user = TwitterUser.by_screen_name('SmartTypes', postgres_handle)
  # similarity_matrix_idx = get_similarity_matrix_idx_for_user(similarity_matrix, network, twitter_user.id)
  # results = get_users_ordered_by_similarity(similarity_matrix, network, similarity_matrix_idx, postgres_handle)
  # for result in results[:20]:
  #   print result[0], result[1].screen_name, result[1].description[:100]

  ##test distance_matrix
  # print "-------------------"
  # distance_matrix = get_square_distance_matrix(similarity_matrix)
  # results = get_users_ordered_by_similarity(distance_matrix, network, similarity_matrix_idx, postgres_handle, reverse=False)
  # for result in results[:20]:
  #   print result[0], result[1].screen_name, result[1].description[:100]













"""
##may need this:

def get_similarity_matrix_idx_for_user(similarity_matrix, network, for_this_user_id):
  for i in range(len(network)):
    if network.keys()[i] == for_this_user_id:
      return i
  return -1

def get_users_ordered_by_similarity(similarity_matrix, network, similarity_matrix_idx, postgres_handle, reverse=True):
  results = []
  for i in range(len(network)):
    similarity_score = similarity_matrix[similarity_matrix_idx][i]
    user = TwitterUser.get_by_id(network.keys()[i], postgres_handle)
    results.append((similarity_score, user))
  return sorted(results, reverse=reverse)


"""

