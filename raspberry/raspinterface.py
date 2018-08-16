import sys
import binascii
import time
import telegram
from bot_database import Database
import bot_telegram
from rasrecv import Lorarcv
from hoperf.board_config import BOARD
from rasnd import LoRaSend

rasprec= Lorarcv(verbose=True)
raspsnd= LoRaSend(verbose=True)
db=Database()

DEBUG_MODE = True
my_token = '616951805:AAEMk8pFivwdy32d7543Z-XKv_2M5lAz7_U'
ANY_ADDR = b'FFFFFFFFFFFFFFFF'
my_lora_address=b'FFFFFFFraspberry'


def send(msg, chat_id, token=my_token):
	bot = telegram.Bot(token=token)
	bot.sendMessage(chat_id=chat_id, text=msg)

database = db.getall()
if DEBUG_MODE: print("DEBUG: Database",database)

"""while True:
	
	chat=db.getuser(usuario)
	chat_id=''.join(map(str, chat))
	if DEBUG_MODE: print("DEBUG: chat_id",chat_id)
	print(type(chat_id))
	send(mensaje,chat_id,my_token)"""
print("All Set")
while True:
	try:
		sys.stdout.write("Listening")
		data,source_addr = rasprec.recv(my_lora_address, ANY_ADDR)
		if DEBUG_MODE: print("Data Received", data)
		data=data[0] #Changing type from tuple to string
		sender,user=data.split(",")
		#msg=data[1]
		if DEBUG_MODE: print("DEBUG: user",user)
		if DEBUG_MODE: print("DEBUG: Sender",sender)
		chat=db.getuser(user)
		if DEBUG_MODE: print("DEBUG: result",chat)
		"""if(chat!=None):
			chat_id=''.join(map(str, chat))
			if DEBUG_MODE: print("DEBUG: chat_id",chat_id)
			msg1="Message LoRa from "+sender+":"
			send(msg1,chat_id,my_token)
			sent, retrans,sent = raspsnd.send(my_lora_address, my_lora_address,source_addr)
			print("Confirmation Message Sent")
			data2,source_addr2 = rasprec.recv(my_lora_address,source_addr)
			msg=data2[0]
			send(msg,chat_id,my_token)
		else:
			if DEBUG_MODE: print("DEBUG: User",user)
			if DEBUG_MODE: print("DEBUG: Not found")"""
	except KeyboardInterrupt:
		sys.stdout.flush()
		print("")
		sys.stderr.write("KeyboardInterrupt\n")
		break
	finally:
		sys.stdout.flush()
		#print("")
		#BOARD.teardown()