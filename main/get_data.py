import serial
import numpy as np
from io import StringIO
from time import sleep
import json
import datetime

ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)

CMD_CALIBRATE_ACCL = b'A' # A: İvmeölçer kalibrasyonu
CMD_CALIBRATE_GYRO = b'G' # G: Jiroskop kalibrasyonu
CMD_CALIBRATE_MAGN = b'M' # M: Manyetometre kalibrasyonu
CMD_SEND_RAW       = b'R' # R: Ham veri gönderimi
CMD_SEND_FILTERED  = b'F' # F: Filtrelenmiş veri gönderimi
CMD_SAVE_BIAS      = b'S' # S: Kayıtlı kalibrasyonu kaydet

CALIB_DONE         = "CALIBRATION::DONE"
CALIB_DATA         = "CALIBRATION::DATA"

ACCEL_GYRO_FILE    = "accel_gyro_bias.json"
MAG_BIAS_SCALE_FILE= "mag_bias_scale.json"

class Timestamp:
    def __init__(self):
        self.now_utc = datetime.datetime.now(datetime.timezone.utc)
    def ts(self):
        self.now_utc = datetime.datetime.now(datetime.timezone.utc)
        return self.now_utc.isoformat()

ts = Timestamp()


class Device:
    def __init__(self) -> None:
        sleep(0.5)
        pass

    def _readline(self):
        return ser.readline().decode('utf-8').strip()

    def _sendCommand(self, cmd):
        ser.write(cmd)
    def _writeLine(self, data):
        ser.write(data.encode("utf-8"))

    def recvLine(self):
        line = ser.readline().decode('utf-8').strip() + "\n"
        print(line)
    def startCalibration(self,type):
        self._sendCommand(type)

        bias = []

        output = self._readline()
        while output != CALIB_DONE:
            output = self._readline()
            if output == "" or output == None:
                continue
            print(output)
            if output == CALIB_DATA:
                output = self._readline()
                bias.append(output)
                print(output)
                output = self._readline()
                bias.append(output)
                print(output)

        self._saveBias(type, bias)

    def _saveBias(self, type, bias):
        csv_file = StringIO("\n".join(bias))
        data_csv = np.genfromtxt(csv_file, delimiter=',',
                             dtype=None, names=True,
                             encoding='utf-8')
        filename = "bias.json"
        biasDict = {}
        if type == CMD_CALIBRATE_ACCL or type == CMD_CALIBRATE_GYRO:
            filename = ACCEL_GYRO_FILE
            biasDict = {
                "date"      : ts.ts(),
                "accelBias" : [data_csv["accX"].tolist(),
                               data_csv["accY"].tolist(),
                               data_csv["accZ"].tolist()],
                "gyroBias"  : [data_csv["gyroX"].tolist(),
                               data_csv["gyroY"].tolist(),
                               data_csv["gyroZ"].tolist()]
            }
        elif type == CMD_CALIBRATE_MAGN:
            filename = MAG_BIAS_SCALE_FILE
            biasDict  = {
                "date"     : ts.ts(),
                "magBias"  : [data_csv["magBiasX"].tolist(),
                              data_csv["magBiasY"].tolist(),
                              data_csv["magBiasZ"].tolist()],
                "magScale" : [data_csv["magScaleX"].tolist(),
                              data_csv["magScaleY"].tolist(),
                              data_csv["magScaleZ"].tolist()]
            }
        print(biasDict)
        with open(filename, 'w') as f:
            json.dump(biasDict, f, indent=4)

    def sendBias(self):
        self._sendCommand(CMD_SAVE_BIAS)
        data = self._getBias()
        self._writeLine(data)
        sleep(0.05)
        print(self._readline())

        output = self._readline()
        print(output)
        while output != CALIB_DONE:
            output = self._readline()
            if output == "" or output == None:
                print("continue")
                continue
            print(output)
        self.readRaw()


    def _getBias(self):
        accelGyroJson = open(ACCEL_GYRO_FILE, "r")
        magJson = open(MAG_BIAS_SCALE_FILE, "r")
        accelGyroDict = json.load(accelGyroJson)
        magDict = json.load(magJson)
        
        accelBias = accelGyroDict['accelBias']
        gyroBias  = accelGyroDict['gyroBias']
        magBias   = magDict['magBias']
        magScale   = magDict['magScale']

        biasList = accelBias + gyroBias + magBias + magScale
        biasArray = np.array(biasList)
        biasData = np.array2string(biasArray, separator=',',
                                   max_line_width=100)[1:-1].replace(' ', '')
        
        return biasData
    def readRaw(self):
        self._sendCommand(CMD_SEND_RAW);
        sleep(0.05)
        output = self._readline()
        print(output)
        while True:
            output = self._readline()
            if output == "" or output == None:
                continue
            print(output)

def main():
    esp32 = Device()
    esp32.recvLine()

    cmd = 2

    if cmd == 0:
        esp32.startCalibration(CMD_CALIBRATE_ACCL)
        # esp32.startCalibration(CMD_CALIBRATE_MAGN)
    elif cmd == 1:
        esp32._sendCommand(CMD_SEND_RAW);
        line = ser.readline().decode('utf-8').strip() + "\n"
        print(line)
        lines = [line]
        # while True:
        for i in range(0,50):
            lines.append(ser.readline().decode('utf-8').strip() + "\n")
            # if line == "" or line == None:
            #     print("continue")
            #     continue
        print()
        line_file = StringIO(line.join(""))
        data = np.genfromtxt(line_file, delimiter=',',
                             dtype=None, names=True,
                             encoding='utf-8')
        print("accX,accY,accZ,gyroX,gyroY,gyroZ,magX,magY,magZ")
        print(data["accX"])

    elif cmd == 2:
        esp32.sendBias()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("KeyboardInterrupt exiting.")
        ser.flush()
        ser.close()
        exit()
