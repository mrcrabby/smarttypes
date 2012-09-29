
"""
utilize postgis bounding box idx to iterate over 
& find the best reduction
"""

"""
this could easily be spread across machines

assume a fixed world (we'll assume [-180, -80], [180, 80])

if starting from scratch take a rough first crack @ intelligently 
placing nodes

first use igraph to run pagerank and other network stats

then divide the world in discrete chunks, and iterate over nodes in 
those chunks

here's the data each node needs:

- avg followie location
- avg follower location
- avg opposite location


"""



