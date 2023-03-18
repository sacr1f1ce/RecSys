import numpy as np
import json
import os
import sys


os.chdir(sys.path[0])

item_matrix = np.load('item_matrix.npy', allow_pickle=True)
item_id = np.load('itemid.npy', allow_pickle=True)
wts = np.load('weights.npy', allow_pickle=True)
popular = np.load('popular.npy', allow_pickle=True)

f = open('anime_id2name.json')

id2name = json.load(f)
f.close


popular_id = [20, 269, 22319, 6702, 1535, 30, 199, 1575, 523, 33, 16498, 30276, 5114, 11757, 31964, 11061, 1, 28223, 11111, 3588, 813,18679, 13601, 34572, 29803, 33352, 35120]
popular_row = [np.where(item_id == i)[0][0] for i in popular_id]