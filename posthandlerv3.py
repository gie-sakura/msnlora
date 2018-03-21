from network import LoRa
import socket
import machine
import time
import binascii
import network
import swlpv3
import struct

ANY_ADDR = b'FFFFFFFFFFFFFFFF'
MAX_PKT_SIZE_REC = 24  # Must determine which is the maximum pkt size in LoRa...
HEADER_FORMAT = "BB"
HEADER_SIZE = 2
# header structure:
# 1B: Tipo de Archivo
# 1B: Tipo de Paquete 
PAYLOAD_SIZE = MAX_PKT_SIZE_REC - HEADER_SIZE
DATA_PACKET = False

# Creacion subpaquete
def make_subpacket(TipoMensaje, TipoPaquete, content):
    
    Paquete = 0
    Mensaje = 0
    if TipoPaquete: Paquete = Paquete | (1<<0) #Falso para Audio, True para texto
    if TipoMensaje: Mensaje = Mensaje | (1<<0) # Falso para Control, True para Texto

    header = struct.pack(HEADER_FORMAT, source_addr, Mensaje, Paquete)
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
    lora = LoRa(mode=LoRa.LORA)
    my_lora_address = binascii.hexlify(network.LoRa().mac())
    dest_lora_address = b'FFFFFFFFFFFFFFFF'
    content=str(my_lora_address)+","+str(tbs)
    paquete = make_subpacket(False, True, content)
    print('buscando a... '+tbs)
    the_sock.settimeout(3) # AM: Se establece un tiempo de búsqueda de usuario de 20 segundos
    while True:
        try:
            print("buscando")
            sent, retrans = swlpv3.tsend(paquete, the_sock, my_lora_address, dest_lora_address)
            mensaje = swlpv3.trecv(the_sock, my_lora_address, sender_lora_address)
            TM, TP, content = unpack(mensaje)
        except socket.timeout:
            sent, retrans = swlpv3.tsend(paquete, the_sock, my_lora_address, dest_lora_address)
            cuenta+=1
            print(cuenta)
        if(cuenta==7 and mensaje == ""):
            break
    return mensaje

def run(post_body,socket,mac):
    print("Entrada posthandler")
    #lora = LoRa(mode=LoRa.LORA)
    #loramac = binascii.hexlify(network.LoRa().mac())
    # PM: extracting data to be sent from passed POST body 
    blks = post_body.split("&")
    print(blks)
    tbs=str(mac)
    for i in blks:
        v = i.split("=")
        tbs += ","+v[1]
    print("tbs")
    print(tbs)
    loramac,sender, receiver, message=tbs.split(",")
    # AM: Revisando a donde enviar y enviando
    #dest_lora_address = reconocimiento(socket, receiver)
    sent, retrans = swlpv3.tsend(aenvio, socket, loramac, message)
    if(dest_lora_address != ""):
        aenvio = str(sender)+","+str(message) # AM: cuando se tiene direccion de envio, envia ID del emisor y el mensaje
        sent, retrans = swlpv3.tsend(aenvio, socket, loramac, message)
        BaseU, BaseM = tabla.BaseDatos.ingresoRegistro(sender)
        # PM: creating web page to be returned
        r_content = "<h1>Message sent via LoRa</h1>\n"
        r_content += "\n"
        r_content += tbs + "\n"
        r_content += "\n"
        r_content += "<p><a href='/'>Back to home</a></p>\n"
    else:
        r_content = "<h1>Destino inalcanzable</h1>\n"
        r_content += "\n"
        r_content += "<p><a href='/'>Back to home</a></p>\n"
    return r_content