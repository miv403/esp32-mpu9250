import time
import serial
import struct
from sys import platform


PORT = 'dev/ttyUSB0' # if on linux
if platform == "win32": # if on windows
    PORT = "COM3"

def recvSensorData():
    # Open serial port
    ser = serial.Serial(PORT, 115200)  # Adjust to your port
    
    # Struct format: 10 floats, little-endian
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
        ser.flush()
        ser.close()
        exit()

def sendCalibrateSignal():
    pass
def sendCalibrationData():

    sendCalibrateSignal()
    # Match the Arduino baud rate and serial port
    ser = serial.Serial('/dev/ttyUSB0', 115200)  # Or COMx on Windows
    time.sleep(2)  # Wait for ESP32 to reset
    
    # Define the same structure: float, float, int32
    data = struct.pack('<ffi', 3.14, 2.71, 42)
    
    # Send over serial
    ser.write(data)
    ser.flush()
    ser.close()

def main():
    if input("calibrate[y/n]: ") == "y":
        pass

    recvSensorData()

if __name__ == "__main__":
    main()
