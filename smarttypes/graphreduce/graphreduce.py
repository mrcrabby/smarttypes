import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse import cs_graph_components

"""
Our goal is to reduce a social graph to 2 dimensions

We want to produce a bunch of tiled images to use w/ 
http://polymaps.org/

Here's how this is broken down:
- Step 1: Pull network into memory:

  http://docs.scipy.org/doc/scipy/reference/tutorial/csgraph.html

  (search for 'Computing the adjacency matrix')
  http://scikit-learn.org/dev/_downloads/wikipedia_principal_eigenvector.py

  http://etudiant.istic.univ-rennes1.fr/current/m2mitic/AMI/src/scikits.learn-0.6/scikits/learn/cluster/spectral.py

  http://etudiant.istic.univ-rennes1.fr/current/m2mitic/AMI/src/scikits.learn-0.6/scikits/learn/utils/graph.py

  http://www.sagemath.org/doc/reference/sage/graphs/digraph.html

- Step 2: Randomly pick landmarks for Landmark MDS

- Step 3: Use custom similarity measure (like Jaccard's) to compare every
  node to every landmark, results in len(network) x len(landmarks)
  matrix

- Step 4: Do landmark MDS, and print the difference between 2d reduction
  and similarity matrix

- Step 5: Load reduction into postgis

- Step 7: Community detection

- Step 8: Pagerank within communities

- Step 7: Use reduction, community, and pagerank to make nice 
  tiled images w/ ggplot2 
"""

def make_sparse_adjanceny_matrix(network):
    sorted_keys = sorted(network.keys())
    number_of_users = len(sorted_keys)
    counter = 0
    list_of_lists = []
    for user in sorted_keys:
        following_list = []
        for maybe_following in sorted_keys:
            if maybe_following in network[user]:
                following_list.append(1)
            else:
                following_list.append(0)
        list_of_lists.append(following_list)
        counter += 1
        if counter % 1000 == 0:
            print '%s of %s users processed' % (counter, number_of_users)
    sparse_matrix = lil_matrix(list_of_lists)
    del list_of_lists
    sparse_matrix = sparse_matrix.tocsr()
    N_components, component_list = cs_graph_components(sparse_matrix)
    print N_components
    return sparse_matrix


def make_similarity_matrix_file(adjanceny_matrix_file):
    """"""

def make_reduction_file(similarity_matrix_file):
    """"""

def compare_similarity_to_reduction(similarity_matrix_file, reduction_file):
    """"""

def save_reduction_to_postgis(reduction_file, postgres_handle):
    """"""

def make_tiled_images(postgres_handle):
    """"""

