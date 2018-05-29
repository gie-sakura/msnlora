from network import LoRa
import socket
import machine
import time
import binascii
import network
import swlpv3
import struct
import ufun
from tabla import BaseDatos #AM: Libreria Bases de Usuarios y mensajes

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

# Creacion subpaquete
def make_subpacket(TipoMensaje, TipoPaquete, content):
    
    Paquete = 0
    Mensaje = 0
    if TipoPaquete: Paquete = Paquete | (1<<0) #Falso para Audio, True para texto
    if TipoMensaje: Mensaje = Mensaje | (1<<0) # Falso para Control, True para Texto

    header = struct.pack(HEADER_FORMAT, Mensaje, Paquete)
    return header + content

# AM: Funcion para desempaquetar
def unpack(packet):
    header  = packet[:HEADER_SIZE]
    content = packet[HEADER_SIZE:]

    TM, TP = struct.unpack(HEADER_FORMAT, header)
    
    return TM, TP, content    

def reconocimiento(the_sock, tbs):
    # AM: Envío paquete de reconocimiento para saber donde enviar mensaje
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
        print("buscando ")
        print(cuenta)
        sent,retrans,nsent = swlpv3.tsend(content, the_sock, my_lora_address, dest_lora_address)
        mensaje,address = swlpv3.trecvcontrol(the_sock, my_lora_address, dest_lora_address)
        print("mensaje ")
        print(mensaje)
        #
        cuenta+=1
        print(cuenta)
        if(mensaje!=b""):
            #TM, TP, content = unpack(mensaje)
            #mensaje =content
            break
        elif(cuenta==3 and mensaje==b""):
            print("El mensaje")
            print(mensaje)
            break
    return mensaje

def run(post_body,socket,mac,sender):
    tabla=BaseDatos()
    print("Entrada posthandler")
    ufun.set_led_to(BLUE)
    dest_lora_address =b""
    # PM: extracting data to be sent from passed POST body 
    blks = post_body.split("&")
    print(blks)
    tbs=str(mac)
    for i in blks:
        v = i.split("=")
        tbs += ","+v[1]
    print("tbs")
    print(tbs)
    loramac, receiver, message=tbs.split(",")
    # AM: Revisando a donde enviar y enviando
    dest_lora_address = reconocimiento(socket, receiver)
    print("dest lora address")
    dest_lora_address2 = dest_lora_address[2:]
    print(dest_lora_address2)
    #sent, retrans,nsent = swlpv3.tsend(tbs, socket, mac, message)
    if(dest_lora_address != b""):
        start_time = time()
        aenvio = str(sender)+","+str(message)+","+str(receiver) # AM: cuando se tiene direccion de envio, envia ID del emisor y el mensaje
        print("aenvio: "+aenvio)
        sent, retrans,sent = swlpv3.tsend(aenvio, socket, mac, dest_lora_address)
        print("Enviado")
        elapsed_time = time() - start_time
        print("Tiempo de Envio: %0.10f seconds." % elapsed_time)
        ufun.set_led_to(OFF)
        #receiver = tabla.ingresoRegistro(sender)
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