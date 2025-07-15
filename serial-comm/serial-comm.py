import serial
import struct
import time

ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
# ser.open()

CMD_CALIBRATE = 0x01
CMD_SEND_CALIB = 0x02
CMD_GET_SENSOR = 0x03

RESP = {
    0x10: "Calibration complete",
    0x11: "Calibration data received",
    0x12: "Sensor mode started",
    0x13: "Sensor data sent",
    0xAA: "OK",
    0xFF: "Unknown command"
}

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
        packet = struct.pack('<6f', *(data['accBias'] + data['gyroBias']))
        ser.write(bytes([CMD_SEND_CALIB]))
        ser.write(packet)

    def calibrate(self):
        ser.write(bytes([CMD_CALIBRATE]))
        self.read_resp()
        self.read_resp()

        struct_format = '<6f'
        struct_size = struct.calcsize(struct_format)

        # while True:
        #     if ser.read() == b'\xAA':
        #         if ser.read() == b'\x55':
        #             break

        # Read full struct
        data_bytes = ser.read(struct_size)

        if len(data_bytes) == struct_size:
            values = struct.unpack(struct_format, data_bytes)
            print("Accel:", values[0:3],
                  "Gyro:", values[3:6]
                  #, "Mag:", values[6:9]
            )

    def getSensorData(self):
        ser.write(bytes([CMD_GET_SENSOR]))
        raw = ser.read(24) # 6 floats x 4 bytes
        if len(raw) == 24:
            values = struct.unpack('<6f', raw)
            return {
                'acc' : values[0:3],
                'gyro' : values[3:6]
            }
        return None

def main():

    esp32 = Device()

    use_existing_calib = False

    if use_existing_calib:
        esp32.sendCalibration(calibration)
    else:

        esp32.calibrate()
        time.sleep(2)

    while True:
        data = esp32.getSensorData()
        if data:
            print("Acc:", data['acc'], "Gyro:", data['gyro']
                  #, "Mag:", data['mag']
            )
        time.sleep(0.5)

if __name__ == "__main__":
    try: 
        main()
    except KeyboardInterrupt:
        exit()
