#include <Wire.h>
#include <MPU9250.h>

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

}calibrationData;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  delay(2000); // Give time to open serial port

  // if calibration needed
  //    then calibrate()

  sensorCheck();
}

void loop() {

  if (mpu.update()) {
    static uint32_t prev_ms = millis();
    if (millis() > prev_ms + 25) {
      sendSensorData();
      prev_ms = millis();
    }
  }
  delay(100); // 10Hz update rate
}


void setCalibrationData() {
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

void sendCalibrationData() {

  Serial.write(0xAA);
  Serial.write(0x55);
  // Send struct as raw bytes
  Serial.write((uint8_t*)&calibrationData, sizeof(calibrationData));
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
    Serial.println("mag bias [mG]: ");
    Serial.print(mpu.getMagBiasX());
    Serial.print(", ");
    Serial.print(mpu.getMagBiasY());
    Serial.print(", ");
    Serial.print(mpu.getMagBiasZ());
    Serial.println();
    Serial.println("mag scale []: ");
    Serial.print(mpu.getMagScaleX());
    Serial.print(", ");
    Serial.print(mpu.getMagScaleY());
    Serial.print(", ");
    Serial.print(mpu.getMagScaleZ());
    Serial.println();
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

    sensorData.magX  = mpu.getMagX();
    sensorData.magY  = mpu.getMagY();
    sensorData.magZ  = mpu.getMagZ();

    sensorData.temperature = mpu.getTemperature();
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

