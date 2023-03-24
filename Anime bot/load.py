import numpy as np
import json
import os
import sys
from utils import map_ind

os.chdir(sys.path[0] + '/data')

item_matrix = np.load('item_matrix.npy', allow_pickle=True)
item_id = np.load('itemid.npy', allow_pickle=True)
wts = np.load('weights.npy', allow_pickle=True)
popular = np.load('popular.npy', allow_pickle=True)
item_bias = np.load('item_bias.npy', allow_pickle=True)
item_factors = np.load('item_factors.npy', allow_pickle=True)
item_factors_inv = np.load('item_factors_inv.npy', allow_pickle=True)

f = open('anime_id2anime_name.json')
g = open('anime_name2anime_id.json')
l = open('anime_id2row.json')

id2name = json.load(f)
name2id = json.load(g)
anime_id2row = json.load(l)
f.close, g.close, l.close

popular_id = [20, 269, 22319, 6702, 1535, 30, 199, 1575, 523, 33, 16498, 30276, 5114, 11757, 31964, 11061, 1, 28223, 11111, 3588, 813,18679, 13601, 34572, 29803, 33352]
popular_row = map_ind(popular_id, item_id) #so ugly


row2anime_id = {}
for id_ in anime_id2row.keys():
    row2anime_id[anime_id2row[id_]] = id_