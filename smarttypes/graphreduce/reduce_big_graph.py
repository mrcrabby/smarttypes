
import smarttypes, sys, os, random
import numpy as np
from collections import OrderedDict


def figure_out_everyones_next_move(network, coordinates_as_dict, coordinates_as_numpy_array):

    """
    avg_position_of_all_nodes
    avg_position_of_followie_nodes
    """
    avg_position_of_all_nodes = np.mean(coordinates_as_numpy_array, 0)

    new_coordinates_as_dict = OrderedDict()
    for node_id in network:
        followie_coordinates = []
        for followie_id in network[node_id]:
            followie_coordinates.append(coordinates_as_dict[followie_id])
        followie_coordinates = np.array(followie_coordinates)
        avg_position_of_followie_nodes = np.mean(followie_coordinates, 0)
        #make a move
        

    return new_coordinates_as_dict


def how_are_we_doing_compared_to_our_objective(network, coordinates_as_dict, coordinates_as_numpy_array):

    """
    avg_distance_of_connected_nodes / avg_distance_of_all_nodes
    """


def reduce_with_semi_intelligent_agents(network):
    #network is an ordereddict

    #randomly assign coordinates
    coordinates_as_dict = OrderedDict()
    for node_id in network:
        x = random.random() * 100
        y = random.random() * 100
        coordinates_as_dict[node_id] = (x, y)
    coordinates_as_numpy_array = np.array(coordinates_as_dict.values())

    for i in range(10):
        coordinates_as_dict = figure_out_everyones_next_move(network, coordinates_as_dict, 
            coordinates_as_numpy_array)
        coordinates_as_numpy_array = np.array(coordinates_as_dict.values())

    return coordinates_as_numpy_array





