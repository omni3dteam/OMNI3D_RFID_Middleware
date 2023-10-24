# Libraries
import logging
import time
import threading
from ctypes import *
from multiprocessing import Queue
from systemd.journal import JournalHandler
import traceback
import sys
# Python dsf API
from dsf.connections import CommandConnection
from dsf.connections import InterceptConnection, InterceptionMode
from dsf.commands.code import CodeType
#from dsf.object_model import MessageType
#Global list to store current filaments
filaments_database = list((0,0,0,0))
#Global variables and flags
spin_delay = 2000
last_nfc_check = 0
write_pending_for_sensor = -1
#Modules
from Coms import *
from nfc_logging import *
# log object used to log to journal
log = logging.getLogger('nfc')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)
# Function used to send filament data to higher instances
def intercept_data_request():
    filters = ["M1002"]
    intercept_connection = InterceptConnection(InterceptionMode.PRE, filters=filters, debug=True)
    intercept_connection.connect()

    command_connection = CommandConnection(debug=False)
    command_connection.connect()

    try:
        while True:
            # Wait for a code to arrive.
            cde = intercept_connection.receive_code()
            # Configuration request
            if cde.type == CodeType.MCode and cde.majorNumber == 1002:
                intercept_connection.resolve_code()
                sensor = (cde.parameter("S").as_int() - 1)
                try:
                    command_connection.perform_simple_code("M1002 T{} C{} A{} N{}".format(
                                 filaments_database[sensor].material,
                                 filaments_database[sensor].colour,
                                 filaments_database[sensor].amount_left,
                                 filaments_database[sensor].nominal_value))
                finally:
                    command_connection.close()
            # We did not handle it so we ignore it and it will be continued to be processed
            else:
                intercept_connection.ignore_code()
    except Exception as e:
        print("Closing connection: ", e)
        traceback.print_exc()
        intercept_connection.close()
# Function used to intercept config message
def intercept_config_message():
    filters = ["M1000"]
    intercept_connection = InterceptConnection(InterceptionMode.PRE, filters=filters, debug=True)
    intercept_connection.connect()
    try:
        while True:
            # Wait for a code to arrive.
            cde = intercept_connection.receive_code()
            # Configuration request
            if cde.type == CodeType.MCode and cde.majorNumber == 1000:
                intercept_connection.resolve_code()
                return cde
            # We did not handle it so we ignore it and it will be continued to be processed
            else:
                intercept_connection.ignore_code()
    except Exception as e:
        print("Closing connection: ", e)
        traceback.print_exc()
        intercept_connection.close()
# Function used to intercept data write request. Used in different thread
def intercept_data_write_request():
    filters = ["M1001"]
    intercept_connection = InterceptConnection(InterceptionMode.PRE, filters=filters, debug=True)
    intercept_connection.connect()
    try:
        while True:
            # Wait for a code to arrive.
            cde = intercept_connection.receive_code()
            # Data request
            if cde.type == CodeType.MCode and cde.majorNumber == 1001:
                intercept_connection.resolve_code()
                sensor = cde.parameter("S").as_int()
                filament_data = MessageTypes.Filament_data(cde.parameter("T").as_int(),
                                                           cde.parameter("C").as_int(),
                                                           cde.parameter("A").as_float(),
                                                           cde.parameter("N").as_float(),
                                                           0,0)
                global filaments_database
                global write_pending_for_sensor
                filaments_database[sensor - 1] = filament_data
                write_pending_for_sensor = (sensor - 1)
            # We did not handle it so we ignore it and it will be continued to be processed
            else:
                intercept_connection.ignore_code()
    except Exception as e:
        print("Closing connection: ", e)
        traceback.print_exc()
        intercept_connection.close()

data_request       = threading.Thread(target=intercept_data_request)
data_write_request = threading.Thread(target=intercept_data_write_request)

# Program entry
if __name__ == "__main__":

    log.info("NFC Middleware started")
    # Wait for configuration gcode
    number_of_sensors = (intercept_config_message().parameter("S").as_int())
    current_sensor = 0
    data_write_request.start()
    data_request.start()
    # Configure slave device
    if configure_slave(number_of_sensors) != 1:
        print("[NFC] Error while initializing slave")
        log.info("[NFC] Error while initializing slave")
        sys.exit()
    # Main loop
    while(True):
        # Receive new filament data #
        new_filament_data = MessageTypes.Uni_message(65, current_sensor, MessageTypes.Filament_data(0,0,0,0,0,0), 0)
        new_filament_data = transceive(new_filament_data)
        # print("Received Filament: ")
        # print_filament_data(new_filament_data.filament_data, current_sensor)
        # Write new data if requested by user (or another instance)  #
        if write_pending_for_sensor != -1:
            write_request_message = MessageTypes.Uni_message(66, write_pending_for_sensor, filaments_database[write_pending_for_sensor], 0)
            respons = transceive(write_request_message)
            write_pending_for_sensor = -1
        # Write new data in normal mode
        else:
            # Calculate amount left
            #
            #
            #
            # Send new data to tag
            write_request_message = MessageTypes.Uni_message(66, current_sensor, new_filament_data.filament_data, 0)
            transceive(write_request_message)
            filaments_database[current_sensor] = new_filament_data.filament_data
        # Print database entry
        # print("Database Filament: ")
        # print_filament_data(filaments_database[current_sensor], current_sensor)
        # Advance sensor
        current_sensor += 1
        if current_sensor > (number_of_sensors-1):
            current_sensor = 0
        time.sleep(0.5)

