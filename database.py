import csv
from MessageTypesNfcSystem import Filament_data

def write_filament(filament_data, sensor):
    csv_file = []
    with open('filaments.csv', 'r') as csvfile:
        reader = csv.reader(csvfile ,quoting=csv.QUOTE_NONNUMERIC)
        csv_file = list(reader)
    with open('filaments.csv', 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        row_number = 0
        for row in csv_file:
            if row_number == sensor:
                csv_file[row_number] = [filament_data.material,
                                        filament_data.colour,
                                        filament_data.amount_left,
                                        filament_data.nominal_value,
                                        -1,
                                        -1]
            row_number += 1
        for row in csv_file:
            filewriter.writerow(row)