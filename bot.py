#! /usr/bin/python

from telegram.ext import Updater, CommandHandler
import requests
import json
import time
import os
import threading
from threading import Thread
import telegram
import random

url = "https://www.binance.com/bapi/earn/v1/friendly/pos/union?pageSize=50&pageIndex=1&status=ALL"
# configure Telegram bot API token
# api_token = ""
bot = telegram.Bot(token=api_token)

happy_emojis = [u'\U0001F642', u'\U0001F603', u'\U0001F600', u'\U0001F389', u'\U0001F38A']
sad_emojis = [u'\U0001F610', u'\U0001F615', u'\U0001F641']

def greet_message(update, context):
        msg = "Welcome to Binance DeFi Staking alert bot"
        msg += "\n\n === Designed by CryptoShine ==="
        msg += "\n\n Follow on Twitter @ CryptoShine"
        msg += "\n\nYou can use this bot to do the following:"
        msg += "\n\n1. Query the status of staking on Binance for a specific token"
        msg += "\nUse the command: /check <name_of_token>"
        msg += "\n\n2. Set an alert to notify you when status of staking pool changes for a specific token"
        msg += "\nUse the command: /alert <name_of_token>"
        msg += "\n\n3. Clear an alert for a specific token"
        msg += "\nUse the command: /clear <name_of_token>"

        update.message.reply_text(msg)

def cmd_clear(update, context):
        token = context.args[0]
        user_id = str(update.effective_user.id)

        with open("alertdb", "r") as f:
            data = f.read()

        res = json.loads(data)

        for token_name in res:
            if token_name == token:
                ids = res[token_name]['user_ids']
                if user_id not in ids:
                    msg = "you have not yet set an alert for this token"
                    update.message.reply_text(msg)
                else:
                    ids.remove(user_id)
                    print("alert has been cleared")
                    update.message.reply_text("alert has been cleared")
        
        os.remove("alertdb")

        with open("alertdb", "w") as f:
                json.dump(res, f)

        return

def cmd_alert(update, context):
        token = context.args[0]
        user_id = str(update.effective_user.id)

        #print(user_id)

        with open("alertdb", "r") as f:
            data = f.read()

        res = json.loads(data)

        for token_name in res:
                if token_name == token:
                    ids = res[token_name]['user_ids']
                    if user_id in ids:
                        msg = "you have already set an alert for token: " + token
                        update.message.reply_text(msg)
                    else:
                        ids.append(user_id)
                        update.message.reply_text("alert has been set successfully")

        os.remove("alertdb")

        with open("alertdb", "w") as f:
            json.dump(res, f)

        #print("request to set an alert by user with id:{0} and username: {1}".format(update.effective_user.id, update.effective_user.username))

        return

def check_status(token_name):
        results = {}
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.2; rv:88.0) Gecko/20100101 Firefox/88.0'}
        res = requests.get(url, headers=headers)
        response = res.text
        try:
            data = json.loads(response)
        except json.decoder.JSONDecodeError:
            print("there was an error")
            print(response)
            return results

        for i in range(len(data["data"])):
            if data["data"][i]["asset"] == token_name:
                projects = data["data"][i]["projects"]
                for j in range(len(projects)):
                    project_name = projects[j]['projectId']
                    status = projects[j]['sellOut']
                    if status == True:
                        state = 0
                    else:
                        state = 1
                    suffix = project_name[-2:]
                    key_name = token_name + "_" + suffix
                    results[key_name] = state

        return results

def monitor(upd):
    #print(upd)

    while True:
        #print("Checking for updates")

        with open("alertdb", "r") as f:
            data = f.read()

        res = json.loads(data)
        
        msg = ""

        for token in res:
            latest = check_status(token)
            #print(latest)

            previous = res[token]['state']

            for key in latest.keys():
                if latest[key] != previous[key]:
                    if latest[key] == 0:
                        status = "closed"
                    else:
                        status = "open"
                    
                    ids = res[token]['user_ids']
                    res[token]['state'] = latest

                    for uid in ids:
                        pool_name = token + " " + key[-2:] + " days pool"
                        if status == "open":
                            emoji = happy_emojis[random.randint(0,len(happy_emojis) - 1)]
                            msg = pool_name + " is " + status + " now " + emoji
                        else:
                            emoji = sad_emojis[random.randint(0,len(sad_emojis) - 1)]
                            msg = pool_name + " is " + status + " now " + emoji

                        bot.sendMessage(chat_id=uid, text=msg)
                        print("alert the user with id: {0} that {1} status changed to {2}".format(uid, key, status))
            
        os.remove("alertdb")

        with open("alertdb", "w") as f:
            json.dump(res, f)

        time.sleep(20)
    
def cmd_check(update, context):
        token_name = context.args[0]

        msg = ""

        if type(token_name) is not str:
            msg = "token name should be a string"
            update.message.reply_text(msg)
            return

        result = check_status(token_name)

        for pool in result.keys():
            if result[pool] == 0:
                available = "False"
            else:
                available = "True"

            pool_name = token_name + " " + pool[-2:] + " days"

            msg += pool_name + " : " + available + "\n"
        
        if msg:
            update.message.reply_text(msg)
        else:
            update.message.reply_text("Token name not found")

def main():
        updater = Updater(api_token)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", greet_message))
        dp.add_handler(CommandHandler("check", cmd_check))
        dp.add_handler(CommandHandler("alert", cmd_alert))
        dp.add_handler(CommandHandler("clear", cmd_clear))
        updater.start_polling()

        x = threading.Thread(target=monitor, args=(updater,))
        x.start()

        updater.idle()

if __name__ == "__main__":
    main()
