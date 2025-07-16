import serial
import struct
import time

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
        pass
    def read_resp(self):
        resp = ser.read(1)
        # if resp:
        #     code = resp[0]
        #     print("[ESP32] Response:", RESP.get(code, f"Unknown ({code:#x})"))

        print("[ESP32] Response: ", resp)

    def sendCalibration(self, data):
        struct_format = '<6f'
        calibData_raw = struct.pack(struct_format,
                                    *(data['accBias'] + data['gyroBias']))
        ser.write(bytes([CMD_SEND_CALIB]))
        ser.write(calibData_raw)

    def calibrate(self):
        ser.write(bytes([CMD_CALIBRATE]))
        self.read_resp()
        time.sleep(0.3)
        # self.read_resp()

        # Read full struct

        struct_format = '<6f'
        struct_size = struct.calcsize(struct_format)
        data_bytes = ser.read(struct_size)

        if len(data_bytes) == struct_size:
            values = struct.unpack(struct_format, data_bytes)
            print("Bias data")
            print("Accel:", values[0:3],
                  "Gyro:", values[3:6]
                  #, "Mag:", values[6:9]
            )

    def getSensorData(self):
        # ser.write(bytes([CMD_GET_SENSOR]))
        # raw = ser.read(24) # 6 floats x 4 bytes
        # if len(raw) == 24:
        #     values = struct.unpack('<6f', raw)
        #     return {
        #         'acc' : values[0:3],
        #         'gyro' : values[3:6]
        #     }

        struct_format = '<6f' # acc*3 + gyro*3 = 6 floats
                              # esp32 and amd64 is little endian
                              # < means little endian
        struct_size = struct.calcsize(struct_format)
        while True:

            print("sensor data2")
            # while True: # wait for header
            #     if ser.read() == b'\xAA':
            #         if ser.read() == b'\x55':
            #             break
            # Read full struct
            raw = ser.read(struct_size)
            if len(raw) == struct_size:
                values = struct.unpack(struct_format, raw)

                print("acc: %.2f %.2f %.2f" % (values[0], values[1], values[2]))
                print("gyro: %.2f %.2f %.2f" % (values[3], values[4], values[5]))

                # print("acc: ", end="")
                # print("%.2f " % values[0:3][0], "%.2f " % values[0:3][1], "%.2f " % values[0:3][2])
                # print("gyro: ", end="")
                # print("%.2f " % values[3:6][0], "%.2f " % values[3:6][1], "%.2f " % values[3:6][2])
                # print(f"acc: {format(values[0:3][0], '.5f')},{format(values[0:3][1], '.5f')},{format(values[0:3][2], '.5f')}")
                # print(f"gyro: {format(values[3:6][0], '.5f')},{format(values[3:6][1], '.5f')},{format(values[3:6][2], '.5f')}")
            time.sleep(0.5)

        # return {
        #     'acc' : values[0:3],
        #     'gyro': values[3:6]
        # }

def main():

    esp32 = Device()

    use_existing_calib = False

    if use_existing_calib:
        esp32.sendCalibration(calibration)
    else:

        esp32.calibrate()
        time.sleep(0.5)

    print("sensor data")
    esp32.getSensorData()
    #while True:
    #    data = esp32.getSensorData()
    #    if data:
    #        print("Acc:", data['acc'], "Gyro:", data['gyro']
    #              #, "Mag:", data['mag']
    #        )
    #    time.sleep(0.5)

if __name__ == "__main__":
    try: 
        main()
    except KeyboardInterrupt:
        print("exit()")
        ser.flush()
        ser.close()
        exit()

