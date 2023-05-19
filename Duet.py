from dsf.connections import CommandConnection
from dsf.connections import SubscribeConnection, SubscriptionMode
import config
import NFC

### NFC Middleware outcomming GCODES ###
def send_code_m5676(mcode):
    pass

def send_code_m5675(mcode):
    pass

def send_code_m5674(mcode):
    pass

# This functions wraps filament data into Gcode and send it into a printer system.
def send_code_m5673(filament_data):
    command_connection = CommandConnection(debug=False)
    command_connection.connect()
    try:
        command_connection.perform_simple_code("M5673 S{} F{} C{} A{} L{} N{}  D{} O{} R{} E{} ".format(
                                 filament_data.sensor,
                                 filament_data.material,
                                 filament_data.colour,
                                 filament_data.amount_left,
                                 filament_data.nominal_value,
                                 filament_data.is_new,
                                 filament_data.day,
                                 filament_data.month,
                                 filament_data.year,
                                 filament_data.serial_number,))
    finally:
        command_connection.close()



### NFC Middleware incomming GCODES

# This GCode handler carries out checking of RFID Tag presence. It takes Gcode message as argument. 
# Parameter 'S' is refering to sensor on which this procedur will be conducted.
# Functions is returning response from NFC Master. 
def mcode_5670(cde):
    NFC.nfc_master_check_sensor(cde.parameter("S").as_int())
    while (config.response_handler.responsePending != True):
        #TODO timeout this loop
        pass
    print(config.response_handler.responseData)
    sensor_response = config.response_handler.responseData
    config.response_handler.ack()
    return sensor_response

# This Gcode is used to write new data to RFID Tag. Takes Gcode message as argument. 
# Returns nothing, but maybe could return status of whole operation. #TODO
def mcode_5678(cde):
    new_filament = NFC.Filament([cde.parameter("S").as_int(), 
                                 cde.parameter("F").as_int(),
                                 cde.parameter("C").as_int(),
                                 cde.parameter("A").as_int(),
                                 cde.parameter("L").as_int(),
                                 cde.parameter("N").as_int(),
                                 cde.parameter("D").as_int(),
                                 cde.parameter("O").as_int(),
                                 cde.parameter("R").as_int(),
                                 (cde.parameter("E").as_int()+1),] # '+1' IS FOR TESTING ONLY !!!
                                 ,0 ,False)
    NFC.nfc_master_send_filament_data(new_filament)
    print(new_filament.serial_number)

# This function is used to handle clearing procedur of RFID tag. 
# Parameter 'S' is refering to sensor on which this procedur will be conducted.
def mcode_5679(cde):
    NFC.nfc_master_clear_tag(cde.parameter("S").as_int())
    pass

def mcode_5680(cde):
    pass

def mcode_5681(cde):
    pass


# Internal function used to stop gcode interceptor when program fails.
def stop():

    command_connection = CommandConnection(debug=True)
    command_connection.connect()
    try:
        # Perform a simple command and wait for its output
        res = command_connection.perform_simple_code("M5682")
    finally:
        command_connection.close()