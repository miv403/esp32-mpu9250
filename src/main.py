import sys
from device import *

def main():
    esp32 = Device()
    esp32.recvLine()

    mode = 0
    calibType = 0
    if mode == "--calibrate":
        cmd = 0
        if   calibType == "accel":
            calibType = CMD_CALIBRATE_ACCL
        elif calibType == "gyro":
            calibType = CMD_CALIBRATE_GYRO
        elif calibType == "magn":
            calibType = CMD_CALIBRATE_MAGN
    else:
        cmd = 1

    if cmd == 0:
        esp32.startCalibration(calibType)
    # elif cmd == 1:
    else:
        esp32.sendBias()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("KeyboardInterrupt exiting.")
        ser.flush()
        ser.close()
        exit()
