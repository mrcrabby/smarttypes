
import smarttypes, sys, os, random
import numpy as np
from collections import OrderedDict
from scipy import spatial

def make_a_move(i, good, bad, me):

    #goal_to_good_dist = 100 - (i * 2)
    good_to_bad_diff = good - bad 
    #goal_to_good_dist goes down as good_to_bad_diff goes up
    goal_to_good_dist = 100 - (i * 2)

    good_to_bad_dist = np.linalg.norm(good_to_bad_diff)
    good_to_bad_x_ratio = good_to_bad_diff[0] / good_to_bad_dist 
    good_to_bad_y_ratio = good_to_bad_diff[1] / good_to_bad_dist 

    goal_to_bad_dist = good_to_bad_dist + goal_to_good_dist
    goal_to_bad_x_dist = goal_to_bad_dist * good_to_bad_x_ratio
    goal_to_bad_y_dist = goal_to_bad_dist * good_to_bad_y_ratio
    goal_x = good[0] + (goal_to_bad_x_dist - good_to_bad_diff[0])
    goal_y = good[1] + (goal_to_bad_y_dist - good_to_bad_diff[1])
    goal = np.array((goal_x, goal_y))

    new_x = (goal[0] + me[0]) * 0.50
    new_y = (goal[1] + me[1]) * 0.50
    return (new_x, new_y)

def figure_out_everyones_next_move(i, g, coordinates_as_dict, coordinates_as_numpy_array):
    """
    avg_position_of_all_nodes
    avg_position_of_followie_nodes
    """
    avg_position_of_all_nodes = np.median(coordinates_as_numpy_array, 0)
    new_coordinates_as_dict = OrderedDict()
    avg_distance_to_connected_nodes = []
    for vertex in g.vs:
        node_id = vertex['name']
        my_coordinate = np.array(coordinates_as_dict[node_id])
        followie_coordinates = []
        for successor in vertex.successors():
            followie_id = successor['name']
            followie_coordinates.append(coordinates_as_dict[followie_id])
        followie_coordinates = np.array(followie_coordinates)
        avg_position_of_followie_nodes = np.median(followie_coordinates, 0)
        avg_distance_to_connected_nodes.append(np.linalg.norm(my_coordinate - avg_position_of_followie_nodes))
        new_coordinates_as_dict[node_id] = make_a_move(i, avg_position_of_followie_nodes, 
            avg_position_of_all_nodes, my_coordinate)
    return new_coordinates_as_dict, np.array(avg_distance_to_connected_nodes)

def how_are_we_doing_compared_to_our_objective(avg_distance_to_connected_nodes, 
    coordinates_as_numpy_array):

    """
    avg_distance_to_connected_nodes / avg_distance_between_all_nodes
    """
    mean_connected_distance = np.mean(avg_distance_to_connected_nodes)
    print 'avg_distance_to_connected_nodes: %s' % mean_connected_distance
    all_distance = spatial.distance.squareform(spatial.distance.pdist(
        coordinates_as_numpy_array))
    mean_all_distance = np.mean(all_distance)
    print 'avg_distance_of_all_nodes: %s' % mean_all_distance
    print 'all together: %s' % (mean_connected_distance / mean_all_distance)

def reduce_with_semi_intelligent_agents(g):
    #randomly assign coordinates
    coordinates_as_dict = OrderedDict()
    for vertex in g.vs:
        node_id = vertex['name']
        x = random.random() * 100
        y = random.random() * 100
        coordinates_as_dict[node_id] = (x, y)
    coordinates_as_numpy_array = np.array(coordinates_as_dict.values())

    for i in range(40):
        print i

        coordinates_as_dict, avg_distance_to_connected_nodes = figure_out_everyones_next_move(
            i, g, coordinates_as_dict, coordinates_as_numpy_array)

        #do this before we overwrite coordinates_as_numpy_array
        #doing this to save computation (this way we can use 
        #figure_out_everyones_next_move to get avg_distance_to_connected_nodes)
        how_are_we_doing_compared_to_our_objective(avg_distance_to_connected_nodes, 
            coordinates_as_numpy_array)

        coordinates_as_numpy_array = np.array(coordinates_as_dict.values())

    return coordinates_as_numpy_array





