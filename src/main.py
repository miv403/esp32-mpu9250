import sys
from device import Device

def main():

    esp32 = None
    mode = 0
    calibType = 0
    try:
        if len(sys.argv) > 1:
            if sys.argv[1] == "--calibrate":
                esp32 = Device(sys.argv[2])
        else:
            esp32 = Device()
    except IndexError:
        print("Unknown command")
        print("Usage:")
        print("\t--calibrate <option>")
        print("\t <option>: accel, gyro, magn")
        print("Ex:")
        print("\t --calibrate gyro")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("KeyboardInterrupt exiting.")
        exit()
