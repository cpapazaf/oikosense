#include <Wire.h>
#include "DHT.h"
#include <LiquidCrystal_I2C.h>

#define DHTPIN A4
#define DHTTYPE DHT11

LiquidCrystal_I2C lcd(0x3F, 2, 1, 0, 4, 5, 6, 7, 3, POSITIVE);
DHT dht(DHTPIN, DHTTYPE);


void setup()
{
  Serial.begin(9600);  
  lcd.begin(16,2);
  dht.begin();
}


void loop() 
{
  delay(2000);
  
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  float f = dht.readTemperature(true);

  if (isnan(h) || isnan(t) || isnan(f)) {
    lcd.write("Failed to read from DHT sensor!");
    return;
  }

  float hif = dht.computeHeatIndex(f, h);
  float hic = dht.computeHeatIndex(t, h, false);
  String disp = String("H:" + String(h) + " T: " + String(t));
  char charBuf[50];
  disp.toCharArray(charBuf, 50);
  lcd.clear();
  lcd.write(charBuf);
  Serial.print("H:");
  Serial.print(h);
  Serial.print("\t");
  Serial.print("T:");
  Serial.println(t);
}


