#include <Wire.h>
#include <MPU9250.h>

MPU9250 mpu;

struct SensorData {

    float yaw, pitch, roll; // [0:3]
    float accX, accY, accZ; // [3:6]
    float magX, magY, magZ; // [6:9]

    float temperature;      // [9:10]

}sensorData;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  delay(2000); // Give time to open serial port

  // MPU sensör denetimi

  if (!mpu.setup(0x68)) {  // change to your own address
      while (1) {
          Serial.println("MPU connection failed. Please check your connection with `connection_check` example.");
          delay(5000);
      }
  }
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

    sensorData.yaw = mpu.getYaw();
    sensorData.pitch = mpu.getPitch();
    sensorData.roll = mpu.getRoll();

    sensorData.accX = mpu.getAccX();
    sensorData.accY = mpu.getAccY();
    sensorData.accZ = mpu.getAccZ();

    sensorData.magX = mpu.getMagX();
    sensorData.magY = mpu.getMagY();
    sensorData.magZ = mpu.getMagZ();

    sensorData.temperature = mpu.getTemperature();
}
