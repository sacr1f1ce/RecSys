import numpy as np

from lightfm import LightFM
from lightfm.data import Dataset
from df import *


dataset = Dataset()
all_user_features = sorted(set(data_users['gender']) | set(data_users['age_group']))

dataset.fit(data_interactions['userid'], 
            data_interactions['movieid'], 
            item_features=None,
            user_features=all_user_features)

user_features = dataset.build_user_features(data_users.user_features)
interactions, weights = dataset.build_interactions(data_interactions.iloc[:, 0:3].values)
model = LightFM(loss='warp')
model.fit(interactions=interactions,
           user_features=user_features,
           item_features=None,
           epochs=5,
           sample_weight=weights);

user_id_map, user_feature_map, item_id_map, item_feature_map = dataset.mapping()

user_x = user_id_map[2255153]
n_users, n_items = interactions.shape
model.predict(user_x, np.arange(n_items)) 