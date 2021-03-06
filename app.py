import requests
from flask import jsonify
import re
import json
import os
import telegram
import logging
import time
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Updater, Filters

apikey = "USvTAH3yhAE3i188kmpg3w3CTht96BFbc8"


def getAuctionHouseDataURL():
	url = "https://us.api.blizzard.com/wow/auction/data/QUELTHALAS?locale=en_US&access_token="+apikey
	response = requests.get(url=url)
	return response.json()

def getAuctionHouseDataJson(last_modified):
	response = getAuctionHouseDataURL()
	files = response['files']
	url = files[0]['url']
	date = files[0]['lastModified']
	if(str(date) != last_modified):
		#bot.send_message(chat_id=update.message.chat_id, text="Refreshing Blizzard's database. Please wait")

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
def getAuctionsFromItem(anItemID):
	last_modified_file = open('./data/last_modified','r')
	last_modified = last_modified_file.read()
	last_modified_file.close()
	getAuctionHouseDataJson(last_modified)
	with open('./data/data') as data_file:
		allData = json.load(data_file)
	auctions = allData['auctions']
	msgs = []
	msg = ""
	counter = 1
	firstMatch = True
	for x in auctions:
		if x['item'] == anItemID:
			if firstMatch:
				msg = "Auctions \n"
				firstMatch = False
			quantity = x['quantity']
			pricePerUnit = x['bid'] // quantity
			gold ='{:,}'.format((pricePerUnit//100)//100).replace(',', '.')
			silver = (pricePerUnit//100) % 100
			copper = (pricePerUnit%100)
			bid = str(gold) + "G " + str(silver)+"S "+str(copper)+"C "
			owner = x['owner']
			msg = msg + owner + " - price per unit: " + bid + "\n"
			counter+=1
			if counter == 75:
				msgs.append(msg)
				msg = ""
				counter=0
	if (len(msgs)==0):
		msgs.append("There are no auctions to show")

	return msgs


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
			gold ='{:,}'.format((x['bid']//100)//100).replace(',', '.')
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
	url = "https://us.api.blizzard.com/data/wow/item/"+str(anItemID)+"?namespace=static-us&locale=en_US&access_token="+apikey
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
	if len(args) ==0:
		msg = "Cannot leave <character_name> blank"
		bot.send_message(chat_id=update.message.chat_id, text=msg)
	else:
		character_name = args[0].lower().capitalize()
		msg = getAuctionsFromCharacter(character_name)
		bot.send_message(chat_id=update.message.chat_id, text=msg)

def daggermaw(bot, update):
	itemID = 124669
	msgs = getAuctionsFromItem(itemID)
	print(msgs)
	for msg in msgs:
		bot.send_message(chat_id=update.message.chat_id, text=msg)
		
def token(bot, update):
	url = "https://us.api.blizzard.com/data/wow/token/index?namespace=dynamic-us&locale=en_US&access_token=" +apikey 
	responseJson = requests.get(url=url).json()
	price = responseJson['price']
	last_updated = responseJson['last_updated_timestamp']
	last_updated = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_updated))
	bot.send_message(chat_id=update.message.chat_id, text=last_updated)
	gold ='{:,}'.format((price//100)//100).replace(',', '.')
	silver = (price//100) % 100
	copper = (price%100)
	price = str(gold) + "G " + str(silver)+"S "+str(copper)+"C "
	bot.send_message(chat_id=update.message.chat_id, text=last_updated)
	bot.send_message(chat_id=update.message.chat_id, text=price)


if __name__ == "__main__":
    # Set these variable to the appropriate values
    TOKEN = "629926880:AAE60C7BDkDKpO96pbsMN2pDgXsFvlGsFCY"
    NAME = "wow-ah-telegram-bot"

    # Port is given by Heroku
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
    dp.add_handler(CommandHandler('daggermaw', daggermaw))
    dp.add_handler(CommandHandler('token', token))
    dp.add_handler(CommandHandler('help',help))
    dp.add_handler(MessageHandler(Filters.command, unknown))

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
updater.idle()
