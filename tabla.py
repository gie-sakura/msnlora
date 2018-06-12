import struct
import sys
import time
from socket import *
import swlpv3
import os
from machine import SD
#import pickle

DEBUG_MODE = True
q=0

class BaseDatos:
	BaseM=[]
	BaseU=[]
	n=0
	message_number = 0

	def ingresoRegistro(self,usuario): #AM: Registro de nuevo usuario
		tbs="a"
		blks = usuario.split("&")
		for i in blks:
			v = i.split("=")
			tbs += ","+v[1]
		print(tbs)
		x=tbs.split(",")
		if DEBUG_MODE: print("DEBUG: data from the form: ", x)
		#print(x)
		user=x[1]
		if DEBUG_MODE: print("DEBUG: User: ", user)
		if user in self.BaseU:
			posicion=self.BaseU.index(user)
		else:
			self.BaseU.append(user)
			self.BaseM.append(user)
			posicion=self.BaseU.index(user)	
		if DEBUG_MODE: print("DEBUG: Position: ", posicion)
		if DEBUG_MODE: print("DEBUG: User Database: ", self.BaseU)
		self.BaseM[posicion]={}
		r_content='<head><meta charset="utf-8"><title>Register LoRa</title>\n'
		r_content +='<style type="text/less">\n'
		r_content +=".dropdown-toggle {display:none;}\n"
		r_content +=".dropdown-menu {display:none;}\n"
		r_content +="</style>\n"
		r_content +="</head>\n"
		r_content += "<body><h1>Welcome</h1>\n"
		r_content += "<h1>"+user+"</h1>\n"
		r_content += '<form class="form-horizontal well" action="" method="post"><div><label for="named">Destination:</label><input type="text" id="named" name="dest_name"></div><div><label for="msg">Message:</label> <textarea id="msg" name="user_message"></textarea></div><div class="button"><button type="submit" onclick=this.form.action="execposthandler.html";document.getElementById("oculto").style.visibility="visible">Send your message</button></div><div class="button"><button type="submit" onclick=this.form.action="tabla.html">Check my messages</button></div>'
		r_content += '<div id="oculto" style="visibility:hidden">Sending...</div>'
		r_content += "<p><a href='/'>Back to home</a></p></body>\n"
		return r_content,user

	def ingreso(self,Emisor,destino,Mensaje): #AM: Funcion para ingresar datos cuando los recibe por primera vez
		print("Entra a guardar el mensaje")
		if DEBUG_MODE: print("DEBUG: Message Database: ", self.BaseM)
		if DEBUG_MODE: print("DEBUG: User Database: ", self.BaseU)
		posicion=self.BaseU.index(destino)
		if DEBUG_MODE: print("DEBUG: Position: ", posicion)
		self.BaseM[posicion]["Emisor "+str(self.n)]=Emisor
		self.BaseM[posicion]["Mensaje "+str(self.n)]=Mensaje
		self.n+=1
		if DEBUG_MODE: print("DEBUG: New Users Database: ", self.BaseU)
		if DEBUG_MODE: print("DEBUG: New Message Database: ", self.BaseM)
		if DEBUG_MODE: print("DEBUG: Number of Message: ", self.n)
		self.message_number+=1
		if(self.message_number==10):
			print("Saving Databases")
			x = save_backup(self.BaseU,self.BaseM)
			self.message_number=0


	def consultaControl(self,destino):
		BaseUsuarios = self.BaseU
		print("Base Usuarios")
		print(BaseUsuarios)
		bandera = 0
		if destino in BaseUsuarios: # AM: Consulta si esta registrado, y hace actualizacion
			bandera = 1
		else:
			bandera = 0
		return bandera

	def consulta(self,user):
		if DEBUG_MODE: print("DEBUG: User: ", user)
		BaseUConsulta = self.BaseU
		if DEBUG_MODE: print("DEBUG: User Database: ", BaseUConsulta)
		BaseMConsulta = self.BaseM
		posicion=BaseUConsulta.index(user)
		if DEBUG_MODE: print("DEBUG: Messages: ", BaseMConsulta[posicion])
		if (BaseMConsulta[posicion]!={}):
			r_content = "<h1>Messages sent via LoRa</h1>\n"
			r_content += "\n"
			r_content += str(BaseMConsulta[posicion]) + "\n"
			r_content += "\n"
			r_content += "<p><a href='/'>Back to home</a></p>\n"
		else:
			r_content = "<h1>No Messages</h1>\n"
			r_content += "\n"
			r_content += "\n"
			r_content += "<p><a href='/'>Back to home</a></p>\n"
		return r_content
################################################################################################################
#Management of the data in the SD Card
def save_backup(DBU,DBM):
	global q
	#sd = SD()
	#os.mount(sd, '/sd')
	#print("SD Card Enabled")
	f = open('/sd/DatabaseU'+str(q)+'.txt', 'w')
	f.write(str(DBU))
	f.close()
	f = open('/sd/DatabaseM'+str(q)+'.txt', 'w')
	f.write(str(DBM))
	f.close()
	print("Databases Saved")
	q+=1
	return q

def open_backup(a):
	f = open('/sd/DatabaseU'+str(a-1)+'users.txt', 'r')
	dataUser = f.readall()
	f.close()
	listaUser = eval(dataUser)
	f = open('/sd/DatabaseM'+str(a-1)+'users.txt', 'r')
	dataMess = f.readall()
	f.close()
	listaMess = eval(dataMess)
	return listaUser,listaMess