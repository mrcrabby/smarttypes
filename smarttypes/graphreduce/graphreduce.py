
import np
from cogent.cluster.approximate_mds import nystrom
from scipy.spatial import distance
from sklearn.cluster import DBSCAN
from collections import OrderedDict

def load_network_from_the_db():
  """
  network is an ordereddict of nodes:

  {
    '12345':node,
    }

  a node is a dict that looks like this:

  {
    'id':'', 
    'following_count':0,
    'followers_count':0,
    'following_ids':set([]),
    'x_dim':0,
    'y_dim':0,
    }
  """
  OrderedDict

def get_landmarks(network):
  """
  if the network has been reduced pick landmarks via reduction
  otherwise pick randomly
  """

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
      following_intersect = intersect(node['following_ids'], landmark_node['following_ids'])
      for intersect_id in following_intersect:
        intersect_node = network.get(intersect_id)
        if intersect_node:
          adamic_score += (1/log(intersect_node['followers_count']))
      landmark_similarities.append(adamic_score)
    similarity_matrix.append(landmark_similarities)
  similarity_matrix = np.array(similarity_matrix)
  return similarity_matrix

def normalize_similarity_matrix():
  """

  """

def reduce_similarity_matrix(similarity_matrix):
  """

  """
  graph_reduction = nystrom(similarity_matrix, 2)


def identify_communities(graph_reduction):


  # self.reduction_distances = distance.squareform(distance.pdist(self.reduction, 'euclidean'))
  # def find_dbscan_groups(self, eps=0.42, min_samples=12):
  #     self.figure_out_reduction_distances()
  #     S = 1 - (self.reduction_distances / np.max(self.reduction_distances))
  #     db = DBSCAN().fit(S, eps=eps, min_samples=min_samples)
  #     self.groups = db.labels_
  #     self.n_groups = len(set(self.groups)) - (1 if -1 in self.groups else 0)












