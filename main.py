# Supporting files
import NFC
import Duet
import config
# Libraries
import logging
import threading
import time
from ctypes import *
from multiprocessing import Queue
from systemd.journal import JournalHandler
from typing import List
import traceback
# Python dsf API
from dsf.connections import InterceptConnection, InterceptionMode
from dsf.commands.code import CodeType
from dsf.object_model import MessageType

###### Global objects ######

log = logging.getLogger('nfc')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

reception_queue = Queue()
queue_transmit = Queue()

config.init()

###### Below are the main threads of NFC Middleware program ######

# This thread is checking if NFC master is online.
# will assert error and stop whole programif unable to detect hearbeat
def check_heartbeat():
    while  ( config.Continue == True  and config.latched_error == False):
        if config.is_master_online == True:
            config.is_master_online = False
            Continue = True
            time.sleep(10)   
        else:
            config.Continue = True
            log.error("NFC Master heartbeat not found") 
            config.error_msg = "NFC Master heartbeat not found"
            break
    config.Continue = True

# This thread is reading data from NFC Master. All messages have const size (100 bytes) in order to simplyfy communication.
# When read is succesfull, read_message thread will push 100 bytes array into FIFO queue named "reception_queue".
# If reading function detects error in serial communication, it will throw latched error and exit whole program.
def read_message():
    while ( config.Continue == True ):
        x = NFC.nfc_master_receive()
        if(x != (0 or -1)):
            reception_queue.put(x)
            if(queue_transmit.qsize() != 0):
                #send
                NFC.nfc_master_send(queue_transmit.get())
            else:
                pass
        elif x == -1:
            config.latched_error = True
            config.error_msg = "NFC Master communication failed"
            break 

# This thread is parsing received messages. If reception_queue is not empty, it will pop first message and act upon it. 
# Communication between NFC master and NFC Middleware is done using messages of 100 bytes, in which first byte is used to recognize type of message
# Message 'A' - used to send heartbeat of NFC Master
# Message 'B' - used as Request from NFC master to send filament data.
# Message 'C' - used to receive filament data from NFC master.
# Message 'D' - used to send filament data to NFC Master.
# Message 'E' - used to check if sensor is detecting RFID tag.
def parse_message():
    while ( config.Continue == True ):
        if(reception_queue.qsize() != 0):
            raw_message = reception_queue.get()
            if raw_message != None:
                if  raw_message[0] == 65:    #A - NFC Master heartbeat
                    NFC.handle_msg_A()
                elif raw_message[0] == 66:   #B - Filament Data request
                    log.info("NFC Master requested filament usage data")
                    NFC.handle_msg_B()
                elif raw_message[0] == 67:   #C - Get filament data from NFC Master
                    log.info("Received filament data")
                    NFC.handle_msg_C(raw_message)
                elif raw_message[0] == 69:
                   log.info("Received check response") 
                   NFC.handle_msg_E(raw_message)
            else:
                pass
        else:
            time.sleep(1)
            pass

# This thread is used to react on mcodes for NFC system.
def intercept_mcodes():

    filters = ["M5670","M5673","M5678", "M5679","M5680", "M5681", "M5682"]
    intercept_connection = InterceptConnection(InterceptionMode.PRE, filters=filters, debug=True)
    intercept_connection.connect()
    try:
        while True:
            # Wait for a code to arrive
            cde = intercept_connection.receive_code()
            #Receive filament data
            if cde.type == CodeType.MCode and cde.majorNumber == 5678:
                intercept_connection.resolve_code()
                Duet.mcode_5678(cde)
            elif cde.type == CodeType.MCode and cde.majorNumber == 5673:
                intercept_connection.resolve_code()
            #clear RFID tag
            elif cde.type == CodeType.MCode and cde.majorNumber == 5679:
                intercept_connection.resolve_code()
                Duet.mcode_5679(cde)
            #RFID Tag detecion
            elif cde.type == CodeType.MCode and cde.majorNumber == 5670:
                if(Duet.mcode_5670(cde) == 4):
                    status = "Not detecting RFID Tag"
                else:
                    status = "detecting RFID Tag"
                intercept_connection.resolve_code(MessageType.Success, "Sensor {} is {}".format(cde.parameter("S").as_int(), status))
        #not assigned
            elif cde.type == CodeType.MCode and cde.majorNumber == 5681:
                pass
            #stop this node
            elif cde.type == CodeType.MCode and cde.majorNumber == 5682:
                intercept_connection.resolve_code()
                raise ValueError('Forced stop')   
            # We did not handle it so we ignore it and it will be continued to be processed
            else:
                intercept_connection.ignore_code()
    except Exception as e:
        print("Closing connection: ", e)
        traceback.print_exc()
        intercept_connection.close()


heartbeat_thread = threading.Thread(target=check_heartbeat)
queue_thread = threading.Thread(target=read_message)
parsing_thread = threading.Thread(target=parse_message)
mcodes_intercept = threading.Thread(target=intercept_mcodes)

# Main loop. used to start, keep alive, and kill threads when error occures.
if __name__ == "__main__":

    log.info("NFC Middleware started")

    heartbeat_thread.start()
    queue_thread.start()
    parsing_thread.start()
    mcodes_intercept.start()

    while( config.Continue == True ):
        time.sleep(10)
    else:
        heartbeat_thread.join()
        queue_thread.join()
        parsing_thread.join()
        Duet.stop()
        mcodes_intercept.join()
        raise ValueError(config.error_msg)   
