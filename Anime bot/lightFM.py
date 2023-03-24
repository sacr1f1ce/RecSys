import numpy as np
import scipy

from lightfm import LightFM
from lightfm.data import Dataset
from df import *
from load import item_factors, item_factors_inv, item_bias
from model_params import *


dataset = Dataset()
all_user_features = sorted(set(data_users['gender']) | set(data_users['age_group']))

dataset.fit(data_interactions['userid'], 
            data_items['anime_id'], 
            item_features=all_item_features,
            user_features=all_user_features)

user_features = dataset.build_user_features(data_users.user_features)
item_features = dataset.build_item_features(data_items.item_features)

interactions, weights = dataset.build_interactions(data_interactions.iloc[:, 0:3].values)

model = LightFM(
    loss='warp',
    no_components=NO_COMPONENTS,
    k = 5,
    learning_rate=LEARNING_RATE,
    item_alpha = ITEM_ALPHA,
    user_alpha = USER_ALPHA,
    random_state=np.random.RandomState(SEED)
)

model.fit(interactions=interactions,
           user_features=user_features,
           item_features=item_features,
           epochs=5,
           sample_weight=weights);


mat = [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]


def cold_start(features):
    mat = np.zeros((1, 6668))
    mat[0, -len(features):] = features
    us_feat = scipy.sparse.csr_matrix(mat)

    test_users = np.arange(1, dtype='i4')
    all_items= np.arange(data_interactions.movieid.nunique(), dtype='i4')
    user_index, item_index = np.meshgrid(test_users, all_items, copy=False)
    lfm_scores = model.predict(
        user_ids = user_index.ravel(),
        item_ids = item_index.ravel(),
        item_features = item_features,
        user_features = us_feat
    )
    return lfm_scores.reshape(len(test_users), len(all_items), order='F')