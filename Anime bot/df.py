import pandas as pd
import numpy as np


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

#data_items = df_items[['anime_id', 'new_title', 'type', 'source', 'score', 
   #                    'scored_by', 'rank', 'popularity', 'members', 'favorites', 'genre']]

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