import sys
import binascii
import time
import telegram
from botrasp_database import Database
from hoperf.board_config import BOARD
from rasp import Lora
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram import ReplyMarkup
import logging


rasp= Lora()
db=Database()

DEBUG_MODE = True
my_token = '616951805:AAEMk8pFivwdy32d7543Z-XKv_2M5lAz7_U'#Token of the Telegram App using botfather
ANY_ADDR = b'FFFFFFFFFFFFFFFF'
my_lora_address=b'FFFFFFFraspberry'
my_lora_address2=b'FFFFFFFraspbsend'
updater = Updater(token='616951805:AAEMk8pFivwdy32d7543Z-XKv_2M5lAz7_U')
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

db.setup()


def send(msg, chat_id, token=my_token):#Function to send a message to the bot
	bot = telegram.Bot(token=token)
	bot.sendMessage(chat_id=chat_id, text=msg)

def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Welcome to the messenger lopy bot")
	bot.send_message(chat_id=update.message.chat_id, text="Please, insert your phone Number or username with the orden /register")

def register(bot,update, args):#Funtion to register a user in the database
	user = ' '.join(args)
	user=user.lower()
	idUser = update.message.chat_id
	flag = db.checkuser(idUser,user)#Checking the user in the database
	if flag ==1:
		bot.send_message(chat_id=idUser, text="Updated, your username now is @"+user)
	elif(flag==2):
		bot.send_message(chat_id=idUser, text="Sorry, this Username is already in use, please choose another one")
	else:
		bot.send_message(chat_id=idUser, text="Welcome @"+user)
	if DEBUG_MODE: print("DEBUG: Username: ", user)
	if DEBUG_MODE: print("DEBUG: Chat id: ", idUser)
	database = db.getall()
	if DEBUG_MODE: print("DEBUG: Database",database)

def send_to(bot,update, args):#Function to look for a user through LoRa
	idUser = update.message.chat_id
	user = ' '.join(args)
	if(user!=""):
		user=user.lower()
		content=str(str(my_lora_address2)+","+user)
		sent, retrans,sent = rasp.trans(content, my_lora_address2,ANY_ADDR)
		msg,source_addr2 = rasp.recv(my_lora_address2,ANY_ADDR)
		if(msg!=b""):
			db.savem(user,source_addr2)
			bot.send_message(chat_id=idUser, text="User Found, please write /msg and your message")
		else:
			bot.send_message(chat_id=idUser, text="User not Found, please try again later")
	else:
		bot.send_message(chat_id=idUser, text="Sorry, you have to tell me an username")

def msg(bot,update,args):#Function to send a message through LoRa
	message=' '.join(args)
	sender=db.getusername(update.message.chat_id)
	receiver,source_addr2=db.getinfo(update.message.chat_id)
	aenvio = sender+","+message+","+receiver
	sent, retrans,sent = rasp.trans(aenvio, my_lora_address2,source_addr2)
	bot.send_message(chat_id=idUser, text="Message Sent")

def helpb(bot,update):
	bot.send_message(chat_id=update.message.chat_id, text="I will help you to remember some commands:")
	bot.send_message(chat_id=update.message.chat_id, text=" you can insert your phone Number or username with the /register order")
	bot.send_message(chat_id=update.message.chat_id, text=" To send a message please use the /send_to order and the name of the user")
	bot.send_message(chat_id=update.message.chat_id, text=" To send it please use the /msg order and the message")


def unknown(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command, if you don't remember you can use the /help order.")

start_handler = CommandHandler('start', start)
help_handler = CommandHandler('help', helpb)
register_handler = CommandHandler('register', register, pass_args=True)
send_to_handler = CommandHandler('send_to', send_to, pass_args=True)
unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(register_handler)
dispatcher.add_handler(send_to_handler)
dispatcher.add_handler(unknown_handler)

updater.start_polling()
database = db.getall()
if DEBUG_MODE: print("DEBUG: Database",database)
print("All Set")

while True:
	try:
		print("Listening")
		data,source_addr = rasp.recv(my_lora_address, ANY_ADDR)#Function to receive the messages
		if DEBUG_MODE: print("Data Received", data)
		#data=data[0] #Changing type from tuple to string
		if DEBUG_MODE: print("Data After", data)
		if(data!=''):
			IPlora,user = data.split(",")
			IPloraf = IPlora[2:]
			if DEBUG_MODE: print("DEBUG: IPlora",IPloraf)
			if DEBUG_MODE: print("DEBUG: source_addr",source_addr)
			if DEBUG_MODE: print("DEBUG: User",user)
			chat=db.getuser(user)#Checking if the user is in the database
			if DEBUG_MODE: print("DEBUG: result",chat)
			if(chat!=None):#If the message is valid, here we go!
				chat_id=''.join(map(str, chat))
				if DEBUG_MODE: print("DEBUG: chat_id",chat_id)
				sent, retrans,sent = rasp.trans(my_lora_address, my_lora_address,IPloraf)#Responding to the lopy
				print("Confirmation Message Sent")
				msg,source_addr2 = rasp.recv(my_lora_address,source_addr)#Receiving the full message
				if DEBUG_MODE: print("DEBUG: msg",msg)
				#msg=data2[0]
				idEmisor, mensajef,usuario = msg.split(",")
				msg1="Message LoRa from "+"@"+idEmisor+":"
				send(msg1,chat_id,my_token)#Sending the message to the telegram user
				send(mensajef,chat_id,my_token)
			else:
				if DEBUG_MODE: print("DEBUG: User",user)
				if DEBUG_MODE: print("DEBUG: Not found")
		else:
			print("ERROR IN PACKET, LISTENING AGAIN")
	except KeyboardInterrupt:
		sys.stdout.flush()
		print("")
		updater.stop()
		sys.stderr.write("KeyboardInterrupt\n")
		break
	finally:
		sys.stdout.flush()