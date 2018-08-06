import sys
from time import sleep
from hoperf.LoRa import *
from hoperf.LoRaArgumentParser import LoRaArgumentParser
from hoperf.board_config import BOARD
import hashlib
import binascii
import signal
import struct


DEBUG_MODE = True
BOARD.setup()

parser = LoRaArgumentParser("A simple LoRa beacon")
parser.add_argument('--single', '-S', dest='single', default=False, action="store_true", help="Single transmission")
parser.add_argument('--wait', '-w', dest='wait', default=1, action="store", type=float, help="Waiting time between transmissions (default is 0s)")

DATA_PACKET = False
ANY_ADDR = b'FFFFFFFF'
# BEGIN: Utility functions
#

class Lorarcv(LoRa):

    tx_counter = 0
      # Must determine which is the maximum pkt size in LoRa with Spread Factor 7... 
    

    def __init__(self, verbose=False):
        super(Lorarcv, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
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
        print("Entra a rx")
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
                    sleep(.5)
                    self.set_mode(MODE.SLEEP)
                    self.set_dio_mapping([1,0,0,0,0,0])
                    self.set_mode(MODE.TX)
                    if DEBUG_MODE: self.debug_printpacket("sent 1st ACK", ack_segment)
                    self.fpacket=False
                    sleep(2)
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
                        print("Entra al checksum")
                        packet_valid = True
                        self.rcvd_data += content
                        self.next_acknum += 1
                        if DEBUG_MODE: print("DEBUG: Data So far: ", self.rcvd_data)
                    else:
                        packet_valid = False
                    ack_segment = self.make_packet(self.MY_ADDR, self.source_addr, seqnum, acknum, packet_valid, self.last_pkt, "")
                    self.write_payload([ord(elem) for elem in ack_segment])
                    sleep(1)
                    self.set_mode(MODE.SLEEP)
                    self.set_dio_mapping([1,0,0,0,0,0])
                    self.set_mode(MODE.TX)
                    if DEBUG_MODE: self.debug_printpacket("sending ACK", ack_segment)
                    if DEBUG_MODE: print("DEBUG: last_pkt so far: ", self.last_pkt)
                    if(self.last_pkt==False):
                        sleep(.5)
                        self.set_mode(MODE.SLEEP)
                        self.set_dio_mapping([0] * 6)
                        self.reset_ptr_rx()
                        BOARD.led_off()
                        self.set_mode(MODE.RXCONT)
                    else:
                        sleep(.5)
                        self.set_mode(MODE.SLEEP)
                        self.flag=1
                else:
                    if DEBUG_MODE: self.debug_printpacket("DISCARDED received packet; not for me!!", packet)
            else:
                sleep(.5)
                self.set_mode(MODE.SLEEP)
                self.flag=1

    def on_tx_done(self):
        print("Entra en tx1")
        self.a=1
        global args


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
        print("Entra en Recv 1")
        self.flag=0
        self.flag_recv = False
        self.MY_ADDR = MY_ADDR[8:]
        self.SND_ADDR = SND_ADDR[8:]
        address_check = b""
        self.fpacket=True
        # Buffer storing the received data to be returned
        self.rcvd_data = b""
        self.next_acknum = 0
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        print("Entra aqui en recv 2")
        while (self.flag==0):
            print("Entra")
            sleep(.5)
        return self.rcvd_data,