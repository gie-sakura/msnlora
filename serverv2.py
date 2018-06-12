#!/usr/bin/python

# PM: based on http://blog.wachowicz.eu/?p=256
# PM: added POST handling
# import signal  # Signal support (server shutdown on signal receive)
# Kiyo: Agregado conexión a red local
# AM: Agregado funcionamiento entre dos dispositivos

import socket  # Networking support
from time import time    # Current time
import ubinascii
import binascii
import posthandlerv3 # PM: code to be executed to handle a POST
import swlpv3 #AM: Libreria transporte no recursiva
from tabla import BaseDatos #AM: Libreria Bases de Usuarios y mensajes
from network import LoRa #AM: Libreria de LoRa
import network
import select #AM: Libreria para cambiar entre sockets
import ufun #AM: Libreria para manejar los Leds
import machine
from network import WLAN
from machine import SD
import gc
import os
import utime


RED = 0xFF0000
YELLOW = 0xFFFF33
GREEN = 0x007F00
PINK=0x6b007f
BLUE= 0x005e63
OFF = 0x000000
WEB_PAGES_HOME_DIR = '/flash' # Directory where webpage files are stored
ANY_ADDR = b'FFFFFFFF'
flag = 0
DEBUG_MODE = True

class Server:
 """ Class describing a simple HTTP server objects."""

 def __init__(self, port = 80):
     """ Constructor """
     self.host = ''   # <-- works on all avaivable network interfaces
     self.port = port
     self.www_dir =  WEB_PAGES_HOME_DIR
     self.flag_null = 0
     self.userR = ""

 def activate_server(self):
     """ Attempts to aquire the socket and launch the server """
     self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     try: # user provided in the __init__() port may be unavaivable
         print("Launching HTTP server on ", self.host, ":",self.port)
         self.socket.bind((self.host, self.port))

     except Exception as e:
         print ("Warning: Could not acquire port:",self.port,"\n")
         print ("I will try a higher port")
         # store to user provided port locally for later (in case 8080 fails)
         user_port = self.port
         self.port = 8080

         try:
             print("Launching HTTP server on ", self.host, ":",self.port)
             self.socket.bind((self.host, self.port))

         except Exception as e:
             print("ERROR: Failed to acquire sockets for ports ", user_port, " and 8080. ")
             print("Try running the Server in a privileged user mode.")
             self.shutdown()
             import sys
             sys.exit(1)

     print ("Server successfully acquired the socket with port:", self.port)
     print ("Press Ctrl+C to shut down the server and exit.")
     print ("Awaiting New connection")
     self.socket.listen(3) # maximum number of queued connections

 def connectionLoRa(self):#Funcion para crear socket LoRa
    try:
        self.s_right = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.loramac = binascii.hexlify(network.LoRa().mac())
        print("socket creado") # AM: Adquisicion socket LoRa
    except socket.error:
        exit('Error creating socket.') 

 def shutdown(self):
     """ Shut down the server """
     try:
         print("Shutting down the server")
         s.socket.shutdown(socket.SHUT_RDWR)

     except Exception as e:
         print("Warning: could not shut down the socket. Maybe it was already closed...", e)


 def _gen_headers(self, code):
     """ Generates HTTP response Headers. """

     # determine response code
     h = ''
     if (code == 200):
        h = 'HTTP/1.1 200 OK\n'
     elif(code == 404):
        h = 'HTTP/1.1 404 Not Found\n'

     # write further headers
#     current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
# PM: should find an alternative for LoPys
     current_date = '4 Agosto 1965'
     h += 'Date: ' + current_date +'\n'
     h += 'Server: Simple-Python-HTTP-Server\n'
     h += 'Connection: close\n\n'  # signal that the conection will be closed after completing the request

     return h

 def _wait_for_connections(self,s_left,addr):
     print("Got connection from:", addr)
     ufun.set_led_to(GREEN)
     data = s_left.recv(1024) #receive data from client
     #if DEBUG_MODE: print("DEBUG: RAW INPUT DATA: ", data)
     treq = bytes.decode(data) #decode it to treq
     #determine request method  (HEAD and GET are supported) (PM: added support to POST )
     request_method = treq.split(' ')[0]
     print("DEBUG: self.flag_null", self.flag_null)
     if(self.flag_null==0):#AM: En caso de que sea peticion nula, la cambia a una GET
        treq2 = treq
        request_method2 = treq2.split(' ')[0]
        print("Datos para metodo null")
        self.flag_null = 1
     if(data=="b''"):
        treq = treq2
        request_method = request_method2
        print("Cambio de datos porque se recibio peticion null")
     print ("Method: ", request_method)
     print ("Full HTTP message: -->")
     print (treq)
     print ("<--")
     treqhead = treq.split("\r\n\r\n")[0]
     treqbody = treq[len(treqhead):].lstrip() # PM: makes easier to handle various types of newlines
     print ("only the HTTP body: -->")
     print (treqbody)
     print ("<--")

         # split on space "GET /file.html" -into-> ('GET','file.html',...)
     file_requested = treq.split(' ')
     if DEBUG_MODE: print("File Requested: ", file_requested)
     if(file_requested==''):
        file_requested = '/index.html'
     file_requested = file_requested[1] # get 2nd element

         #Check for URL arguments. Disregard them
     file_requested = file_requested.split('?')[0]  # disregard anything after '?'

     if (file_requested == '/'):  # in case no file is specified by the browser
             file_requested = '/index.html' # load index.html by default
     elif (file_requested == '/favicon.ico'):  # most browsers ask for this file...
             file_requested = '/index.html' # ...giving them index.html instead
     file_requested = self.www_dir + file_requested
     print ("Serving web page [",file_requested,"]")

# GET method
     if (request_method == 'GET') | (request_method == 'HEAD') :
    ## Load file content
         try:
             gc.collect()
             print("mem_free: ", gc.mem_free())
             file_handler = open(file_requested,'rb')
             if (request_method == 'GET'):  #only read the file when GET
                 response_content = file_handler.read() # read file content
             file_handler.close()
             response_headers = self._gen_headers( 200)
         except Exception as e: #in case file was not found, generate 404 page
             error_str = str(e)
             if (error_str[:24] == 'memory allocation failed'):
                print ("Warning, memory allocation failed. Serving response code 500"+" -> "+error_str)
                response_headers = self._gen_headers(500)
                if (request_method == 'GET'):
                    response_content = b"<html><body><p>Error 500: Memory allocation failed</p><p>Python HTTP server</p><p><a href='/'>Back to home</a></p></body></html>"
                else:
                    print ("Warning, file not found from GET. Serving response code 404\n", e)
                    response_headers = self._gen_headers( 404)
                    if (request_method == 'GET'):
                        response_content = b"<html><head><meta charset='utf-8'><title>LoRa</title></head><body><p>Error 404: File not found</p><p>Python HTTP server</p><p><a href='/'>Back to home</a></p></body></html>"
         server_response =  response_headers.encode() # return headers for GET and HEAD
         if (request_method == 'GET'):
             server_response +=  response_content  # return additional conten for GET only
         s_left.send(server_response)
         print ("Closing connection with client")
         ufun.set_led_to(OFF)
         s_left.close()

# POST method
     elif (request_method == 'POST'):
             ## Load file content
         try:
             total_time= utime.ticks_ms()
             if (file_requested.find("execposthandler") != -1):
                 print("... PM: running python code")
                 #total_time= utime.ticks_ms()
                 if DEBUG_MODE: print("DEBUG: lenght message:",len(treqbody))
                 if (len(treqbody) > 25):
                     response_content, search_time = posthandlerv3.run(treqbody,self.s_right,self.loramac,self.userR)
                     total_time_final = utime.ticks_ms() - total_time
                     stt = total_time_final - search_time
                     if DEBUG_MODE: print("DEBUG: Total Time:",total_time_final)
                     if DEBUG_MODE: print("DEBUG: STT:",stt)
                 else:
	                 print("... PM: empty POST received")
	                 response_content = b"<html><body><p>Error: EMPTY FORM RECEIVED, Please Check Again</p><p>Python HTTP server</p><p><a href='/'>Back to home</a></p></body></html>"
             elif (file_requested.find("tabla") != -1):
                 print("AM: Consulta mensajes")
                 tabla=BaseDatos()
                 response_content = tabla.consulta(self.userR)
             elif (file_requested.find("registro") != -1):
                 print("AM: Registro")
                 tabla=BaseDatos()
                 if (len(treqbody) > 12 ):
                     response_content,self.userR = tabla.ingresoRegistro(treqbody)
                     print("Register Ok")
                 else:
                     print("... PM: empty POST received")
                     response_content = b"<html><body><p>Error: Please Choose a username</p><p>Python HTTP server</p><p><a href='/'>Back to home</a></p></body></html>"
             else:
                 file_handler = open(file_requested,'rb')
                 response_content = file_handler.read() # read file content
                 file_handler.close()

             response_headers = self._gen_headers(200)
         except Exception as e: #in case file was not found, generate 404 page
             print ("Warning, file not found. Serving response code 404\n", e)
             response_headers = self._gen_headers(404)
             response_content = b"<html><body><p>Error 404: File not found</p><p>Python HTTP server</p><p><a href='/'>Back to home</a></p></body></html>"

         server_response =  response_headers.encode() # return headers
         server_response +=  response_content  # return additional content
         s_left.send(server_response)
         print ("Closing connection with client")
         ufun.set_led_to(OFF)
         s_left.close()

     else:
         print("Unknown HTTP request method:", request_method)

 def conexion(self): #Funcion encargada de coordinar uso de los sockets
    ANY_ADDR = b'FFFFFFFFFFFFFFFF'
    while True:
        s_read, _, _ = select.select([self.socket, self.s_right], [], [])          
        for a in s_read:
            if a == self.socket:
                # reading data from the HTTP channel
                print("DEBUG: in connections_handler: reading data from the HTTP channel")
                s_left, addr = self.socket.accept()
                self._wait_for_connections(s_left,addr)
                #time.sleep(4) #AM: Retardo para cerrar conexiones http
            elif a == self.s_right:
                # reading data from the LORA channel using swlpv3
                print("DEBUG: reading data from the LORA channel using swlpv3")
                ufun.flash_led_to(YELLOW)
                data,sender = swlpv3.trecvcontrol(self.s_right, my_lora_address, ANY_ADDR)
                LoRaRec(data,self.s_right,sender)
                print("DEBUG: done reading data from the LORA channel using swlpv3")
                print(data)
                print("The End.")
                ufun.flash_led_to(OFF)
###################################################################################

def LoRaRec(data,socket,source_address):
    mensaje = b""
    my_lora_address = binascii.hexlify(network.LoRa().mac())
    print("DEBUG: Content in reception LoRa",data)
    print(source_address)
    if (source_address == ANY_ADDR):
        content2 = str(data)
        IPlora,usuario = content2.split(",")
        print("IP Lora: "+str(IPlora))
        lenght = len(usuario)
        userf = usuario[:lenght-1]
        IPloraf = IPlora[4:]
        print("usuario "+str(userf))
        bandera=tabla.consultaControl(userf)
        print("flag")
        print(bandera)
        if bandera == 1:
            print("En tsend"+str(IPloraf))
            sent, retrans,sent = swlpv3.tsend(my_lora_address, socket, my_lora_address, IPloraf)
    elif(source_address== my_lora_address[8:]):
        mensaje = data
        print("El mensaje en serverv2")
        print(mensaje)
        if(mensaje !=b""):
            mensajet = str(mensaje)
            idEmisor, mensajef,usuario = mensajet.split(",")
            print("Emisor: "+str(idEmisor[1:]))
            print("Mensaje: "+str(mensajef))
            print("Usuario: "+str(usuario))
            lenght = len(usuario)
            userf = usuario[:lenght-1]
            tabla.ingreso(idEmisor,userf,mensaje)

################################################################################################################################
# Enabling garbage collection
gc.enable()
gc.collect()
print("mem_free: ", gc.mem_free())
sd = SD()
os.mount(sd, '/sd')
print("SD Card Enabled")
lora = LoRa(mode=LoRa.LORA) #Inicializando LoRa
lora.sf(7)# Set Spread Factor
# AM: Se configura la lopy como punto de Acceso y servidor HTTP
# PM: choosing random name for lopy
lopy_name = "messenger"+str(ufun.random_in_range())
wlan = WLAN(mode=WLAN.STA_AP, ssid=lopy_name)
wlan.init(mode=WLAN.STA_AP, ssid=lopy_name, auth=None, channel=7, antenna=WLAN.INT_ANT)
print("Red Name: "+str(lopy_name))
print ("Starting web server")
tabla=BaseDatos() #Instanciamiento Clase Base de Datos
s = Server(80)  # construct server object
my_lora_address = binascii.hexlify(network.LoRa().mac())
s.activate_server() # acquire the socket
s.connectionLoRa() #Acquire Socket LoRa
s.conexion()