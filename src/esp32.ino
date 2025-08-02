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

#define CALIB_DONE "CALIBRATION::DONE"
#define CALIB_DATA "CALIBRATION::DATA"
#define SENSOR_DATA "SENSOR::DATA"

struct Bias{
  float acc[3];
  float gyro[3];
  float magBias[3];
  float magScale[3];
}bias;

bool isCalibrated = false;

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
  delay(500);
  Serial.println("[ESP32] MPU9250 connected.");

  char cmd = '0';
  while(true){
    if(isCalibrated) {
      Serial.println(CALIB_DONE);
      cmd = '0';
    }
    if(Serial.available() > 0) {
      cmd = Serial.read();

      if(cmd == CMD_CALIBRATE_ACCL
      || cmd == CMD_CALIBRATE_GYRO
      || cmd == CMD_CALIBRATE_MAGN) { // TODO test calibration
        startCalibration(cmd);
      }
      else if(cmd == CMD_SEND_RAW) {
        Serial.println("accX,accY,accZ,gyroX,gyroY,gyroZ,magX,magY,magZ");
        sendRawDataLoop();
      }
      else if(cmd == CMD_SAVE_BIAS) {
        saveBias();
      }
      else if(cmd == CMD_SEND_FILTERED) {
        Serial.println(SENSOR_DATA);
        Serial.println("roll,pitch,yaw");
        break;
      }
    }
  }
} // end setup()

void loop() {
  if(mpu.update()) {
    static uint32_t prev_ms = millis();
    if(millis() > prev_ms + 25) {
      sendRPY();
      prev_ms = millis();
    }
  }
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

void sendRawDataLoop() {
  if(mpu.update()) {
    static uint32_t prev_ms = millis();
    if(millis() > prev_ms + 25) {
      sendRawData();
      prev_ms = millis();
    }
  }
}

void startCalibration(char type) {

  if(type == CMD_CALIBRATE_ACCL || type == CMD_CALIBRATE_GYRO){
    // calibrate anytime you want to
    Serial.println("Accel Gyro calibration will start in 1sec.");
    Serial.println("Please leave the device still on the flat plane.");
    delay(1000);
    mpu.calibrateAccelGyro();
    // print_calibration();
    sendBias(type);

  }
  else if(type == CMD_CALIBRATE_MAGN){
    mpu.verbose(true);
    Serial.println("Mag calibration will start in 5sec.");
    Serial.println("Please Wave device in a figure eight until done.");
    delay(5000);
    mpu.calibrateMag();
    // print_calibration();
    mpu.verbose(false);
    sendBias(type);
  }
  isCalibrated = true;
}

void setBias() {
  mpu.setAccBias (bias.acc[0],
                  bias.acc[1],
                  bias.acc[2]);

  mpu.setGyroBias(bias.gyro[0],
                  bias.gyro[1],
                  bias.gyro[2]);

  mpu.setMagBias (bias.magBias[0],
                  bias.magBias[1],
                  bias.magBias[2]);
  mpu.setMagBias (bias.magScale[0],
                  bias.magScale[1],
                  bias.magScale[2]);

  isCalibrated = true;
}

void getBias() {
  bias.acc[0]      = mpu.getAccBiasX();
  bias.acc[1]      = mpu.getAccBiasY();
  bias.acc[2]      = mpu.getAccBiasZ();

  bias.gyro[0]     = mpu.getGyroBiasX();
  bias.gyro[1]     = mpu.getGyroBiasY();
  bias.gyro[2]     = mpu.getGyroBiasZ();

  bias.magBias[0]  = mpu.getMagBiasX();
  bias.magBias[1]  = mpu.getMagBiasY();
  bias.magBias[2]  = mpu.getMagBiasZ();

  bias.magScale[0] = mpu.getMagScaleX();
  bias.magScale[1] = mpu.getMagScaleY();
  bias.magScale[2] = mpu.getMagScaleZ();
}

void sendBias(char type) {

  getBias();
  Serial.println(CALIB_DATA);

  if(type == CMD_CALIBRATE_ACCL || type == CMD_CALIBRATE_GYRO) {
    Serial.println("accX,accY,accZ,gyroX,gyroY,gyroZ");
    Serial.print(   bias.acc[0]   ); Serial.print(",");
    Serial.print(   bias.acc[1]   ); Serial.print(",");
    Serial.print(   bias.acc[2]   ); Serial.print(",");

    Serial.print(   bias.gyro[0]  ); Serial.print(",");
    Serial.print(   bias.gyro[1]  ); Serial.print(",");
    Serial.println( bias.gyro[2]  );

  }
  else if(type == CMD_CALIBRATE_MAGN) {
    Serial.println("magBiasX,magBiasY,magBiasZ,magScaleX,magScaleY,magScaleZ");
    Serial.print( bias.magBias[0] ); Serial.print(",");
    Serial.print( bias.magBias[1] ); Serial.print(",");
    Serial.print( bias.magBias[2] ); Serial.print(",");

    Serial.print( bias.magScale[0]); Serial.print(",");
    Serial.print( bias.magScale[1]); Serial.print(",");
    Serial.println( bias.magScale[2]); 
  }
}

void saveBias() { // DONE test saving bias
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');  // Read until newline

    char *title = "accX,accY,accZ,gyroX,gyroY,gyroZ,magBiasX,magBiasY,magBiasZ,magScaleX,magScaleY,magScaleZ\n";
    // String csv_str = title + input;
    CSV_Parser cp(title, /*format*/ "ffffffffffff"); // 12 float
    cp << input;

    float *floats = (float*)cp["my_floats"];
    bias.acc[0]       = ((float*)cp["accX"])[0];
    bias.acc[1]       = ((float*)cp["accY"])[1];
    bias.acc[2]       = ((float*)cp["accZ"])[2];

    bias.gyro[0]      = ((float*)cp["gyroX"])[0];
    bias.gyro[1]      = ((float*)cp["gyroY"])[1];
    bias.gyro[2]      = ((float*)cp["gyroZ"])[2];

    bias.magBias[0]   = ((float*)cp["magBiasX"])[0];
    bias.magBias[1]   = ((float*)cp["magBiasY"])[1];
    bias.magBias[2]   = ((float*)cp["magBiasZ"])[2];

    bias.magScale[0]  = ((float*)cp["magScaleX"])[0];
    bias.magScale[1]  = ((float*)cp["magScaleY"])[1];
    bias.magScale[2]  = ((float*)cp["magScaleZ"])[2];

    setBias();

    Serial.print("You entered: ");
    Serial.print(mpu.getAccBiasX());
    Serial.print(",");
    Serial.println(mpu.getMagScaleZ());

  }
}

void sendRPY() {
  Serial.print(mpu.getRoll() - 31.31); Serial.print(",");
  Serial.print(mpu.getPitch()); Serial.print(",");
  Serial.println(mpu.getYaw());
}
