import numpy as np
import json
import telebot
from telebot import types

from utils import *
from load import *


M = item_matrix @ item_matrix.T

ratings = {}
request_user = {}

API_TOKEN = '5677096457:AAHYpRxfaCw9WnJjRybbF-igrxK3XAe3cXo'
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['suggest'])
def echo_message(message):
    name = message.from_user.username
    if name not in ratings:
        bot.send_message(message.chat.id,
                             text=f'Not enough info')
    else:
        p = np.zeros(13686)
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
    for i in range(1, 11):
        keys.append(types.InlineKeyboardButton(text=f'{i}', callback_data=i))
    keyboard.add(*keys)
    
    anime_id = popular_row[len(ratings[name])]
    request_user[name] = anime_id

    bot.send_message(
        message.from_user.id, 
        text=f'Please rate {id2name[str(item_id[anime_id])]}', 
        reply_markup=keyboard
        )
    

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    name = call.from_user.username
    ratings[name][request_user[name]] = call.data
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                           text=f'{id2name[str(item_id[request_user[name]])]}: {call.data}')   
                


bot.polling()