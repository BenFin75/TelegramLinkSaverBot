from telegram import *
from telegram.ext import *
import logging
import os
from os import walk
import requests
import json
import pandas as pd
from pathlib import Path, PureWindowsPath
from urlextract import URLExtract

bot_token_df = pd.read_csv((os.path.join(os.path.dirname(os.getcwd()),"TelegramBotTokens.csv")))
bot_index = int(bot_token_df.index[bot_token_df['Bot Name'] == 'Link Saver Bot'].values)
bot_token = str(bot_token_df.loc[[bot_index], ['Bot Token']].values).strip("'[]")

bot = Bot(bot_token)
updater=Updater(bot_token, use_context=True)
dispatcher=updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
extractor = URLExtract()

users_win = PureWindowsPath(r'.\UserData')
userdb = Path(users_win)


def start(update, context):
    help_msg = (
        "Hello! Welcome to the telegram link saver bot!" + "\n" + 
        "This bot allows you to save links into categories and retrieve them later" + "\n" + "\n" + 
        "Type /help for a list of commands." + "\n" + "\n" + 
        "Made by Ben Finley" + "\n" + 
        "The code for this bot is avalible at: https://github.com/Hiben75/TelegramLinkSaverBot"
        )
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_msg, disable_web_page_preview=1);

def helpcmd(update, context):
    help_msg = ( 
        "Here is a list of my commands:" + "\n" + "\n" + 
        "/savelink  <category>  <link>" + "\n" + "save your link with a category. e.g. /save google www.google.com" + "\n" + "\n" + 
        "/getlinks  <category>" + "\n" + "retreive all links associated with a category. e.g. /getlinks google" + "\n" + "\n" + 
        "/getcategories" + "\n" + "retreive all saved categories." + "\n" + "\n" + 
        "/removelink  <category>  <link>" + "\n" + "remove a specific link in a category. e.g. removelink google www.google.com" + "\n" + "\n" + 
        "/clearcategory  <category>" + "\n" + "deletes all links associated with a category. e.g. /clearcategory google" + "\n" + "\n" + 
        "/wipedata" + "\n" + "deletes all your saved links and categories." + "\n" + "\n" + 
        "Made by Ben Finley" + "\n" + 
        "The code for this bot is avalible at: https://github.com/Hiben75/TelegramLinkSaverBot"
        )
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_msg);

def save(update, context):
    users_message = update.message.text
    username = update.message.from_user.username
    userfile = username + '.json'
    userfile_path = os.path.join(userdb, userfile)
    url = extractor.find_urls(users_message)
    if not os.path.isfile(userfile_path):
        with open(userfile_path, "w") as file_init:
            initialize = {}
            file_init.write(json.dumps(initialize))
    if len(url) == 1:
        urlstring = ' '.join(str(x) for x in url)
        category = users_message.replace(urlstring, '') [10:-1]
        toadd = str(url).strip("[']")
        with open(userfile_path) as file:
            user_data = json.loads(file.read())
            if category in user_data:
                if toadd not in user_data[category]:
                    user_data[category].append(toadd)
                    with open(userfile_path, "w") as file_write:
                        json.dump(user_data, file_write, sort_keys=True, indent=2)
                    save_msg = ('Your link has been saved as a "' + category + '" link.' + "\n" +
                                "Type:" + "\n" + "/getlink " + category + "\n" + "to retrieve this link and other links of this category."
                                )
                else:
                    save_msg = ('Your link has already been added to "' + category + '".' + "\n" +
                                "Type:" + "\n" + "/getlink " + category + "\n" + "to retrieve this link and other links of this category."
                                )
            else:
                toadd_lst = [toadd]
                user_data[category] = toadd_lst
                with open(userfile_path, "w") as file_write:
                    json.dump(user_data, file_write, sort_keys=True, indent=2)
                save_msg = ('Your link has been saved as a "' + category + '" link.' + "\n" +
                            "Type:" + "\n" + "/getlink " + category + "\n" + "to retrieve this link and other links of this category."
                            )
    if len(url) > 1:
        save_msg = "please only send one link at a time"
    if len(url) == 0:
        save_msg = "please send make sure you have a valid link"
    context.bot.send_message(chat_id=update.effective_chat.id, text=save_msg);
        
def get(update, context):
    users_message = update.message.text
    username = update.message.from_user.username
    userfile = username + '.json'
    userfile_path = os.path.join(userdb, userfile)
    user_link_json = open(userfile_path, "a")
    category = users_message [9:]
    with open(userfile_path) as file:
        user_data = json.loads(file.read()) 
        if category in user_data:
            links = '\n \n'.join(user_data[category])
            get_msg = ('Here are the links you saved in "' + category + '":' + "\n" + "\n" +  links)

        else:
            categories_list = []
            for key in user_data.keys():
                categories_list.append(key)
                saved_categories = '\n'.join(categories_list)
            get_msg = ("You dont have that as a category" + "\n" + "\n" + "Your saved categories are:" + "\n" + "\n" + saved_categories)
    context.bot.send_message(chat_id=update.effective_chat.id, text=get_msg, disable_web_page_preview=1);

def remove(update: Update, context: CallbackContext):
    global  meesage_data
    meesage_data = update
    reply_buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Yes", callback_data=1),
            InlineKeyboardButton("No", callback_data=2),
        ]
    ])
    update.message.reply_text("Are you sure?", reply_markup=reply_buttons)

def clear(update: Update, context: CallbackContext):
    global  meesage_data
    meesage_data = update
    users_message = update.message.text
    category = users_message [7:]
    reply_buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Yes", callback_data=3),
            InlineKeyboardButton("No", callback_data=4),
        ]
    ])
    update.message.reply_text("Are you sure you want to remove all links from " + category + "?", reply_markup=reply_buttons)

def wipe(update: Update, context: CallbackContext):
    global  meesage_data
    meesage_data = update
    reply_buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Yes", callback_data=5),
            InlineKeyboardButton("No", callback_data=6),
        ]
    ])
    update.message.reply_text("Are you sure you want to delete all your saved links?", reply_markup=reply_buttons)

def button(update: Update, context: CallbackContext):
    global meesage_data
    if update.callback_query.data == '1':
        users_message = meesage_data.message.text
        username = meesage_data.message.from_user.username
        userfile = username + '.json'
        userfile_path = os.path.join(userdb, userfile)
        url = extractor.find_urls(users_message)
        if not os.path.isfile(userfile_path):
            button_msg = "You dont have that link saved."
            chat_id_set = update.effective_chat.id
            meesage_data.callback_query.answer()
            update.callback_query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup([])
                )
            context.bot.deleteMessage(update.callback_query.message.chat.id, update.callback_query.message.message_id)
            context.bot.send_message(chat_id=update.effective_chat.id, text=button_msg)
            return;
        if len(url) == 1:
            urlstring = ' '.join(str(x) for x in url)
            category = users_message.replace(urlstring, '') [12:-1]
            toadd = str(url).strip("[']")
            with open(userfile_path) as file:
                user_data = json.loads(file.read())
                if category in user_data:
                    if toadd not in user_data[category]:
                        button_msg = ("You dont have that link saved.")
                    else:
                        user_data[category].remove(toadd)
                        with open(userfile_path, "w") as file_write:
                            json.dump(user_data, file_write, sort_keys=True, indent=2)
                        button_msg = (toadd + ' has been removed from ' + category)
                else:
                    categories_list = []
                    for key in user_data.keys():
                        categories_list.append(key)
                        saved_categories = '\n'.join(categories_list)
                    button_msg = ('"' + category + '" is not one of your categories' + "\n" + "\n" + "Your saved categories are:" + "\n" + "\n" + saved_categories)
        if len(url) > 1:
            button_msg = "please only send one link at a time"
        if len(url) == 0:
            button_msg = "please send make sure you have a valid link"

    elif update.callback_query.data == '2':
        button_msg = 'No changes have been made.'

    elif update.callback_query.data == '3':
        users_message = meesage_data.message.text
        username = meesage_data.message.from_user.username
        userfile = username + '.json'
        userfile_path = os.path.join(userdb, userfile)
        user_link_json = open(userfile_path, "a")
        category = users_message [7:]
        with open(userfile_path) as file:
            user_data = json.loads(file.read()) 
            if category in user_data:
                with open(userfile_path, "w") as file_write:
                    del user_data[category]
                    json.dump(user_data, file_write, sort_keys=True, indent=2)
                button_msg = ('All links in "' + category + '" have been deleted')

            else:
                categories_list = []
                for key in user_data.keys():
                    categories_list.append(key)
                    saved_categories = '\n'.join(categories_list)
                button_msg = ("You dont have that as a category" + "\n" + "\n" + "Your saved categories are:" + "\n" + "\n" + saved_categories)

    elif update.callback_query.data == '4':
        button_msg = 'No changes have been made.'

    elif update.callback_query.data == '5':
        users_message = meesage_data.message.text
        username = meesage_data.message.from_user.username
        userfile = username + '.json'
        userfile_path = os.path.join(userdb, userfile)
        os.remove(userfile_path)
        button_msg = 'Your data has been wiped'

    elif update.callback_query.data == '6':
        button_msg = 'No changes have been made.'

    chat_id_set = update.effective_chat.id
    update.callback_query.answer()
    update.callback_query.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup([])
        )
    context.bot.deleteMessage(update.callback_query.message.chat.id, update.callback_query.message.message_id)
    context.bot.send_message(chat_id=update.effective_chat.id, text=button_msg)

def getcategories(update, context):

	users_message = update.message.text
	username = update.message.from_user.username
	userfile = username + '.json'
	userfile_path = os.path.join(userdb, userfile)
	if not os.path.isfile(userfile_path):
	    with open(userfile_path, "w") as file_init:
	        initialize = {}
	        file_init.write(json.dumps(initialize))
	with open(userfile_path) as file:
	    user_data = json.loads(file.read())
	    categories_list = []
	    for key in user_data.keys():
	        categories_list.append(key)
	        print(categories_list)
	        saved_categories = '\n'.join(categories_list)
	    categories_msg = ("Your saved categories are:" + "\n" + "\n" + saved_categories)
	    updater.bot.sendMessage(chat_id=update.effective_chat.id, text = categories_msg);
	    if len(categories_list) == 0: 
	    	updater.bot.sendMessage(chat_id=update.effective_chat.id, text = "You dont have any saved categories yet.");

def stop(update, context):
    if update.message.chat.id == 110799848:
        updater.bot.sendMessage(chat_id=update.effective_chat.id, text = 'Shuting Down');
        updater.stop()
        updater.is_idle = False



#Dispatchers for bot commands
dispatcher.add_handler(CallbackQueryHandler(button))
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('helplink', helpcmd))
dispatcher.add_handler( CommandHandler('savelink', save))
dispatcher.add_handler(CommandHandler('getlinks', get))
dispatcher.add_handler(CommandHandler('removelink', remove))
dispatcher.add_handler(CommandHandler('clear', clear))
dispatcher.add_handler(CommandHandler('wipedata', wipe))
dispatcher.add_handler(CommandHandler('getcategories', getcategories))
dispatcher.add_handler(CommandHandler('stop', stop))



updater.start_polling()

updater.idle()