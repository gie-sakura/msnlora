from network import LoRa
import socket
import machine
from time import time    # Current time
import binascii
import network
import swlp #Stop and Wait Protocol
import struct
import ufun
from tabla import BaseDatos #AM: Libreria Bases de Usuarios y mensajes
import utime

ANY_ADDR = b'FFFFFFFFFFFFFFFF'
MAX_PKT_SIZE_REC = 32  # Must determine which is the maximum pkt size in LoRa...
HEADER_FORMAT = "BB"
HEADER_SIZE = 2
# header structure:
# 1B: Tipo de Archivo
# 1B: Tipo de Paquete 
PAYLOAD_SIZE = MAX_PKT_SIZE_REC - HEADER_SIZE
DATA_PACKET = False
RED = 0xFF0000
YELLOW = 0xFFFF33
GREEN = 0x007F00
PINK=0x6b007f
BLUE= 0x005e63
OFF = 0x000000
DEBUG_MODE = True

# AM: subpacket creation not implemented
def make_subpacket(TipoMensaje, TipoPaquete, content):
    
    Paquete = 0
    Mensaje = 0
    if TipoPaquete: Paquete = Paquete | (1<<0) #False for Audio, True for plain text
    if TipoMensaje: Mensaje = Mensaje | (1<<0) # False for Control, True for payload

    header = struct.pack(HEADER_FORMAT, Mensaje, Paquete)
    return header + content

# AM: Unpack, not implemented
def unpack(packet):
    header  = packet[:HEADER_SIZE]
    content = packet[HEADER_SIZE:]

    TM, TP = struct.unpack(HEADER_FORMAT, header)
    
    return TM, TP, content    

def reconocimiento(the_sock, tbs):
    # AM: We send a broadcast message looking for the user
    mensaje = ""
    content= ""
    cuenta = 0
    address = b""
    lora = LoRa(mode=LoRa.LORA)
    my_lora_address = binascii.hexlify(network.LoRa().mac())
    dest_lora_address = b'FFFFFFFFFFFFFFFF'
    content=str(str(my_lora_address)+","+str(tbs))
    if DEBUG_MODE: print("DEBUG: Content: ", content)
    if DEBUG_MODE: print("DEBUG: Searching: ", tbs)
    # AM: Se establece un tiempo de búsqueda de usuario de 20 segundos
    while True:
        if DEBUG_MODE: print("DEBUG: Searching: ", cuenta)
        sent,retrans,nsent = swlp.tsend(content, the_sock, my_lora_address, dest_lora_address)
        mensaje,address = swlp.trecvcontrol(the_sock, my_lora_address, dest_lora_address)
        if DEBUG_MODE: print("DEBUG: Message: ", mensaje)
        if DEBUG_MODE: print("DEBUG: Retransmisions",retrans)
        cuenta+=1
        if(mensaje!=b""): #We found the user receiver
            break
        elif(cuenta==3 and mensaje==b""):
            if DEBUG_MODE: print("DEBUG: Message when destination not found: ", mensaje)
            break
    return mensaje

def run(post_body,socket,mac,sender):
    tabla=BaseDatos()
    ufun.set_led_to(BLUE)
    dest_lora_address =b""
    # PM: extracting data to be sent from passed POST body 
    blks = post_body.split("&")
    if DEBUG_MODE: print("DEBUG: Data received from the form: ", blks)
    tbs=str(mac)
    for i in blks:
        v = i.split("=")
        tbs += ","+v[1]
    if DEBUG_MODE: print("DEBUG: tbs: ", tbs)
    loramac, receiver, message=tbs.split(",")
    # AM: Checking where to send the message
    start_search_time = utime.ticks_ms()
    dest_lora_address = reconocimiento(socket, receiver)
    search_time = utime.ticks_ms() - start_search_time
    dest_lora_address2 = dest_lora_address[2:]
    if DEBUG_MODE: print("DEBUG: dest lora address: ", dest_lora_address2)
    if DEBUG_MODE: print("DEBUG: Search Destination time: %0.10f mseconds."% search_time)
    if(dest_lora_address != b""):
        start_time = utime.ticks_ms()
        aenvio = str(sender)+","+str(message)+","+str(receiver) # AM: cuando se tiene direccion de envio, envia ID del emisor y el mensaje
        if DEBUG_MODE: print("DEBUG: Payload to be sent: ", aenvio)
        sent, retrans,sent = swlp.tsend(aenvio, socket, mac, dest_lora_address)
        elapsed_time = utime.ticks_ms() - start_time
        if DEBUG_MODE: print("DEBUG: Sent OK, Message time: %0.10f mseconds."% elapsed_time)
        if DEBUG_MODE: print("DEBUG: Retransmisions",retrans)
        if DEBUG_MODE: print("DEBUG: Segments sent:",sent)
        ufun.set_led_to(OFF)
        # PM: creating web page to be returned
        r_content = "<h1>Message sent via LoRa</h1>\n"
        r_content += "\n"
        r_content += tbs + "\n"
        r_content += "\n"
        r_content += "<p><a href='/'>Back to home</a></p>\n"
    else:
        ufun.set_led_to(OFF)
        r_content = "<h1>Destination Not found\n"
        r_content += "<h1><a href='/'>Back To Home</a></h1>\n"
    return r_content