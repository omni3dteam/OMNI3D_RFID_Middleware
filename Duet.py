from dsf.connections import CommandConnection
from dsf.connections import SubscribeConnection, SubscriptionMode

import logging
from systemd.journal import JournalHandler

import NFC

EXTRUDER_0 = 0
EXTRUDER_1 = 1
BOTH_EXTRUDERS = 2
NUMBER_OF_EXTRUDERS = 2


def return_from_object_model(thing):
    subscribe_connection = SubscribeConnection(SubscriptionMode.PATCH)
    subscribe_connection.connect()
    try:
        # Get the complete model once
        object_model = subscribe_connection.get_object_model()

        #print(object_model.move.extruders[0].position)

        # Get multiple incremental updates, due to SubscriptionMode.PATCH, only a
        # subset of the object model will be updated
    finally:
        subscribe_connection.close()
        #print((object_model.job.file.file_name))

def send_code_m5676(mcode):
    pass

def send_code_m5675(mcode):
    pass

def send_code_m5674(mcode):
    pass

#Send detected filament as gcode
def send_code_m5673(filament_data):
    command_connection = CommandConnection(debug=True)
    command_connection.connect()

    res = command_connection.perform_simple_code("M5673 S{} F{} C{} A{} L{} N{}  D{} O{} R{} E{} ".format(
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
#Read filament as gcode
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
                                 cde.parameter("E").as_int(),]
                                 ,0 ,False)
def mcode_5679(cde):
    pass

def mcode_5680(cde):
    pass

def mcode_5681(cde):
    pass


def stop():

    command_connection = CommandConnection(debug=True)
    command_connection.connect()
    try:
        # Perform a simple command and wait for its output
        res = command_connection.perform_simple_code("M5682")
    finally:
        command_connection.close()