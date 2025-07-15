import serial
import struct
from sys import platform

port = 'dev/ttyUSB0' # if on linux
if platform == "win32": # if on windows
    port = "COM3"

# Open serial port
ser = serial.Serial(port, 115200)  # Adjust to your port

# Struct format: 9 floats, little-endian
struct_format = '<10f'
struct_size = struct.calcsize(struct_format)
try: 
    while True:
        # Wait for header (0xAA 0x55)
        while True:
            if ser.read() == b'\xAA':
                if ser.read() == b'\x55':
                    break
    
        # Read full struct
        data_bytes = ser.read(struct_size)
    
        if len(data_bytes) == struct_size:
            values = struct.unpack(struct_format, data_bytes)
            # print("Accel:", values[0:3], "Gyro:", values[3:6], "Mag:", values[6:9])
            gyroRaw  = values[0:3]
            accelRaw = values[3:6]
            magRaw   = values[6:9]
            tempRaw  = values[9:10]
            print("Gyro: ", gyroRaw )
            print("Accel: ",  accelRaw)
            print("Mag: ",  magRaw  )
            print("Temp: ",  tempRaw )
except KeyboardInterrupt:
    print("exit")
    exit()
