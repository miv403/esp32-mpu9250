#include <Wire.h>
#include <MPU9250.h>
#include <CSV_Parser.h>

MPU9250 mpu;

#define CMD_CALIBRATE_ACCL 'A' // A: İvmeölçer kalibrasyonu
#define CMD_CALIBRATE_GYRO 'G' // G: Jiroskop kalibrasyonu
#define CMD_CALIBRATE_MAGN 'M' // M: Manyetometre kalibrasyonu
#define CMD_SEND_RAW       'R' // R: Ham veri gönderimi
#define CMD_SEND_FILTERED  'F' // F: Filtrelenmiş veri gönderimi
#define CMD_SAVE_BIAS      'S' // S: Kayıtlı kalibrasyonu kaydet

struct Bias{
  float acc [3];
  float gyro[3];
  float mag [3];
}bias;

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  Wire.begin();

  // delay to wait for sensor
  delay(1000);

  if (!mpu.setup(0x68)) {
    Serial.println("[ESP32] MPU9250 connection error!");
    while (1) {
      Serial.println("[ESP32] Check sensor connection.");
      delay(5000);
      if (mpu.setup(0x68)) break;
    }
  }
  Serial.println("[ESP32] MPU9250 connected.");

  while(true){
    if(Serial.available() > 0) {
      char cmd = Serial.read();
      
      if(cmd == CMD_CALIBRATE_ACCL
      || cmd == CMD_CALIBRATE_GYRO
      || cmd == CMD_CALIBRATE_MAGN) {
        startCalibration(cmd);
      }
      else if(cmd == CMD_SEND_RAW) {
        break;
      }
      else if(cmd == CMD_SAVE_BIAS) {
        saveBias();
      }
    }
  }

  Serial.println("accX,accY,accZ,gyroX,gyroY,gyroZ,magX,magY,magZ");
} // end setup()

void loop() {
  if(mpu.update()) {
    static uint32_t prev_ms = millis();
    if(millis() > prev_ms + 25) {
      sendRawData();
      prev_ms = millis();
    }
  }
}

void startCalibration(char type) {

      // if(type == CMD_CALIBRATE_ACCL){

      // }
      // else if (type == CMD_CALIBRATE_GYRO){

      // }
      // else if (type == CMD_CALIBRATE_MAGN){

      // }
}

void sendRawData() {
  // Serial.println("accX,accY,accZ,gyroX,gyroY,gyroZ,magX,magY,magZ");
  Serial.print(mpu.getAccX()) ; Serial.print(",");
  Serial.print(mpu.getAccY()) ; Serial.print(",");
  Serial.print(mpu.getAccZ()) ; Serial.print(",");
  Serial.print(mpu.getGyroX()); Serial.print(",");
  Serial.print(mpu.getGyroY()); Serial.print(",");
  Serial.print(mpu.getGyroZ()); Serial.print(",");
  Serial.print(mpu.getMagX()) ; Serial.print(",");
  Serial.print(mpu.getMagY()) ; Serial.print(",");
  Serial.println(mpu.getMagZ());
}

void saveBias() {
  char *title = "accX,accY,accZ,gyroX,gyroY,gyroZ,magX,magY,magZ\n";
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');  // Read until newline
    String csv_str = title + input;
    CSV_Parser cp(csv_str, /*format*/ "fffffffff"); // 9 float

    float *floats = (float*)cp["my_floats"];
    bias.acc[0]  = (float*)cp["accX"][0];
    bias.acc[1]  = (float*)cp["accY"][1];
    bias.acc[2]  = (float*)cp["accZ"][2];

    bias.gyro[0] = (float*)cp["gyroX"][0];
    bias.gyro[1] = (float*)cp["gyroY"][1];
    bias.gyro[2] = (float*)cp["gyroZ"][2];

    bias.mag[0]  = (float*)cp["magX"][0];
    bias.mag[1]  = (float*)cp["magY"][1];
    bias.mag[2]  = (float*)cp["magZ"][2];

    setBias();
    //Serial.print("You entered: ");
    // Serial.println(csv_str);

  }
}

void setBias() {
  mpu.setAccBias (bias.acc[0],
                  bias.acc[1],
                  bias.acc[2]);

  mpu.setGyroBias(bias.gyro[0],
                  bias.gyro[1],
                  bias.gyro[2]);

  mpu.setMagBias (bias.mag[0],
                  bias.mag[1],
                  bias.mag[2]);
}
