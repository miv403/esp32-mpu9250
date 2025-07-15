import serial
import struct

# Open serial port
ser = serial.Serial('/dev/ttyUSB0', 115200)  # Adjust to your port

# Struct format: 9 floats, little-endian
struct_format = '<9f'
struct_size = struct.calcsize(struct_format)

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
        print("Accel:", values[0:3], "Gyro:", values[3:6], "Mag:", values[6:9])
