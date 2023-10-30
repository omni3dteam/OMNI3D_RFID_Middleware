import MessageTypesNfcSystem

def print_filament_data(filament_data, sensor):
    print('''Filament from sensor: %d
            Material: %d
            Colour: %d
            Amount left: %f
            Nominal Value: %f \n
            '''%(
            sensor,
            filament_data.material,
            filament_data.colour,
            filament_data.amount_left,
            filament_data.nominal_value))
