# === CONFIGURATION ===
BOARD_FQBN = esp32:esp32:esp32
PORT = /dev/ttyUSB0
BAUD = 115200
# SKETCH = write-serial.ino
# SKETCH = simple-serial-comm
# SKETCH = send-struct
SKETCH = send-sensor-data
BUILD_DIR = build

# === AUTOMATIC SKETCH DIR NAME ===
SKETCH_NAME = $(basename $(SKETCH))
SKETCH_DIR = $(SKETCH_NAME)

# === DEFAULT TARGET ===
all: compile

# === COMPILE SKETCH ===
compile:
	arduino-cli compile --fqbn $(BOARD_FQBN) --output-dir $(BUILD_DIR) $(SKETCH_DIR)

# === UPLOAD TO BOARD ===
upload: compile
	arduino-cli upload -p $(PORT) --fqbn $(BOARD_FQBN) --input-dir $(BUILD_DIR) $(SKETCH_DIR)

# === SERIAL MONITOR ===
monitor:
	arduino-cli monitor -p $(PORT) -b $(BOARD_FQBN) --config $(BAUD)

# === CLEAN BUILD DIR ===
clean:
	rm -rf $(BUILD_DIR)


