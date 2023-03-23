import numpy as np
import json
import telebot
from telebot import types

from utils import *
from load import *
#from lightFM import *
from search import *


M = item_matrix @ item_matrix.T

ratings = {}
request_user = {}
search_user = {}

API_TOKEN = '5677096457:AAHYpRxfaCw9WnJjRybbF-igrxK3XAe3cXo'
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['reset'])
def echo_message(message):
    name = message.from_user.username
    ratings.pop(name, None)
    request_user.pop(name, None)
    bot.send_message(
        message.chat.id, 
        text='Your information has been cleared'
    )
    

# @bot.message_handler(commands=['fm_test'])
# def echo_message(message):
#     keyboard = types.InlineKeyboardMarkup()
#     keys = []
#     keys.append(types.InlineKeyboardButton(text='Male', callback_data='male'))
#     keys.append(types.InlineKeyboardButton(text='Female', callback_data='female'))
#     keys.append(types.InlineKeyboardButton(text='Non-Binary', callback_data='nonbin'))
#     keyboard.add(*keys)
#     bot.send_message(
#         message.chat.id, 
#         text='Please select your gender', 
#         reply_markup=keyboard
#     )


@bot.message_handler(commands=['suggest'])
def echo_message(message):
    name = message.from_user.username
    if name not in ratings:
        bot.send_message(message.chat.id,
                             text=f'Not enough info')
    else:
        p = np.zeros(M.shape[-1])
        #print(ratings[name])
        for anime_id, score in ratings[name].items():
            p[anime_id] = score
        recs = M @ p
        recs = downvote_seen_items(recs, ratings[name].keys())
        for id_ in topn_recommendations(recs):
            bot.send_message(message.chat.id,
                             text=f'Consider {id2name[str(item_id[id_])]}')
        
            
@bot.message_handler(commands=['rate'])
def echo_message(message):
    name = message.from_user.username
    if name not in ratings:
        ratings[name] = {}
    keyboard = types.InlineKeyboardMarkup()
    keys = []
    keys.append(types.InlineKeyboardButton(text='Popular', callback_data='Popular'))
    keys.append(types.InlineKeyboardButton(text='Search', callback_data='Search'))
    keyboard.add(*keys)
    bot.send_message(
        message.chat.id, 
        text='You can either rate some of the popular anime or search a specific one', 
        reply_markup=keyboard
    )
    

@bot.message_handler(content_types=['text'])
def process_name(message):
    name = message.from_user.username
    if name in search_user and search_user[name]:
        search_res = search(message.text)
        anime_id = map_ind([search_res], item_id)[0]
        request_user[name] = anime_id

        keyboard = types.InlineKeyboardMarkup()
        keys = []
        for i in range(1, 11):
            keys.append(types.InlineKeyboardButton(text=f'{i}', callback_data=i))
        keys.append(types.InlineKeyboardButton(text='Did not watch', callback_data=-1))
        keyboard.add(*keys)

        bot.send_message(
            message.chat.id, 
            text=f'Please rate {id2name[str(item_id[anime_id])]}', 
            reply_markup=keyboard
            )


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    name = call.from_user.username
    if call.data in ['male', 'female', 'nonbin']:
        user_x = user_id_map[2255153]
        n_users, n_items = interactions.shape # no of users * no of items
        scores = model.predict(user_x, np.arange(n_items)) # means predict for all
        for id_ in topn_recommendations(scores, topn=5):
            bot.send_message(call.message.chat.id,
                             text=f'Consider {id2name[str(item_id[id_])]}')
    elif call.data == 'Search':
        bot.send_message(call.message.chat.id,
                             text=f'Please give me the name of anime you would like to rate')
        search_user[call.from_user.username] = True
    elif call.data == 'Popular':
        anime_id = popular_row[len(ratings[name])] 
        request_user[name] = anime_id 

        keyboard = types.InlineKeyboardMarkup()
        keys = []
        for i in range(1, 11):
            keys.append(types.InlineKeyboardButton(text=f'{i}', callback_data=i))
        keys.append(types.InlineKeyboardButton(text='Did not watch', callback_data=-1))
        keyboard.add(*keys)

        bot.send_message(
            call.message.chat.id, 
            text=f'Please rate {id2name[str(item_id[anime_id])]}', 
            reply_markup=keyboard
            )

    else:
        response = int(call.data)
        if response > 0:
            ratings[name][request_user[name]] = response
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, 
                                text=f'{id2name[str(item_id[request_user[name]])]}: {response}')
        else:
            ratings[name][request_user[name]] = 0
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)

    


bot.polling()