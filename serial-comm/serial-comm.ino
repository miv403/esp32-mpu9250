#include <Wire.h>
#include <MPU9250.h>

#define CMD_CALIBRATE   0x01
#define CMD_RECV_CALIB  0x02
#define CMD_GET_SENSOR  0x03

#define RESP_CALIB_DONE   0x10
#define RESP_CALIB_RCVD   0x11
#define RESP_SENSOR_MODE  0x12
#define RESP_SENSOR_SENT  0x13
#define RESP_OK           0xAA
#define RESP_ERR          0xFF

MPU9250 mpu;

// struct order: acc, gyro
struct CalibrationData {
  float accBias[3];
  float gyroBias[3];
} calib;

struct SensorData {
  float acc[3];
  float gyro[3];
}sensorData;

void setup() {
  Serial.begin(115200);
  Serial.flush();
  Wire.begin();
  delay(2000);

    if (!mpu.setup(0x68)) {  // change to your own address
        while (1) {
            Serial.write(RESP_ERR);
            delay(5000);
        }
    }
  uint8_t cmd = 0xAA;
  while(true) {
    if (Serial.available()) {
      uint8_t cmd = Serial.read();
      if (cmd == CMD_CALIBRATE) {
        break;
      }
    }
  }
  if (cmd == CMD_CALIBRATE) { // CALIBRATION
    Serial.write(RESP_OK);
    calibrate();
    Serial.write(RESP_CALIB_DONE);

    sendStruct(&calib, sizeof(CalibrationData));

    // Serial.write((uint8_t*)&calib, sizeof(CalibrationData));
    // break;
  }
  else if (cmd == CMD_RECV_CALIB) { // TODO didn't test it yet
    // gets saved calibration data from serial
    Serial.write(RESP_OK);

    while (Serial.available() < sizeof(CalibrationData));
    Serial.readBytes( (uint8_t*)&calib, sizeof(CalibrationData));
    Serial.write(RESP_CALIB_RCVD);
    // break;
  }
   // else if (cmd == CMD_GET_SENSOR) {
   //   break;
   // }
   // Serial.write(RESP_SENSOR_MODE);
   // setSensorData(); // gets & sets sensorData before send
   // sendStruct(&sensorData, sizeof(SensorData));
}


void loop() {
    // Serial.flush();
    // Serial.println("Before setSensorData");
    setSensorData(); // gets & sets sensorData before send
    //Serial.println("Before HEADER");
    
    sendStruct(&sensorData, sizeof(SensorData));
    // Serial.write((uint8_t*)&sensorData, sizeof(SensorData));
}

void sendStruct(const void* data, size_t size) {
  // Start marker to indicate the beginning of a struct
  Serial.write('S');
  Serial.write('T');
  // Send the struct data as a byte array
  Serial.write((uint8_t*)data, size);
  // End marker to indicate the end of a struct
  Serial.write('E');
  Serial.write('D');
}
bool receiveStruct(void* data, size_t size) {
  // Check for the start marker
  if (Serial.available() >= 2 && Serial.read() == 'S' && Serial.read() == 'T') {
    // Wait for the full struct data to be available
    if (Serial.available() >= (int)size + 2) {
      // Read the struct data
      Serial.readBytes(static_cast<uint8_t*>(data), size);
      // Check for the end marker
      if (Serial.read() == 'E' && Serial.read() == 'D') {
        return true;
      }
    }
  }
  return false;
}


void calibrate() {

    // calibrate anytime you want to
    // Serial.println("Accel Gyro calibration will start in 5sec.");
    // Serial.println("Please leave the device still on the flat plane.");
    mpu.verbose(true);
    delay(200);
    mpu.calibrateAccelGyro();

    // Serial.println("Mag calibration will start in 5sec.");
    // Serial.println("Please Wave device in a figure eight until done.");
    // delay(3000);
    // mpu.calibrateMag();

    getBias(); // saves the acquired bias to CalibrationData struct

    // print_calibration(); // old function to print biases to serial
    mpu.verbose(false);
}
void getBias() {
  calib.accBias[0]  = mpu.getAccBiasX();
  calib.accBias[1]  = mpu.getAccBiasY();
  calib.accBias[2]  = mpu.getAccBiasZ();

  calib.gyroBias[0] = mpu.getGyroBiasX();
  calib.gyroBias[1] = mpu.getGyroBiasY();
  calib.gyroBias[2] = mpu.getGyroBiasZ();
}
void setBias() { // sets mpu9250's offset registers
  mpu.setAccBias (calib.accBias[0],
                  calib.accBias[1],
                  calib.accBias[2]);

  mpu.setGyroBias(calib.gyroBias[0],
                  calib.gyroBias[1],
                  calib.gyroBias[2]);
}

void setSensorData() {
    // the current sensor data should be packaged before transmission

    sensorData.acc[0] = mpu.getAccX();
    sensorData.acc[1] = mpu.getAccY();
    sensorData.acc[2] = mpu.getAccZ();

    sensorData.gyro[0] = mpu.getGyroX();
    sensorData.gyro[1] = mpu.getGyroY();
    sensorData.gyro[2] = mpu.getGyroZ();
}
/*
  if(Serial.available) {
    sensorData.gyro[0] = mpu.getGyroX();
    sensorData.gyro[1] = mpu.getGyroY();
    sensorData.gyro[2] = mpu.getGyroZ();
    sensorData.acc[0] = mpu.getAccX();
    sensorData.acc[1] = mpu.getAccY();
    sensorData.acc[2] = mpu.getAccZ();

    Serial.write(0xAA);
    Serial.write(0x55);

    Serial.write((uint8_t*)&sensorData, sizeof(SensorData));
  }

    if (cmd == CMD_GET_SENSOR) {
      float data[9] = {
        mpu.getAccX(), mpu.getAccY(), mpu.getAccZ(),
        mpu.getGyroX(), mpu.getGyroY(), mpu.getGyroZ(),
        mpu.getMagX(), mpu.getMagY(), mpu.getMagZ()
      };
      Serial.write((byte*)data, sizeof(data));
    }
 */
