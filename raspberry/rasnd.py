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
#BOARD.setup()

#parser = LoRaArgumentParser("A simple LoRa beacon")
#parser.add_argument('--single', '-S', dest='single', default=False, action="store_true", help="Single transmission")
#parser.add_argument('--wait', '-w', dest='wait', default=1, action="store", type=float, help="Waiting time between transmissions (default is 0s)")

DATA_PACKET = False
ANY_ADDR = b'FFFFFFFF'
# BEGIN: Utility functions
#

class LoRaSend(LoRa):

    tx_counter = 0
      # Must determine which is the maximum pkt size in LoRa with Spread Factor 7... 
    

    def __init__(self):
        #super(LoRaSend, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([1,0,0,0,0,0])
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
        if DEBUG_MODE: print("SND_ADDR", self.snd_add)
        #print("\nRxDone")
        #print(self.get_irq_flags())
        ackn = self.read_payload(nocheck=True)
        ack=''.join(chr(i) for i in ackn)
        if DEBUG_MODE: print("ack", ack)
        ack_source_addr, ack_dest_addr, ack_seqnum, ack_acknum, ack_is_ack, ack_final, ack_check, ack_content = self.unpack(ack)
        if (ack_seqnum == 0 and self.bandera ==0):
            self.rcv2 = ack_source_addr
            self.bandera = 1
        if DEBUG_MODE: self.debug_printpacket("received ack", ack)
        if ack_final:
            self.set_mode(MODE.SLEEP)
        # If valid, here we go!
        if (ackn_is_ackn) and (ack_acknum == self.acknum)and(self.rcv2==ack_source_addr):
            self.set_dio_mapping([1,0,0,0,0,0])
            self.reset_ptr_rx()
            self.set_mode(MODE.TX)
            self.flagsend=1
        else:
            if DEBUG_MODE: print("ERROR: packet received not valid")
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        BOARD.led_off()
        self.set_mode(MODE.RXCONT)

    def on_tx_done(self):
        print("Entra en tx1")
        self.a=1
        global args
        """
        #self.set_mode(MODE.STDBY)
        self.clear_irq_flags(TxDone=1)
        sys.stdout.flush()
        BOARD.led_off()
        #sleep(args.wait)
        pl = b"Winter is coming"
        print("Entra en tx2")
        self.write_payload([ord(elem) for elem in pl])
        BOARD.led_on()
        print("Entra en tx3")
        self.set_mode(MODE.TX)
        
        #self.set_mode(MODE.TX)
        if(self.flagsend==1):
            sample_rtt = recv_time - send_time
            if estimated_rtt == -1:
                estimated_rtt = sample_rtt
            else:
                estimated_rtt = estimated_rtt * 0.875 + sample_rtt * 0.125
                dev_rtt = 0.75 * dev_rtt + 0.25 * abs(sample_rtt - estimated_rtt)
            if DEBUG_MODE: debug_printpacket("Payload left", self.payload)
            text=self.payload[0:PAYLOAD_SIZE]   # Copying PAYLOAD_SIZE bytes header from the input string
            if DEBUG_MODE: print("Payload to send", text)
            self.payload = self.payload[PAYLOAD_SIZE:]    # Shifting the input string
            if DEBUG_MODE: print("Payload left", self.payload)
            # AM: Checking if it's the last ACK
            if last_pkt:
                self.dentro= True
            # Checking if this is the last packet
            if (len(text) == PAYLOAD_SIZE) and (len(payload) > 0): 
                self.last_pkt = False
            else: 
                self.last_pkt = True
                self.bandera = 0
            # Increment sequence and ack numbers
            self.seqnum += 1
            self.acknum += 1
            RCV_ADDR = self.rcv2
            packet = make_packet(SND_ADDR, RCV_ADDR, self.seqnum, self.acknum, DATA_PACKET, last_pkt, text)
            self.write_payload([ord(elem) for elem in packet])
            sys.stdout.write("\rtx #%d" % self.tx_counter)           
            self.sent += 1 
            if DEBUG_MODE: debug_printpacket("sending new packet", packet, True)
        if(self.flagsend==2):
            packet = make_packet(self.snd_add, self.rec_add, self.seqnum, self.acknum, DATA_PACKET, self.last_pkt, self.text)
            self.write_payload([ord(elem) for elem in packet])
            self.flagn +=1
            if DEBUG_MODE: debug_printpacket("re-sending packet: ", packet)
            if DEBUG_MODE: print("From rasnd Flag Number: ", self.flagn)
            self.sent += 1
            self.retrans += 1
            if(self.flagn==3):   #AM: Para no dejar el socket colgado se pone un reenvio de 3 paquetes
                self.dentro= True
                self.set_mode(MODE.SLEEP)"""


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

    def send(self,payload,SND_ADDR,RCV_ADDR):
        print("Entra en Send 1")
        global args
        signal.signal(signal.SIGALRM, self.handler)
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
        BOARD.led_on()
        if DEBUG_MODE: print("RCV_ADDR", RCV_ADDR)
        self.snd_add = SND_ADDR
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
        print("Entra en Send 2")
        self.write_payload([ord(elem) for elem in packet])
        if DEBUG_MODE: self.debug_printpacket("sending 1st", packet)
        self.set_mode(MODE.TX)
        self.sent += 1
        self.dentro=False
        # waiting for a ack
        sleep(2)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        #signal.alarm(10)
        print("Entra en send 3")
        if not self.dentro:
            while True:
                sleep(2)
                print("Entra al while")
                #self.set_mode(MODE.SLEEP)
                #self.set_dio_mapping([0] * 6)
                #self.reset_ptr_rx()
                #self.set_mode(MODE.RXCONT)
                
        print("RETURNING tsend")
        return(self.sent,self.retrans,self.sent)