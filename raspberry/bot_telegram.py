from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import ReplyMarkup
import logging
from bot_database import Database

#Script made to the Telegram application
DEBUG_MODE = True
updater = Updater(token='616951805:AAEMk8pFivwdy32d7543Z-XKv_2M5lAz7_U')
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
db=Database()

db.setup()
def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Welcome to the messenger lopy bot")
	bot.send_message(chat_id=update.message.chat_id, text="Please, insert your phone Number or username with the orden /register")

def register(bot,update, args):
	user = ' '.join(args)
	idUser = update.message.chat_id
	flag = db.checkuser(idUser,user)
	if flag ==1:
		bot.send_message(chat_id=idUser, text="Updated, your username now is @"+user)
	else:
		bot.send_message(chat_id=idUser, text="Welcome @"+user)
	if DEBUG_MODE: print("DEBUG: Username: ", user)
	if DEBUG_MODE: print("DEBUG: Chat id: ", idUser)
	database = db.getall()
	if DEBUG_MODE: print("DEBUG: Database",database)

def unknown(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

start_handler = CommandHandler('start', start)
#confirm_handler = MessageHandler(Filters.text, confirm, pass_chat_data=True)
register_handler = CommandHandler('register', register, pass_args=True)
#receive_handler = MessageHandler(Filters.text, receive)
unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(register_handler)
#dispatcher.add_handler(confirm_handler)
dispatcher.add_handler(unknown_handler)

updater.start_polling()