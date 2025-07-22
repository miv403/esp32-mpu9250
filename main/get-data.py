import serial
import numpy as np
from io import StringIO
from time import sleep

ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)

CMD_CALIBRATE_ACCL = b'A' # A: İvmeölçer kalibrasyonu
CMD_CALIBRATE_GYRO = b'G' # G: Jiroskop kalibrasyonu
CMD_CALIBRATE_MAGN = b'M' # M: Manyetometre kalibrasyonu
CMD_SEND_RAW       = b'R' # R: Ham veri gönderimi
CMD_SEND_FILTERED  = b'F' # F: Filtrelenmiş veri gönderimi
CMD_SAVE_BIAS      = b'S' # S: Kayıtlı kalibrasyonu kaydet

class Device:
    def __init__(self) -> None:
        sleep(0.5)
        pass

    def sendCommand(self, cmd):
        ser.write(cmd)
    def recvLine(self):
        line = ser.readline().decode('utf-8').strip() + "\n"
        print(line)

def main():
    esp32 = Device()
    esp32.recvLine()

    cmd = 2

    if cmd == 0:
        pass
    elif cmd == 1:
        esp32.sendCommand(CMD_SEND_RAW);
        line = ser.readline().decode('utf-8').strip() + "\n"
        print(line)
        # while True:
        for i in range(0,1000):
            line += ser.readline().decode('utf-8').strip() + "\n"
            # if line == "" or line == None:
            #     print("continue")
            #     continue
        print()
        line_file = StringIO(line)
        data = np.genfromtxt(line_file, delimiter=',',
                             dtype=None, names=True,
                             encoding='utf-8')
        print("accX,accY,accZ,gyroX,gyroY,gyroZ,magX,magY,magZ")
        print(data["accX"])
        pass
    elif cmd == 2:
        esp32.sendCommand(CMD_SAVE_BIAS)
        ser.write(bytes("bias,1.3,2.4,2.5", "utf-8"))
        sleep(0.05)
        line1 = ser.readline().decode("utf-8").strip()
        line2 = ser.readline().decode("utf-8").strip()
        print(line1)
        print(line2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("KeyboardInterrupt exiting.")
        ser.flush()
        ser.close()
        exit()
