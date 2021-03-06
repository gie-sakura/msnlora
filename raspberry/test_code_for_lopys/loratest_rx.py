from network import LoRa
import binascii
import machine
import network
import socket
import sys
import time
import swlp

# check if string is empty
def isNotBlank (myString):
    return bool(myString and myString.strip())

# —------------------------------------
# Initialize LoRa in LORA mode.
#lora = LoRa(mode=LoRa.LORA)
# lora = LoRa(mode=LoRa.LORA, frequency=868000000, sf=8, bandwidth=LoRa.BW_125KHZ, coding_rate=LoRa.CODING_4_5)

freq=869000000                  # def.: frequency=868000000         
tx_pow=14                       # def.: tx_power=14                 
band=LoRa.BW_125KHZ             # def.: bandwidth=LoRa.868000000    
spreadf=7                       # def.: sf=7                        
prea=8                          # def.: preamble=8                  
cod_rate=LoRa.CODING_4_5        # def.: coding_rate=LoRa.CODING_4_5 
pow_mode=LoRa.ALWAYS_ON         # def.: power_mode=LoRa.ALWAYS_ON   
tx_iq_inv=False                 # def.: tx_iq=false                 
rx_iq_inv=False                 # def.: rx_iq=false                 
ada_dr=False                    # def.: adr=false                   
pub=False                       # def.: public=true                 
tx_retr=1                       # def.: tx_retries=1                
dev_class=LoRa.CLASS_A          # def.: device_class=LoRa.CLASS_A   

ANY_ADDR = b'FFFFFFFFFFFFFFFF'

lora = LoRa(mode=LoRa.LORA,
        frequency=freq,         
        tx_power=tx_pow,               
        bandwidth=band,    
        sf=spreadf,                       
        preamble=prea,               
        coding_rate=cod_rate,
        power_mode=pow_mode,  
        tx_iq=tx_iq_inv,                
        rx_iq=rx_iq_inv,                
        adr=ada_dr,                  
        public=pub,       
        tx_retries=tx_retr,              
        device_class=dev_class)

# Get loramac as id to be sent in message
lora_mac = binascii.hexlify(network.LoRa().mac()).decode('utf8')
print(lora_mac)

# Create a raw LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# mr add 27/07
# s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

tStartMsec = time.ticks_ms()
LoraStats = ""                          # init lora stats
print("Start lora rx")
while True:
    #### # get any data received...
    #s.setblocking(True)
    print("Recibiendo")

    #dataRx,a = swlp.trecvcontrol(s, lora_mac, ANY_ADDR)
    dataRx = s.recv(64)
    LoraStats = lora.stats()            # get lora stats

    if isNotBlank (dataRx):
        print("rx[{}] stats[{}]".format(dataRx, LoraStats))

    # wait a random amount of time
    # time.sleep(machine.rng() & 0x07)
