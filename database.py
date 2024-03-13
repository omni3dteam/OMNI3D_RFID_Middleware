import sqlite3

from MessageTypesNfcSystem import Filament_data
connection = sqlite3.connect("filaments.db")

def check_if_databse_exists():
    cursor = connection.cursor()
    cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='filament' ''')
    if cursor.fetchone()[0] == 1:
        return 1
    else:
        init_database()

def init_database():
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE filament(sensor INTEGER, colour INTEGER, material INTEGER, amount_left FLOAT, nominal_value INTEGER)''')

    cursor.execute('''INSERT INTO filament VALUES (0,-1,-1,0.0,1)''')
    cursor.execute('''INSERT INTO filament VALUES (1,-1,-1,0.0,1)''')
    cursor.execute('''INSERT INTO filament VALUES (2,-1,-1,0.0,1)''')
    cursor.execute('''INSERT INTO filament VALUES (3,-1,-1,0.0,1)''')

    connection.commit()

def read_database():
    cursor = connection.cursor()
    return cursor.execute("SELECT * from filament").fetchall()

def write_filament(filament_data, sensor):
    cursor = connection.cursor()
    cursor.execute('''UPDATE filament SET colour = ?, material = ?, amount_left = ?, nominal_value = ? WHERE sensor = ?''', (filament_data.material, filament_data.colour, filament_data.amount_left, filament_data.nominal_value, sensor))
    connection.commit()

