
import os
from collections import defaultdict
import numpy as np
from scipy.spatial import distance

"""
Our goal is to reduce a social graph to 2 dimensions

We want to produce a bunch of tiled images to use w/ 
http://polymaps.org/

Here's how this is broken down:
- Step 1: Pull network info from the db, and write to an 
  adjanceny_matrix_file

- Step 2: Use adjanceny_matrix_file to make a 
  similarity_matrix_file

- Step 3: Use similarity_matrix_file to make a reduction_file

- Step 4: Compare similarity_to_reduction 

- Step 5: Load reduction into postgis

- Step 6: Use reduction info in postgis to make tiled images 
  for polymaps display
"""

def make_adjanceny_matrix_file(network):
    """"""

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








