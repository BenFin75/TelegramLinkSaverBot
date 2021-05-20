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
print(bot_token)



bot = Bot(bot_token)
updater=Updater(bot_token, use_context=True)
dispatcher=updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
extractor = URLExtract()

users_win = PureWindowsPath(r'.\UserData')
userdb = Path(users_win)


def start(update, context):
    print()
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
        "/getlinklink  <category>" + "\n" + "retreive all links associated with a category. e.g. /getlink google" + "\n" + "\n" + 
        "Made by Ben Finley" + "\n" + 
        "The code for this bot is avalible at: https://github.com/Hiben75/TelegramLinkSaverBot"
        )
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_msg);

#def updatejson(update, context, users_message, username, user_link_json):



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
        print(toadd)
        print(userfile_path)
        with open(userfile_path) as file:
            user_data = json.loads(file.read())
            if category in user_data:
                if toadd not in user_data[category]:
                    user_data[category].append(toadd)
                    print(user_data[category])
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
                print(user_data[category])
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
        print('opened file')
        user_data = json.loads(file.read()) 
        if category in user_data:
            links = '\n \n'.join(user_data[category])
            get_msg = ('Here are the links you saved in "' + category + '":' + "\n" + "\n" +  links)

        else:
            catagories_list = []
            for key in user_data.keys():
                catagories_list.append(key)
                saved_catagories = '\n'.join(catagories_list)
            get_msg = ("You dont have that as a category" + "\n" + "Your saved categories are:" + "\n" + saved_catagories)
    context.bot.send_message(chat_id=update.effective_chat.id, text=get_msg, disable_web_page_preview=1);



def stoplink(update, context):
    if update.message.chat.id == 110799848:
        shutdown_msg = 'Shuting Down'
        updater.bot.sendMessage(chat_id=update.effective_chat.id, text = shutdown_msg);
        updater.stop()
        updater.is_idle = False


#Handlers for bot commands
start_handler = CommandHandler('start', start)
help_handler = CommandHandler('helplink', helpcmd)
save_handler = CommandHandler('savelink', save)
get_handler = CommandHandler('getlink', get)
stoplink_handler = CommandHandler('stoplink', stoplink)

#Dispatchers for bot commands
dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(save_handler)
dispatcher.add_handler(get_handler)
dispatcher.add_handler(stoplink_handler)



updater.start_polling()

updater.idle()