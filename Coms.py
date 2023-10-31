import glob
import pickle
import serial
from serial import *
import time
import MessageTypesNfcSystem
import sys
import struct
#from middleware import log
# Helpful function to automatically detect serial port on which NFC Master is present.
ser = serial.Serial()

#Helper function to convert Uni_message to bytes
def convert_to_bytes(message):
    try:
        return struct.pack('BBBBffBBB', message.message_id, message.sensor_number,
                                    message.filament_data.material, message.filament_data.colour,
                                    message.filament_data.amount_left, message.filament_data.nominal_value,
                                    message.filament_data.space1, message.filament_data.space2,
                                    message.data)
    except:
        #log.info("[NFC] Data error while converting uni to bytes")
        return 0
#Helper function to convert bytes to Uni_message
def convert_to_uni_message(bytes):
    try:
        data = struct.unpack('BBBBffBBB', bytes)
        filament_data = MessageTypesNfcSystem.Filament_data(data[2], data[3], data[4], data[5], data[6], data[7])
        return MessageTypesNfcSystem.Uni_message(data[0], data[1], filament_data, data[8])
    except:
         #log.info("[NFC] Data error while converting bytes to uni")
         return 0
# Transcive function that send Uni_message and receives it back.
def transceive(config_message):
    # Send Message
    ser.write(convert_to_bytes(config_message))
    # Read response
    res = ser.read(15)
    if(len(res) == 15):
        return convert_to_uni_message(res)
    else:
        #log.info("[NFC] Received zero bytes")
        return 0
# Initialize serial port
def init_serial_port():
    ser.baudrate = 12000000
    ser.port = "/dev/ttyACM0"
    ser.timeout = 2
    try:
        ser.open()
    except serial.serialutil.SerialException:
        #log.info("[NFC] Error while opening serial port")
        return 0
#Function to initialize communication with nfc slave.
def configure_slave(num_of_sensors):
    #Initialize USB endpoint
    if init_serial_port() == 0:
        return 0
    #Transceive first message
    filament = MessageTypesNfcSystem.Filament_data(0,0,0,0,0,0)
    config_message = MessageTypesNfcSystem.Uni_message(67, 255, filament, 0)
    respons = transceive(config_message)
    if respons == 0:
        return 0
    if respons.data != MessageTypesNfcSystem.RADIO_CHECK_MESSAGE:
        #log.info("[NFC] slave did not respond with RADIO_CHECK_MESSAGE")
        return 0
    else:
        pass
        #log.info("[NFC] slave configuration done")
    config_message.data = num_of_sensors
    respons = transceive(config_message)
    return 1