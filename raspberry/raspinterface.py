import sys
import binascii
import time
import telegram
from bot_database import Database
import bot_telegram2
from rasrecv import Lorarcv
from hoperf.board_config import BOARD

rasprec= Lorarcv(verbose=True)
db=Database()

DEBUG_MODE = True
my_token = '616951805:AAEMk8pFivwdy32d7543Z-XKv_2M5lAz7_U'
ANY_ADDR = b'FFFFFFFFFFFFFFFF'
my_lora_address=b'FFFFFFFraspberry'


BOARD.setup()


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
		data = rasprec.recv(my_lora_address, ANY_ADDR)
		chat_id='613841330'
		send(data,chat_id,my_token)
		time.sleep(60)
	except KeyboardInterrupt:
		sys.stdout.flush()
		print("")
		sys.stderr.write("KeyboardInterrupt\n")
	finally:
		sys.stdout.flush()
		#print("")
		#BOARD.teardown()