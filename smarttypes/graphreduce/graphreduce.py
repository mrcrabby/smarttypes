
import copy
import numpy as np
#from cogent.cluster.approximate_mds import nystrom
from scipy.spatial import distance
from sklearn.cluster import DBSCAN
from collections import OrderedDict
import numpy.random as nprnd

import smarttypes
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.utils.postgres_handle import PostgresHandle
postgres_handle = PostgresHandle(smarttypes.connection_string)


def load_network_from_the_db():
  network = OrderedDict()
  def add_user_to_network(user):
    network[user.id] = {}
    network[user.id]['following_ids'] = set(user.following_ids)
    network[user.id]['following_count'] = user.following_count
    network[user.id]['followers_count'] = user.followers_count
  twitter_user = TwitterUser.by_screen_name('SmartTypes')
  add_user_to_network(twitter_user)
  for following in twitter_user.following:
    add_user_to_network(twitter_user)
  return network

def get_landmarks(network, num_of_landmarks=50):
  """
  figure out how to pick good landmarks
  """
  node_ids = np.array(network.keys())
  random_idxs = nprnd.randint(len(network), size=num_of_landmarks)
  return node_ids[random_idxs]

def mk_similarity_matrix(network, landmarks):
  """
  similarity_matrix is len(network) x len(landmarks)
  """
  similarity_matrix = []
  for landmark_id in landmarks:
    landmark_node = network[landmark_id]
    landmark_similarities = []
    for node_id, node in network.items():
      adamic_score = 0
      following_intersect = node['following_ids'].intersection(landmark_node['following_ids'])
      for intersect_id in following_intersect:
        intersect_node = network.get(intersect_id)
        if intersect_node:
          adamic_score += (1/log(intersect_node['followers_count']))
      landmark_similarities.append(adamic_score)
    similarity_matrix.append(landmark_similarities)
  similarity_matrix = np.array(similarity_matrix)
  return similarity_matrix

def reduce_similarity_matrix(similarity_matrix):
  graph_reduction = nystrom(similarity_matrix, 2)

def normalize_similarity_matrix(similarity_matrix):
  similarity_matrix = 1 - (similarity_matrix / np.max(similarity_matrix))
  return similarity_matrix

def get_square_distance_matrix(similarity_matrix):
  return distance.squareform(distance.pdist(similarity_matrix, 'euclidean'))

def identify_communities(similarity_matrix, eps=0.42, min_samples=12):
  db = DBSCAN().fit(S, eps=eps, min_samples=min_samples)
  #db.labels_
  print len(set(self.groups)) - (1 if -1 in self.groups else 0)


if __name__ == "__main__":

  network = load_network_from_the_db()
  landmarks = get_landmarks(network, 50)
  similarity_matrix = mk_similarity_matrix(network, landmarks)
  similarity_matrix = normalize_similarity_matrix(similarity_matrix)
  similarity_matrix = get_square_distance_matrix(similarity_matrix)
  identify_communities(similarity_matrix)











