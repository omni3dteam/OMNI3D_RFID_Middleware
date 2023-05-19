import serial
import struct
import construct
import traceback
import glob
import config
from Response import response
import Duet

# Helpful function to automatically detect serial port on which NFC Master is present.
def serial_ports():

    ports = glob.glob('/dev/tty[A-Za-z]*')
    for port in ports:
        print(type(port))
        if 'USB' in port:
            return port
        pass

# Open communication channel
ser = serial.Serial(serial_ports(), 921600, timeout = 1000)

# Class Filament is used to create abstracion layer around data saved on RFID Tag.
# It contains member functions that are helpful to move this data around program.

class Filament:

    sensor        = 0
    material      = 0
    colour        = 0
    amount_left   = 0
    nominal_value = 0
    is_new        = 0 
    day           = 0  
    month         = 0
    year          = 0
    serial_number = 0

    filament_data = construct.Struct(
                        "sensor"       / construct.Int8ub,
                        "material"     / construct.Int32un,
                        "colour"       / construct.Int32un,
                        "amount_left"  / construct.Int32un,
                        "nominal_value"/ construct.Int32un,
                        "is_new"       / construct.Int8ub,
                        "day"          / construct.Int8ub,
                        "month"        / construct.Int8ub,
                        "year"         / construct.Int8ub,
                        "serial_number"/ construct.Int32un
                    )
    
    # Member function used to convert raw bytearray to iterable python list.
    def return_as_list(self, bytesarray):
        received_filament = self.filament_data.parse(bytesarray)
        return [received_filament.sensor, received_filament.material, received_filament.colour, received_filament.amount_left, received_filament.nominal_value, received_filament.is_new, received_filament.day, received_filament.month, received_filament.year, received_filament.serial_number]
    
    # Member function used to return filament data as list.
    def return_list(self):
        return [self.sensor, self.material, self.colour, self.amount_left, self.nominal_value,self.is_new, self.day, self.month, self.year, self.serial_number]
    
    # Internal function used to assign new filament data to members.
    def assign(self, filament_data):
        self.sensor        = int(filament_data[0])
        self.material      = int(filament_data[1])
        self.colour        = int(filament_data[2])
        self.amount_left   = int(filament_data[3])
        self.nominal_value = int(filament_data[4])
        self.is_new        = int(filament_data[5])
        self.day           = int(filament_data[6])
        self.month         = int(filament_data[7])
        self.year          = int(filament_data[8])
        self.serial_number = int(filament_data[9]) 

    # Class constructor. Gives two ways of constructing object.
    # 1. From python list.
    # 2. From bytearray.
    # When calling constructor its important to specify which way should be used by setting bool "from_bytes" as True or False.
    # This mechanism allows for clean transitions like:
    # bytes -> wrapped filament data -> list 
    #                 or
    #  list -> wrapped filament data -> bytes
    # used throughout this code.
    def __init__(self, filament_data, bytesarray, from_bytes):
        if(from_bytes == False):
            self.assign(filament_data)
        else:
            filament_data = self.return_as_list(bytesarray)
            self.assign(filament_data)

    # Member function used to return filament data as bytearray. Useful to prepare data befor sending it through UART.      
    def return_as_bytes(self):

        buffer =  struct.pack('B' ,self.sensor       )
        buffer += struct.pack('I' ,self.material     )
        buffer += struct.pack('I' ,self.colour       )
        buffer += struct.pack('I' ,self.amount_left  )
        buffer += struct.pack('I' ,self.nominal_value)
        buffer += struct.pack('B' ,self.is_new       )
        buffer += struct.pack('B' ,self.day          )
        buffer += struct.pack('B' ,self.month        )
        buffer += struct.pack('B' ,self.year         )
        buffer += struct.pack('I' ,self.serial_number)
        return buffer
    
    # Member function to clear current fields.
    def clear_tag(self):
        self.material      = 0
        self.colour        = 0
        self.amount_left   = 0
        self.nominal_value = 0
        self.is_new        = 0
        self.day           = 0
        self.month         = 0
        self.year          = 0
        self.serial_number = 0

# End of Filament class

### High level functions ###
def nfc_master_send_filament_data(_filament_data):
    buffer =  _filament_data.return_as_bytes()
    nfc_master_send('D'.encode('utf-8'), buffer)

def nfc_master_check_sensor(sensor):
    nfc_master_send('E'.encode('utf-8'), struct.pack('B' ,sensor))

def nfc_master_clear_tag(sensor):
    nfc_master_send('B'.encode('utf-8'), struct.pack('B' ,sensor))  

### Low level functions ###
def nfc_master_receive():
    try:
        ser.timeout = 1
        x = ser.read(100)
        if(len(x) == 0):
           pass
        else:
            return x
    except Exception as e:
        print("Closing serial connection: ", e)
        traceback.print_exc()
        return -1
    finally:
        pass

def nfc_master_send(prefix, data):

    buffer = prefix
    buffer += data
    buffer += bytearray(100-len(buffer))
    ser.write(buffer)
    return 1

# Handler functions used when parsing messages from NFC Master.

def handle_msg_A():
    # Detecting this message means NFC master is alive
    config.is_master_online = True
    pass

def handle_msg_B():
    pass

def handle_msg_C(raw_message):
    parsed_message = raw_message[1:]
    new_filament = Filament(0, parsed_message, True)
    Duet.send_code_m5673(new_filament)
    pass

def handle_msg_E(raw_message):
    parsed_message = raw_message[1:]
    new_response = response(raw_message[0], raw_message[1])
    config.response_handler.register_pending_response(new_response)
    print(config.response_handler.responseData)
    pass