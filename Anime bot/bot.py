import numpy as np
import json
import telebot
from telebot import types

from utils import *
from load import *
from lightFM_warmstart import *
from lightFM import *
from search import *

import warnings
warnings.filterwarnings("ignore")


M = item_matrix @ item_matrix.T

ratings = {}
request_user = {}
search_user = {}
user_feats = {}

gender2pos = {'female':0, 'male':1, 'nonbin':2}

API_TOKEN = '5677096457:AAHYpRxfaCw9WnJjRybbF-igrxK3XAe3cXo'
bot = telebot.TeleBot(API_TOKEN)

commands = [
    types.BotCommand('rate', 'Share your ratings'),
    types.BotCommand('suggest', 'Get recommendations'),
    types.BotCommand('suggest_fm', 'Get recommendations with lightFM'),
    types.BotCommand('cold_start', 'Input your data and get recommendations'),
    types.BotCommand('reset', 'Clear your data')

]

bot.set_my_commands(commands)

@bot.message_handler(commands=['reset'])
def reset_msg(message):
    name = message.from_user.username
    ratings.pop(name, None)
    request_user.pop(name, None)
    user_feats.pop(name, None)
    bot.send_message(
        message.chat.id, 
        text='Your information has been cleared'
    )


@bot.message_handler(commands=['cold_start'])
def cold_start_msg(message):
    name = message.from_user.username
    if name not in user_feats:
        user_feats[name] = np.zeros(13)
    keyboard = types.InlineKeyboardMarkup()
    keys = []
    keys.append(types.InlineKeyboardButton(text='Male', callback_data='male'))
    keys.append(types.InlineKeyboardButton(text='Female', callback_data='female'))
    keys.append(types.InlineKeyboardButton(text='Non-Binary', callback_data='nonbin'))
    keyboard.add(*keys)
    bot.send_message(
        message.chat.id, 
        text='Please select your gender', 
        reply_markup=keyboard
    )
    

@bot.message_handler(commands=['start'])
def start_msg(message):
    bot.send_message(
        message.chat.id, 
        text='Hi, please use one of the commands.')


@bot.message_handler(commands=['suggest'])
def suggest_msg(message):
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
            

@bot.message_handler(commands=['suggest_fm'])
def suggest_fm_msg(message):
    name = message.from_user.username
    if name not in ratings:
        bot.send_message(message.chat.id,
                             text=f'Not enough info')
    else:
        p = np.zeros(item_factors.shape[0])
        for anime_id, score in ratings[name].items():
            p[anime_id] = score
        recs = warm_start(p)
        recs = downvote_seen_items(recs, ratings[name].keys())
        for id_ in topn_recommendations(recs):
            bot.send_message(message.chat.id,
                             text=f'Consider {id2name[str(row2anime_id[id_])]}')
        
            
@bot.message_handler(commands=['rate'])
def rate_msg(message):
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
    print('INTERACTION')
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
        user_feats[name][gender2pos[call.data]] = 1
        keyboard = types.InlineKeyboardMarkup()
        keys = []
        for i in range(1, 10):
            keys.append(types.InlineKeyboardButton(text=f'{15 + (i - 1) * 4} - {15 + i * 4}', callback_data=i + 1000))
        keys.append(types.InlineKeyboardButton(text='50+', callback_data=1010))
        keyboard.add(*keys)

        bot.send_message(
            call.message.chat.id, 
            text=f'Please select your age group', 
            reply_markup=keyboard
            )
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, 
                                    text=f'Gender {call.data}')
        
    elif call.data == 'Search':
        bot.send_message(call.message.chat.id,
                             text=f'Please give me the name of anime you would like to rate')
        search_user[call.from_user.username] = True
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    elif call.data == 'Popular':
        for id_ in popular_row:
            if id_ not in ratings[name].keys():
                anime_id = id_
                break
        #anime_id = popular_row[len(ratings[name])] 
        request_user[name] = anime_id 

        keyboard = types.InlineKeyboardMarkup()
        keys = []
        for i in range(1, 11):
            keys.append(types.InlineKeyboardButton(text=f'{i}', callback_data=i))
        keys.append(types.InlineKeyboardButton(text='Did not watch', callback_data=-1))
        keyboard.add(*keys)

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)

        bot.send_message(
            call.message.chat.id, 
            text=f'Please rate {id2name[str(item_id[anime_id])]}', 
            reply_markup=keyboard
            )
    else:
        response = int(call.data)
        if response >= 1000:
            user_feats[name][response - 997] = 1
            recs = cold_start(user_feats[name])
            for id_ in topn_recommendations(recs[0]):
                bot.send_message(call.message.chat.id, 
                                 text=f'Consider {id2name[str(row2anime_id[id_])]}')
            age_var = response - 1000
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, 
                                    text=f'Age group {15 + (age_var - 1) * 4} - {15 + age_var * 4}')

        else:
            if response > 0:
                print(ratings, request_user)
                ratings[name][request_user[name]] = response
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, 
                                    text=f'{id2name[str(item_id[request_user[name]])]}: {response}')
            else:
                ratings[name][request_user[name]] = 0
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)

    


while True:
    try:
        bot.polling(none_stop=True)
    except:
        pass