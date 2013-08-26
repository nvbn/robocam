#include <Wire.h>
#include "I2Cdev.h"
#include "MPU6050.h"
MPU6050 accelgyro;
 
int16_t ax, ay, az;
int16_t gx, gy, gz;
 
void setup(){
    Wire.begin();
    accelgyro.initialize();
    Serial.begin(9600);
    delay(100);
}
 
void loop(){
    accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
    Serial.print(ax); Serial.print(" ");
    Serial.print(ay); Serial.print(" ");
    Serial.print(az); Serial.print(" ");
    Serial.print(gx); Serial.print(" ");
    Serial.print(gy); Serial.print(" ");
    Serial.println(gz);
    delay(500);
}
