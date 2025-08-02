import serial
import struct
import time
import pickle

CALIB_FILE = "./calib.dat"

HEADER_BYTES = b'AT' # Define header bytes as bytes literal
HEADER_BYTES_2 = b'BT' # Define header bytes as bytes literal
TERM_BYTES = b'ED' # Define terminal bytes as bytes literal

ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)

CMD_CALIBRATE  = 0x01
CMD_SEND_CALIB = 0x02
CMD_GET_SENSOR = 0x03

RESP = {
    0x10: "Calibration complete",
    0x11: "Calibration data received",
    0x12: "Sensor mode started",
    0x13: "Sensor data sent",
    0xAA: "OK",
    0xFF: "ERROR"
}

# struct order: acc, gyro

# placeholder calibration data
calibration = {
    'accBias' : [0.1, -0.1, 0.0],
    'gyroBias' : [0.05, 0.01, -0.02]
}

class Device:
    def __init__(self):
        # time.sleep(1.5)
        self.bias = ()
        self.readBiasFromFile()
        pass

    def saveBias(self):
        calibDataFile = open(CALIB_FILE, "wb")
        pickle.dump(self.bias, calibDataFile)
        calibDataFile.close()

    def readBiasFromFile(self):
        calibDataFile = open(CALIB_FILE, "rb")
        self.bias = pickle.load(calibDataFile)
        print("Bias data read: ", self.bias)

    def read_resp(self):
        resp = ser.read(2)
        # if resp:
        #     code = resp[0]
        #     print("[ESP32] Response:", RESP.get(code, f"Unknown ({code:#x})"))

        print("[ESP32] Response: ", resp)

    def calibrate(self):
        # sends command to calibration and recieves bias data
        ser.write(bytes([CMD_CALIBRATE]))
        time.sleep(0.4)
        self.read_resp()
        time.sleep(0.4)
        self.read_resp()

        self.bias = self.receiveStruct('<6f')

        if self.bias == None:
            print("bias data not receieved.")
            return
        print(self.bias)
        print("Bias Data: ")
        print("Accel Bias: ", self.bias[0:3])
        print("Gyro Bias: ",  self.bias[3:6])

        self.saveBias()

        # Read full struct
        # struct_format = '<6f'
        # struct_size = struct.calcsize(struct_format)
        # data_bytes = ser.read(struct_size)

        # if len(data_bytes) == struct_size:
        #     values = struct.unpack(struct_format, data_bytes)
        #     print("Bias data")
        #     print("Accel:", values[0:3],
        #           "Gyro:", values[3:6]
        #           #, "Mag:", values[6:9]
        #     )

    def getSensorData(self):
        # self.read_resp() # reading serial for RESP_SENSOR_MODE
        sensorData = self.receiveStruct('<6f')

        if not sensorData:
            print("sensor data not received")
            return
        print("Sensor Data: ") # debug purposes FIXME delete this line
        print("Accel Data: %.5f %.5f %.5f" % (sensorData[0], sensorData[1], sensorData[2]))
        print("Gyro Data:  %.5f %.5f %.5f" % (sensorData[3], sensorData[4], sensorData[5])) 

        # print("Accel Data: ", sensorData[0:3])
        # print("Gyro Data: ", sensorData[3:6])

    def sendCalibration(self):
        struct_format = '<6f'
        ser.write(bytes([CMD_SEND_CALIB]))
        self.read_resp()
        self.sendStruct(self.bias, struct_format)
        self.read_resp()
        # calibData_raw = struct.pack(struct_format, *(data['accBias'] + data['gyroBias']))
        # ser.write(calibData_raw)

    def receiveStruct(self,struct_format):
        struct_size = struct.calcsize(struct_format)
        try:
            c = 0
            while True:
                print("waiting for header ", c)
                c += 1
                header = ser.read(2)
                if header == HEADER_BYTES or header == HEADER_BYTES_2:
                    print("header: ", header)
                    data = ser.read(struct_size)
                    unpacked_data = struct.unpack(struct_format, data)
                    return unpacked_data

        except serial.SerialException as e:
            print(f"Error reading from serial port: {e}")
        except struct.error as e:
            print(f"Error unpacking data: {e}")
        return None

    def sendStruct(self, data, struct_format):
        # Args:
        #     data: A tuple containing the data to be sent.
        try:
            packed_data = struct.pack(struct_format, *data)
            ser.write(b'ST' + packed_data + b'ED')
            print(f"Sent: {data}")
        except serial.SerialException as e:
            print(f"Error writing to serial port: {e}")
def main():

    esp32 = Device()

    # esp32.calibrate()
    esp32.sendCalibration()

    while True:
        esp32.getSensorData()

    # while True:
    #     print("MPU9250 Controller: ")
    #     print("1. Calibrate")
    #     print("2. Send Calibration")
    #     print("3. Get Sensor Data")
    #     cmd = input("?: ")
    #     if cmd == "1":
    #         esp32.calibrate()
    #     elif cmd == "2":
    #         esp32.sendCalibration()
    #     elif cmd == "3":
    #         while True:
    #             esp32.getSensorData()

if __name__ == "__main__":
    try: 
        main()
    except KeyboardInterrupt:
        print("exit()")
        ser.flush()
        ser.close()
        exit()

"""
    def getSensorData(self):
        pass
        struct_format = '<6f'
        struct_size = struct.calcsize(struct_format)
        while True:
                # Read until we find the header
                while True:
                    print("headers")
                    byte1 = ser.read(1)
                    if not byte1: # Timeout or no data
                        break # Exit inner loop, try again
                    if byte1 == HEADER_BYTES[0:1]: # Check for 0xAA
                        byte2 = ser.read(1)
                        if not byte2:
                            break # Exit inner loop, try again
                        if byte2 == HEADER_BYTES[1:2]: # Check for 0x55
                            print("Header found!")
                            break # Header found, break from inner while loop

                # If header was found, proceed to read the struct data
                if byte1 == HEADER_BYTES[0:1] and byte2 == HEADER_BYTES[1:2]: # Ensure header was actually found
                    if ser.in_waiting >= struct_size:
                        raw_data = ser.read(struct_size)
                        if len(raw_data) == struct_size:
                            try:
                                values = struct.unpack(struct_format, raw_data)
                                print("acc: %.2f %.2f %.2f" % (values[0], values[1], values[2]))
                                print("gyro: %.2f %.2f %.2f" % (values[3], values[4], values[5])) # Corrected print for gyroscope
                            except struct.error as e:
                                print(f"Error unpacking data: {e}. Raw: {raw_data.hex()}")
                        else:
                            print(f"Incomplete data received. Expected {struct_size}, got {len(raw_data)}")
                    else:
                        # Not enough data after header, might need to re-sync
                        print("Not enough data immediately after header. Resyncing...")
                else:
                    # If we broke out of the inner loop without finding a header
                    pass # Just continue the outer loop to keep searching for headers

                time.sleep(0.01) # Small delay to prevent busy-waiting and allow buffer to fill
"""
