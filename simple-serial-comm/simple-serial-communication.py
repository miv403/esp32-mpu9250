import serial

ser = serial.Serial()
ser.baudrate = 115200
ser.port = '/dev/ttyUSB0'
ser.open()
values = bytearray([4, 9, 61, 144, 61, 161, 147, 3, 210, 89, 111, 78, 184, 151, 17, 129])

ser.write(values)
total = 0

while total < len(values):
    print(ord(ser.read(1)))
    total=total+1

ser.close()

