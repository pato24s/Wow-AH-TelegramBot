import requests
from flask import jsonify
import re
import json

import telegram
import logging
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Updater, Filters

apikey = "e8z3nuc6af5qeu5svxq6t5w2y43a5v5m"


def getAuctionHouseDataURL():
	url = "https://us.api.battle.net/wow/auction/data/Quel'Thalas?locale=es_MX&apikey="+apikey
	response = requests.get(url=url)
	return response.json()

def getAuctionHouseDataJson(last_modified):
	response = getAuctionHouseDataURL()
	files = response['files']
	url = files[0]['url']
	date = files[0]['lastModified']
	if(str(date) != last_modified):
		print("actualizando json")
		response = requests.get(url=url)
		
		#cambio last_modified file
		last_modified_file = open('./data/last_modified','w')
		last_modified_file.write(str(date))
		last_modified_file.close()

		#cambio json file
		with open('./data/data', 'w') as outfile:
			json.dump(response.json(), outfile)
	
	else:
		print("json ya actualizado")

def getAuctionsFromCharacter(aCharacter):
	last_modified_file = open('./data/last_modified','r')
	last_modified = last_modified_file.read()
	last_modified_file.close()
	getAuctionHouseDataJson(last_modified)
	with open('./data/data') as data_file:
		allData = json.load(data_file)
	auctions = allData['auctions']
	print(aCharacter)
	msg = ""
	for x in auctions:
		if x['owner'] == aCharacter:
			gold = (x['bid']//100)//100
			silver = (x['bid']//100) % 100
			copper = (x['bid']%100)
			bid = str(gold) + "G " + str(silver)+"S "+str(copper)+"C "
			print(getItemNameFromId(x['item']) +" - bid: " + bid)
			msg = msg + getItemNameFromId(x['item']) +" - bid: " + bid + "\n"
	
	if (len(msg)==0):
		msg = "There are no auctions to show"
	else:
		msg = "Auctions \n" + msg
	return msg

def getItemNameFromId(anItemID):
	url = "https://us.api.battle.net/wow/item/"+str(anItemID)+"?locale=en_US&apikey="+apikey
	responseJson = requests.get(url=url).json()
	return responseJson['name']


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="This bot will show you all your current auctions in Quel'Thalas\n Type /help in order to get information about the commands")

def help(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Commands:\n /start - Get welcome message \n /auctions <character_name> - Get current auctions for <character_name>")


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command. \n Type \help to get a list of possible commands.")


def auctions(bot, update, args):
	character_name = args[0].lower().capitalize()
	msg = getAuctionsFromCharacter(character_name)
	bot.send_message(chat_id=update.message.chat_id, text=msg)

if __name__ == "__main__":
    # Set these variable to the appropriate values
    TOKEN = "629926880:AAE60C7BDkDKpO96pbsMN2pDgXsFvlGsFCY"
    NAME = "WowAH_bot"

    Port is given by Heroku
    PORT = os.environ.get('PORT')

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the Updater
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    # Add handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_error_handler(error)

    dp.add_handler(CommandHandler('auctions',auctions,pass_args=True))
    dp.add_handler(CommandHandler('help',help))
    dp.add_handler(MessageHandler(Filters.command, unknown))

    Start the webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
updater.idle()