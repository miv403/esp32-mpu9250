#include <Wire.h>

// Define your sensor data struct
struct SensorData {
  float ax, ay, az;
  float gx, gy, gz;
  float mx, my, mz;
};

// Create and fill the struct with dummy or real sensor data
SensorData data;

void setup() {
  Serial.begin(115200);
  delay(1000); // Give time to open serial port
}

void loop() {
  // Replace with actual sensor readings
  data.ax = 1.1;
  data.ay = 2.2;
  data.az = 3.3;
  data.gx = 4.4;
  data.gy = 5.5;
  data.gz = 6.6;
  data.mx = 7.7;
  data.my = 8.8;
  data.mz = 9.9;

  // Optional sync header (e.g. 0xAA 0x55)
  Serial.write(0xAA);
  Serial.write(0x55);

  // Send struct as raw bytes
  Serial.write((uint8_t*)&data, sizeof(data));

  delay(100); // 10Hz update rate
}
