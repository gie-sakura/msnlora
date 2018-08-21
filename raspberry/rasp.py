import sys
import time
from hoperf.LoRa import *
from hoperf.LoRaArgumentParser import LoRaArgumentParser
from hoperf.board_config import BOARD
import hashlib
import binascii
import signal
import struct
import socket

DEBUG_MODE = True
socket.setdefaulttimeout(10)
BOARD.setup()

parser = LoRaArgumentParser("A simple LoRa beacon")
parser.add_argument('--single', '-S', dest='single', default=False, action="store_true", help="Single transmission")
parser.add_argument('--wait', '-w', dest='wait', default=1, action="store", type=float, help="Waiting time between transmissions (default is 0s)")

DATA_PACKET = False
ANY_ADDR = b'FFFFFFFF'
# BEGIN: Utility functions
#

class Lora(LoRa):

    tx_counter = 0    

    def __init__(self, verbose=False):
        super(Lora, self).__init__(verbose)
        MAX_PKT_SIZE = 230
        self.HEADER_FORMAT = "!8s8sHHB3s"
        # header structure:
        # 8B: source addr (last 8 bytes)
        # 8B: dest addr (last 8 bytes)
        # 2B: seqnum 
        # 2B: acknum
        # 1B: flags
        # 3B: checksum
        self.HEADER_SIZE = 24
        self.PAYLOAD_SIZE = MAX_PKT_SIZE - self.HEADER_SIZE

    def handler(self,signum, frame):
        
        raise Exception("Exception")

    def make_packet(self,source_addr, dest_addr, seqnum, acknum, is_a_ack, last_pkt, content):
        flags = 0
        if last_pkt: flags = flags | (1<<0)
        if is_a_ack: flags = flags | (1<<4)
        check = self.get_checksum(content)
        header = struct.pack(self.HEADER_FORMAT, source_addr, dest_addr, seqnum, acknum, flags, check)
        return header + content

    # Break a packet into its component parts
    def unpack(self,packet):
        header  = packet[:self.HEADER_SIZE]
        content = packet[self.HEADER_SIZE:]
        sp, dp, seqnum, acknum, flags, check = struct.unpack(self.HEADER_FORMAT, header)
        is_a_ack = (flags >> 4) == 1
        last_pkt = (flags & 1)  == 1
        return sp, dp, seqnum, acknum, is_a_ack, last_pkt, check, content

    def get_checksum(self,data):
        h = hashlib.sha256(data)
        ha = binascii.hexlify(h.digest())
        return ha[-3:]

    def debug_printpacket(self,msg, packet, cont=False):
        sp, dp, seqnum, acknum, is_a_ack, last_pkt, check, content = self.unpack(packet)
        if cont:
            print("{}: s_p: {}, d_p: {}, seqn: {}, ackn: {}, ack: {}, fin: {}, check: {}, cont: {}".format(msg, sp, dp, seqnum, acknum, is_a_ack, last_pkt, check, content))
        else:
            print("{}: s_p: {}, d_p: {}, seqn: {}, ackn: {}, ack: {}, fin: {}, check: {}".format(msg, sp, dp, seqnum, acknum, is_a_ack, last_pkt, check))

    def on_rx_done(self):
        #signal.alarm(10)
        BOARD.led_on()
        if(self.env==0):
            if DEBUG_MODE: print("DEBUG: Reception")
            if DEBUG_MODE: print("DEBUG: From Swlp My Address: ", self.MY_ADDR)
            #print("\nRxDone")
            #print(self.get_irq_flags())
            packetn = self.read_payload(nocheck=True)
            packet=''.join(chr(i) for i in packetn)
            if DEBUG_MODE: print("packet", packet)
            if(packet==""):
                if DEBUG_MODE: print("ERROR: packet received not valid")
            else:
                if(self.fpacket==True):
                    self.source_addr, dest_addr, seqnum, acknum, ack, self.last_pkt, check, content = self.unpack(packet)
                    address_check = dest_addr
                    if (dest_addr==self.MY_ADDR):
                        self.flag_recv = True
                    else:
                        if DEBUG_MODE: self.debug_printpacket("DISCARDED received packet; not for me!!", packet)
                        self.set_mode(MODE.SLEEP)
                    if(self.flag_recv==True):
                        if DEBUG_MODE: self.debug_printpacket("received 1st packet", packet, True)
                        checksum_OK = (check == self.get_checksum(content))
                        if (checksum_OK) and (self.next_acknum == acknum):
                            packet_valid = True
                            self.rcvd_data += content
                            self.next_acknum += 1
                            if DEBUG_MODE: print("DEBUG: Data So far: ", self.rcvd_data)
                            if DEBUG_MODE: print("DEBUG: acknum So far: ", self.next_acknum)
                        else:
                            packet_valid = False
                    # Sending first ACK
                        ack_segment = self.make_packet(self.MY_ADDR, self.source_addr, seqnum, acknum, packet_valid, self.last_pkt, "")
                        self.write_payload([ord(elem) for elem in ack_segment])
                        time.sleep(.5)
                        self.set_mode(MODE.SLEEP)
                        self.set_dio_mapping([1,0,0,0,0,0])
                        self.set_mode(MODE.TX)
                        if DEBUG_MODE: self.debug_printpacket("sent 1st ACK", ack_segment)
                        self.fpacket=False
                        time.sleep(2)
                        self.set_mode(MODE.SLEEP)
                        self.set_dio_mapping([0] * 6)
                        self.reset_ptr_rx()
                        BOARD.led_off()
                        self.set_mode(MODE.RXCONT)
                if(self.fpacket==False and self.last_pkt==False):
                    if DEBUG_MODE: print("DEBUG: acknum Of the second Packet: ", self.next_acknum)
                    self.source_addr, dest_addr, seqnum, acknum, ack, self.last_pkt, check, content = self.unpack(packet)
                    if (dest_addr==self.MY_ADDR):
                        if DEBUG_MODE: self.debug_printpacket("received packet", packet, True)
                        checksum_OK = (check == self.get_checksum(content))
                        if DEBUG_MODE: print("checksum_OK",checksum_OK)
                    # ACK the packet if it's correct; otherwise send NAK.
                        if (checksum_OK) and (self.next_acknum == acknum):
                            packet_valid = True
                            self.rcvd_data += content
                            self.next_acknum += 1
                            if DEBUG_MODE: print("DEBUG: Data So far: ", self.rcvd_data)
                        else:
                            packet_valid = False
                        ack_segment = self.make_packet(self.MY_ADDR, self.source_addr, seqnum, acknum, packet_valid, self.last_pkt, "")
                        self.write_payload([ord(elem) for elem in ack_segment])
                        time.sleep(1)
                        self.set_mode(MODE.SLEEP)
                        self.set_dio_mapping([1,0,0,0,0,0])
                        self.set_mode(MODE.TX)
                        if DEBUG_MODE: self.debug_printpacket("sending ACK", ack_segment)
                        if DEBUG_MODE: print("DEBUG: last_pkt so far: ", self.last_pkt)
                        if(self.last_pkt==False):
                            time.sleep(.5)
                            self.set_mode(MODE.SLEEP)
                            self.set_dio_mapping([0] * 6)
                            self.reset_ptr_rx()
                            BOARD.led_off()
                            self.set_mode(MODE.RXCONT)
                        else:
                            time.sleep(.5)
                            self.set_mode(MODE.SLEEP)
                            self.flag=1
                    else:
                        if DEBUG_MODE: self.debug_printpacket("DISCARDED received packet; not for me!!", packet)
                else:
                    time.sleep(.5)
                    self.set_mode(MODE.SLEEP)
                    self.flag=1
        elif(self.env==1):
            if DEBUG_MODE: print("DEBUG: Waiting for ACK")
            if DEBUG_MODE: print("SND_ADDR", self.snd_add)
            #print("\nRxDone")
            #print(self.get_irq_flags())
            ackn = self.read_payload(nocheck=True)
            ack=''.join(chr(i) for i in ackn)
            if DEBUG_MODE: print("ack", ack)
            if(ack==""):
                print("ERROR: packet received not valid")
            else:
                try:
                    ack_source_addr, ack_dest_addr, ack_seqnum, ack_acknum, ack_is_ack, ack_final, ack_check, ack_content = self.unpack(ack)
                    self.recv_time = time.time()
                    if (ack_seqnum == 0 and self.bandera ==0):
                        self.rcv2 = ack_source_addr
                        self.bandera = 1
                        if DEBUG_MODE: print("DEBUG: rcv2",self.rcv2)
                    if DEBUG_MODE: self.debug_printpacket("received ack", ack)
                    if DEBUG_MODE: print("DEBUG: ack_source_addr",ack_source_addr)
                    if ack_final:
                        self.flag=1
                        print(self.flag)
                        if DEBUG_MODE: print("DEBUG: last packet")
                        time.sleep(.5)
                        self.set_mode(MODE.SLEEP)
                        print(self.frx)
                        # If valid, here we go!
                    elif (ack_is_ack) and (ack_acknum == self.acknum) and (self.rcv2==ack_source_addr):
                        self.frx=1
                        time.sleep(1)
                        self.set_mode(MODE.SLEEP)
                        self.set_dio_mapping([1,0,0,0,0,0])
                        self.reset_ptr_rx()
                        self.set_mode(MODE.TX)
                        self.flagsend=1
                    else:
                        if DEBUG_MODE: print("ERROR: packet not for me")
                        self.set_mode(MODE.SLEEP)
                        self.reset_ptr_rx()
                        BOARD.led_off()
                        self.set_mode(MODE.RXCONT)
                except socket.timeout:
                    print("Entra a la excepcion")
                    time.sleep(.5)
                    self.frx=2
                    signal.alarm(120)
                    self.set_mode(MODE.SLEEP)
                    self.set_dio_mapping([1,0,0,0,0,0])
                    self.reset_ptr_rx()
                    self.set_mode(MODE.TX)

    def on_tx_done(self):
        global args
        if(self.env==1):
            if DEBUG_MODE: print("DEBUG: transmission")
            #print(self.frx)
            self.a=1
            self.set_mode(MODE.STDBY)
            self.clear_irq_flags(TxDone=1)
            sys.stdout.flush()
            #packet="Paquete 2"
            if(self.flag==0):
                self.set_mode(MODE.TX)
            else:
                self.set_mode(MODE.STDBY)
                self.clear_irq_flags(TxDone=1)
                self.set_mode(MODE.SLEEP)
            time.sleep(.5)
            #self.write_payload([ord(elem) for elem in packet])
            if(self.frx==0):
                print(self.frx)
                self.set_mode(MODE.SLEEP)
                self.set_dio_mapping([0] * 6)
                self.reset_ptr_rx()
                BOARD.led_off()
                self.set_mode(MODE.RXCONT)
            elif(self.frx==2):
                print(self.frx)
                packet = self.make_packet(self.snd_add, self.rec_add, self.seqnum, self.acknum, DATA_PACKET, self.last_pkt, self.text)
                self.write_payload([ord(elem) for elem in packet])
                self.flagn +=1
                if DEBUG_MODE: self.debug_printpacket("re-sending packet: ", packet)
                if DEBUG_MODE: print("From rasp Flag Number: ", self.flagn)
                self.sent += 1
                self.retrans += 1
                if(self.flagn==3):   #AM: Para no dejar el socket colgado se pone un reenvio de 3 paquetes
                    self.dentro= True
                    self.set_mode(MODE.SLEEP)
                self.frx=0
            elif(self.frx==1):
                print(self.frx)
                self.sample_rtt = self.recv_time - self.send_time
                if self.estimated_rtt == -1:
                    self.estimated_rtt = self.sample_rtt
                else:
                    self.estimated_rtt = self.estimated_rtt * 0.875 + self.sample_rtt * 0.125
                    self.dev_rtt = 0.75 * self.dev_rtt + 0.25 * abs(self.sample_rtt - self.estimated_rtt)
                if DEBUG_MODE: print("Payload left", self.payload)
                self.text=self.payload[0:self.PAYLOAD_SIZE]   # Copying PAYLOAD_SIZE bytes header from the input string
                if DEBUG_MODE: print("Payload to send", self.text)
                self.payload = self.payload[self.PAYLOAD_SIZE:]    # Shifting the input string
                if DEBUG_MODE: print("Payload left", self.payload)
                if (len(self.text) == self.PAYLOAD_SIZE) and (len(self.payload) > 0): 
                    self.last_pkt = False
                else: 
                    self.last_pkt = True
                    self.bandera = 0
                    # Increment sequence and ack numbers
                self.seqnum += 1
                self.acknum += 1
                RCV_ADDR = self.rcv2
                packet = self.make_packet(self.snd_add, RCV_ADDR, self.seqnum, self.acknum, DATA_PACKET, self.last_pkt, self.text)
                self.write_payload([ord(elem) for elem in packet])           
                self.sent += 1 
                if DEBUG_MODE: self.debug_printpacket("sending new packet", packet, True)
                signal.alarm(120)
                self.frx=0
        elif(self.env==0):
            if DEBUG_MODE: print("DEBUG: Receiving")
            self.a=1

    def on_cad_done(self):
        print("\non_CadDone")
        print(self.get_irq_flags())

    def on_rx_timeout(self):
        print("\non_RxTimeout")
        print(self.get_irq_flags())

    def on_valid_header(self):
        print("\non_ValidHeader")
        print(self.get_irq_flags())

    def on_payload_crc_error(self):
        print("\non_PayloadCrcError")
        print(self.get_irq_flags())

    def on_fhss_change_channel(self):
        print("\non_FhssChangeChannel")
        print(self.get_irq_flags())

    def recv(self,MY_ADDR,SND_ADDR):
        if DEBUG_MODE: print("DEBUG: Reception Function")
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        self.flag=0
        self.flag_recv = False
        self.MY_ADDR = MY_ADDR[8:]
        self.SND_ADDR = SND_ADDR[8:]
        address_check = b""
        self.fpacket=True
        self.source_addr=b""
        # Buffer storing the received data to be returned
        self.rcvd_data = b""
        self.next_acknum = 0
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        self.env=0
        while (self.flag==0):
            #sys.stdout.write("Entra en el while")
            time.sleep(.5)
        return self.rcvd_data, self.source_addr

    def trans(self,payload,SND_ADDR,RCV_ADDR):
        if DEBUG_MODE: print("DEBUG: Transmission Function")
        self.env=1
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([1,0,0,0,0,0])
        global args
        #signal.signal(signal.SIGALRM, self.handler)
        self.flag=0
        self.payload=payload
        self.rec_add = RCV_ADDR
        self.seqnum = 0
        self.acknum = 0
        self.sent    = 0
        self.retrans = 0
        self.bandera = 0
        self.flagn = 0
        self.nsent = 0
        self.timeout_time    =  1    # 1 second
        self.estimated_rtt   = -1
        self.dev_rtt         =  1
        sys.stdout.write("\rstart")
        self.tx_counter = 0
        self.frx=0
        BOARD.led_on()
        if DEBUG_MODE: print("RCV_ADDR", RCV_ADDR)
        self.snd_add = SND_ADDR[8:]
        self.rec_add = RCV_ADDR[8:]
        if DEBUG_MODE: print("New RCV_ADDR", self.rec_add)
        if DEBUG_MODE: print("SND_ADDR", self.snd_add)
        # Reads first block from string "payload"
        self.text=self.payload[0:self.PAYLOAD_SIZE]    # Copying PAYLOAD_SIZE bytes header from the input string
        self.payload = self.payload[self.PAYLOAD_SIZE:]    # Shifting the input string
        # Checking if this is the last packet
        if (len(self.text) == self.PAYLOAD_SIZE) and (len(self.payload) > 0):
            self.last_pkt = False
        else:
            self.last_pkt = True
            self.bandera = 0 
        packet = self.make_packet(self.snd_add, self.rec_add, self.seqnum, self.acknum, DATA_PACKET, self.last_pkt, self.text)
        self.write_payload([ord(elem) for elem in packet])
        if DEBUG_MODE: self.debug_printpacket("sending 1st", packet)
        self.send_time = time.time()
        time.sleep(.5)
        self.set_mode(MODE.TX)
        self.sent += 1
        self.dentro=False
        #time.sleep(1)
        #self.clear_irq_flags(TxDone=1)
        #signal.alarm(600)
        print("Entra en send 3")
        while(True):
            #print("Entra al while")
            time.sleep(.5)
            if(self.flag==1):
                time.sleep(1)
                self.set_mode(MODE.STDBY)
                self.set_mode(MODE.SLEEP)
                break
        return(self.sent,self.retrans,self.sent)
