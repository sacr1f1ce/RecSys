import pandas as pd
import numpy as np
import itertools
import os
import sys
os.chdir(sys.path[0] + '/data')

df = pd.read_csv('animelists_cleaned.csv')
df_users = pd.read_csv('users_cleaned.csv')
df_items = pd.read_csv('anime_cleaned.csv')

username2userid = df_users.set_index('username').to_dict()['user_id']
df['userid'] = df['username'].apply(lambda x: username2userid[x])

titles = df_items.title.values
english_titles = df_items.title_english.fillna('00000').values
for i in range(len(english_titles)):
    if english_titles[i] == '00000':
        english_titles[i] = titles[i]
df_items['new_title'] = english_titles

data_items = df_items[['anime_id', 'new_title', 'type', 'source',  'score',
                        'scored_by', 'members', 'favorites', 'genre']]
data_items.genre.fillna('Unknown', inplace=True)
data_items['type'] = data_items.type.apply(lambda x: 'type' + x)
data_items['source'] = data_items.source.apply(lambda x: 'source' + x)
data_items['score'] = data_items.score.apply(lambda x: 'score' + str(int(x)))
data_items['scored_by'] = data_items.scored_by.apply(lambda x: 'scored_by' + str(x // 100000))
data_items['members'] = data_items.members.apply(lambda x: 'members' + str(x // 100000))
data_items['favorites'] = data_items.favorites.apply(lambda x: 'favorites' + str(x // 10000))
data_items['genre'] = data_items.genre.apply(lambda x: x.split(', '))
all_item_features = []
for col in ['type', 'source', 'score', 'scored_by', 'members', 'favorites']:
    all_item_features += sorted(data_items[col].unique())
all_item_features += sorted(set(itertools.chain.from_iterable(data_items.genre)))

data_items['item_features'] = list(
    zip(
        data_items['anime_id'], 
        list(
            zip(data_items['type'], 
                data_items['source'], 
                data_items['score'], 
                data_items['scored_by'], 
                data_items['members'], 
                data_items['favorites'], 
                data_items['genre'])
        )
    )
)

data_items['item_features'] = data_items.item_features.apply(
    lambda x: (x[0], [x[1][0], x[1][1], x[1][2], x[1][3], x[1][4], x[1][5]] + x[1][6])
)

data_users = df_users[['username', 'user_id', 'gender', 'birth_date']]

data_interactions = df[
    [
    'userid',
    'anime_id',
    'my_score', 
    'my_last_updated'
    ]].rename(
    columns={
    "userid": "userid",
    "anime_id": "movieid",
    'my_last_updated':'timestamp',
    'my_score':'rating'
    }
)

data_interactions = data_interactions.loc[data_interactions.rating > 0]

shared_ids = np.intersect1d(data_users.user_id, data_interactions.userid)
data_users = data_users[data_users.user_id.isin(shared_ids)]
data_interactions = data_interactions[data_interactions.userid.isin(shared_ids)]

data_users['age'] = data_users.birth_date.apply(lambda x: 2023 - int(x[:4]))
data_users['age_group'] = pd.cut(data_users['age'], 10)

age2num = {}
for i, age in enumerate(data_users.age_group.unique()):
    age2num[age] = str(i)
data_users['age_group'] = data_users['age_group'].apply(lambda x: age2num[x])

data_users['user_features'] = list(
    zip(
    data_users['user_id'],
    data_users['age_group'],
    data_users['gender']
    )
)

data_users['user_features'] = data_users.user_features.apply(lambda x: (x[0], [x[1], x[2]]))