import struct
import sys
import time
from socket import *
import swlpv3

class BaseDatos:
	BaseM=[]
	BaseU=[]

	def ingresoRegistro(self,usuario): #AM: Registro de nuevo usuario
		#user =""
		#blks=[]
		tbs="a"
		blks = usuario.split("&")
		for i in blks:
			v = i.split("=")
			tbs += ","+v[1]
		print(tbs)
		x=tbs.split(",")
		print(x)
		user=x[1]
		print("User es")
		print(user)
		self.BaseU.append(usuario)
		self.BaseM.append(usuario)
		posicion=self.BaseU.index(usuario)
		print("posicion")
		print(posicion)
		print("Base Usuarios")
		print(self.BaseU)
		self.BaseM[posicion]={}
		r_content = "<h1>Registrado</h1>\n"
		r_content += "<h1>"+user+"</h1>\n"
		r_content += "<p><a href='/'>Back to home</a></p>\n"
		return r_content

	def ingreso(self,Emisor,destino,Mensaje): #AM: Funcion para ingresar datos cuando los recibe por primera vez
		print(self.BaseM)
		print(type(self.BaseM))
		posicion=self.BaseU.index(destino)
		print(posicion)
		self.BaseM[posicion]["Emisor "+str(n)+": "]=Emisor
		self.BaseM[posicion]["Mensaje "+str(n)+": "]=Mensaje
		n+=1
		print("lista de envios")
		print(self.BaseU)
		print("Lista de Mensajes")
		print(self.BaseM)
		print(n)
	def consultaControl(destino):
		BaseUsuarios = self.BaseU
		bandera = 0
		if destino in BaseUsuarios: # AM: Consulta si esta registrado, y hace actualizacion
			bandera = 1
		else:
			bandera = 0
		return bandera
	def consulta(self,post_body):
		blks = post_body.split("&")
		for i in blks:
			v = i.split("=")
			tbs += ","+v[1]
		sender, receiver, message=tbs.split(",")
		BaseUConsulta = self.BaseU
		BaseMConsulta = self.BaseM
		if sender in BaseUConsulta:
			posicion=BaseUConsulta.index(sender)
			r_content = "<h1>Messages sent via LoRa</h1>\n"
			r_content += "\n"
			r_content += BaseMConsulta[posicion] + "\n"
			r_content += "\n"
			r_content += "<p><a href='/'>Back to home</a></p>\n"
		else:
			ingresoRegistro(sender)
			r_content = "<h1>No Messages</h1>\n"
			r_content += "\n"
			r_content += "\n"
			r_content += "<p><a href='/'>Back to home</a></p>\n"
		return r_content