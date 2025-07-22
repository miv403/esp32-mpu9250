#include <Wire.h>
#include <MPU9250.h>
#include <string.h>

#include "calibration.h"

#define OPT_CALIBRATE 0

MPU9250 mpu;

struct SensorData {

    // float yaw, pitch, roll; // [0:3]
    float gyroX, gyroY, gyroZ; // [0:3]
    float accX, accY, accZ; // [3:6]
    float magX, magY, magZ; // [6:9]

    float temperature;      // [9:10]
}sensorData;

struct CalibrationData {
  float accBiasX, accBiasY, accBiasZ;
  float gyroBiasX, gyroBiasY, gyroBiasZ;
  float magBiasX, magBiasY, magBiasZ;
  float magScaleX, magScaleY, magScaleZ;

}calibrationData;

struct MyData {
  float a;
  float b;
  int32_t c;
}receivedData;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  delay(2000); // Give time to open serial port

  sensorCheck();

  if(Serial.available()) {
    int option = Serial.read();
    if(option  == OPT_CALIBRATE){
      calibrate();
      sendCalibrationData();
    }
  }
}

void loop() {
  if (mpu.update()) {
    static uint32_t prev_ms = millis();
    if (millis() > prev_ms + 25) {
      //sendSensorData();
      printSensorData();
      prev_ms = millis();
    }
  }
  delay(100); // 10Hz update rate
}

void sensorCheck() {
  // MPU sensör denetimi
  if (!mpu.setup(0x68)) {  // change to your own address
      while (1) {
          Serial.println("MPU connection failed. Please check your connection with `connection_check` example.");
          delay(5000);
      }
  }
}

void calibrate() { // calibrate using MPU9250.h calibration functions
  // calibrate anytime you want to
  Serial.println("Accel Gyro calibration will start in 5sec.");
  Serial.println("Please leave the device still on the flat plane.");
  mpu.verbose(true);
  delay(5000);
  mpu.calibrateAccelGyro();

  mpu.verbose(false);

  //print_calibration();

}

void sendCalibrationData() {
  getBias();
  Serial.write(0xAA);
  Serial.write(0x55);
  // Send struct as raw bytes
  Serial.write((uint8_t*)&calibrationData, sizeof(calibrationData));
}

void recvCalibrationData() {
  while(!Serial);

  if (Serial.available() >= sizeof(MyData)) {
    Serial.readBytes((char *)&receivedData, sizeof(MyData));

    // You can now use receivedData.a, receivedData.b, receivedData.c
    Serial.println("Received Struct:");
    Serial.print("a: "); Serial.println(receivedData.a);
    Serial.print("b: "); Serial.println(receivedData.b);
    Serial.print("c: "); Serial.println(receivedData.c);
  }
}

void getBias() {

  // FIXME aşağıdaki dönüşümler ekrana basmak için kullanlıyor. 
  // kaydettikten sonra tekrar register'lara yüklerken gerekli olmayabilir.
  calibrationData.accBiasX = mpu.getAccBiasX() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY;
  calibrationData.accBiasY = mpu.getAccBiasY() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY;
  calibrationData.accBiasZ = mpu.getAccBiasZ() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY;;

  calibrationData.gyroBiasX = mpu.getGyroBiasX() / (float)MPU9250::CALIB_GYRO_SENSITIVITY;
  calibrationData.gyroBiasY = mpu.getGyroBiasY() / (float)MPU9250::CALIB_GYRO_SENSITIVITY;
  calibrationData.gyroBiasZ = mpu.getGyroBiasZ() / (float)MPU9250::CALIB_GYRO_SENSITIVITY;

  calibrationData.magBiasX = mpu.getMagBiasX();
  calibrationData.magBiasY = mpu.getMagBiasY();
  calibrationData.magBiasZ = mpu.getMagBiasZ();

  calibrationData.magScaleX = mpu.getMagScaleX();
  calibrationData.magScaleY = mpu.getMagScaleY();
  calibrationData.magScaleZ = mpu.getMagScaleZ();
}

void sendSensorData() {
  updateSensorData();
  // Optional sync header (e.g. 0xAA 0x55)
  Serial.write(0xAA);
  Serial.write(0x55);
  // Send struct as raw bytes
  Serial.write((uint8_t*)&sensorData, sizeof(sensorData));

}

void updateSensorData() {
  // updates all sensor data with getter()

    // sensorData.yaw = mpu.getYaw();
    // sensorData.pitch = mpu.getPitch();
    // sensorData.roll = mpu.getRoll();

    sensorData.gyroX = mpu.getGyroX();
    sensorData.gyroY = mpu.getGyroY();
    sensorData.gyroZ = mpu.getGyroZ();

    sensorData.accX  = mpu.getAccX();
    sensorData.accY  = mpu.getAccY();
    sensorData.accZ  = mpu.getAccZ();

}

void printSensorData() {
  updateSensorData();
  Serial.print("GyroX, GyroY, GyroZ: ");
  Serial.print(mpu.getGyroX(), 2);
  Serial.print(", ");
  Serial.print(mpu.getGyroY(), 2);
  Serial.print(", ");
  Serial.println(mpu.getGyroZ(), 2);

}


void print_calibration() {
    Serial.println("< calibration parameters >");
    Serial.println("accel bias [g]: ");
    Serial.print(mpu.getAccBiasX() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY);
    Serial.print(", ");
    Serial.print(mpu.getAccBiasY() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY);
    Serial.print(", ");
    Serial.print(mpu.getAccBiasZ() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY);
    Serial.println();
    Serial.println("gyro bias [deg/s]: ");
    Serial.print(mpu.getGyroBiasX() / (float)MPU9250::CALIB_GYRO_SENSITIVITY);
    Serial.print(", ");
    Serial.print(mpu.getGyroBiasY() / (float)MPU9250::CALIB_GYRO_SENSITIVITY);
    Serial.print(", ");
    Serial.print(mpu.getGyroBiasZ() / (float)MPU9250::CALIB_GYRO_SENSITIVITY);
    Serial.println();
}
