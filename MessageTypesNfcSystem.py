from dataclasses import dataclass
from ctypes import *
import sys

@dataclass
class Filament_data:
    material: c_uint8
    colour: c_uint8
    amount_left: float
    nominal_value: float
    space1: c_uint8
    space2: c_uint8

SIZE_OF_FILAMENT_DATA = sys.getsizeof(Filament_data)

@dataclass
class Uni_message:
    message_id: c_uint8
    sensor_number: c_uint8
    filament_data: Filament_data
    data: c_uint8

SIZE_OF_UNI_MESSAGE =  sys.getsizeof(Uni_message)
RADIO_CHECK_MESSAGE = 255