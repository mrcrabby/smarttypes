
import os, csv
from collections import defaultdict
import numpy as np
from scipy.spatial import distance

"""
Our goal is to reduce a social graph to 2 dimensions

We want to produce a bunch of tiled images to use w/ 
http://polymaps.org/

Here's how this is broken down:
- Step 1: Pull network into memory, looks like this:

  {'id':set['id', 'id'], ...}

- Step 2: Randomly pick landmarks for Landmark MDS

- Step 3: Use custom similarity measure (like Jaccard's) to compare every
  node to every landmark, results in len(network) x len(landmarks)
  matrix

- Step 4: Landmark MDS, and print the difference between 2d reduction
  and similarity meaures

- Step 5: Load reduction into postgis

- Step 7: Community detection

- Step 8: Pagerank within communities

- Step 7: Use reduction, community, and pagerank to make nice 
  tiled images w/ ggplot2 
"""

def make_adjanceny_matrix_file(network, adjanceny_matrix_file):
    sorted_keys = sorted(network.keys())
    number_of_users = len(sorted_keys)
    writer = csv.writer(adjanceny_matrix_file)
    writer.writerow(sorted_keys)
    counter = 0
    for user in sorted_keys:
        following_list = []
        for maybe_following in sorted_keys:
        	if maybe_following in network[user]:
        		following_list.append(1)
        	else:
        		following_list.append(0)
        writer.writerow(following_list)
        counter += 1
        if counter % 1000 == 0:
        	print '%s of %s users processed' % (counter, number_of_users)


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








