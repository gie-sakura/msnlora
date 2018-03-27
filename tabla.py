import struct
import sys
import time
from socket import *
import swlpv3

class BaseDatos:
	BaseM=[]
	BaseU=[]
	n=0

	def ingresoRegistro(self,usuario): #AM: Registro de nuevo usuario
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
		self.BaseU.append(user)
		self.BaseM.append(user)
		posicion=self.BaseU.index(user)
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
		print("Entra a guardar el mensaje")
		print(self.BaseM)
		print(self.BaseU)
		print(type(self.BaseM))
		posicion=self.BaseU.index(destino)
		print(posicion)
		self.BaseM[posicion]["Emisor "+str(self.n)+": "]=Emisor
		self.BaseM[posicion]["Mensaje "+str(self.n)+": "]=Mensaje
		self.n+=1
		print("lista de envios")
		print(self.BaseU)
		print("Lista de Mensajes")
		print(self.BaseM)
		print(self.n)
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
	def consulta(self,post_body):
		tbs="a"
		blks = post_body.split("&")
		for i in blks:
			v = i.split("=")
			tbs += ","+v[1]
		x=tbs.split(",")
		user=x[1]
		print("Usuario: "+str(user))
		BaseUConsulta = self.BaseU
		print("Base U Consulta")
		print(BaseUConsulta)
		BaseMConsulta = self.BaseM

		if user in BaseUConsulta:
			posicion=BaseUConsulta.index(user)
			print(str(BaseMConsulta[posicion]))
			r_content = "<h1>Messages sent via LoRa</h1>\n"
			r_content += "\n"
			r_content += str(BaseMConsulta[posicion]) + "\n"
			r_content += "\n"
			r_content += "<p><a href='/'>Back to home</a></p>\n"
		else:
			ingresoRegistro(sender)
			r_content = "<h1>No Messages</h1>\n"
			r_content += "\n"
			r_content += "\n"
			r_content += "<p><a href='/'>Back to home</a></p>\n"
		return r_content