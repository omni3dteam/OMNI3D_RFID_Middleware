# OMNI3D_NFC_Middleware

NFC Middleware is a program responsible for communication with NFC Master. It acts as a translator between UART protocol and GCODE. This translation allows programs with high abstracion to directly interact with RFID system inside OMNI3D industrial printers.

## System Overview
![NFC system overview drawio](https://github.com/omni3dteam/OMNI3D_NFC_Middleware/assets/127947391/f74e748b-7d84-4bae-9940-1e5f785187d4)

## List of Mcodes and thier funcionality

### M5670: RFID Tag detecion
Check if sensor detetcs RFID Tag. Returns 0 if tag is detected and 1 if not
#### Parameters 
* **Sn** Sensor number. Corresponds to extruder number. First extruder is **S0** 

### M5673: Write Data
Write data to RFID Tag. Returns 0 if succesfull 1 otherwise. Write operation is only available if sensor is actively detecing RFID tag. 
#### Parameters
* **Sn** Sensor number. Corresponds to extruder number. First extruder is **S0** 
* **Fnnnn** Material type. See OMNI3D_Filament_Data_Base
* **Cnnnn** Colour. See OMNI3D_Filament_Data_Base
* **Annnn** Amount of material used on this spool (in mmm)
* **Lnnnn** Amount of material on new spool (in mm)
* **Nn** Indicator if material was ever used
* **Dnn** Day of first use
* **Onn** Month of first use
* **Rnn** Year of first use (only two last digits i.e 2023 is R23)
* **Ennnn** Serial number. Uniqe for every spool, given when first inserted into a database.

### M5678: Read Data
Read data stored on RFID Tag. Returns 1 if failed. Read operation is only available if sensor is actively detecing RFID tag. Returns data as parameters, in the same format as described in [M5673](#M5673:-Write-Data)








