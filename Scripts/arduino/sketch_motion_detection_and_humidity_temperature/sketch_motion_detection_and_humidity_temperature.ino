#include "DHT.h"

#define MOTIONPIN 3
#define DHTPIN A4

#define DHTTYPE DHT11

volatile int global_sensor_state = LOW;

// Initialize DHT sensor.
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  // initialize serial:
  Serial.begin(9600);

  //set motion input
  pinMode(MOTIONPIN, INPUT);

  // this is MOTIONPIN with interrupt
  attachInterrupt(digitalPinToInterrupt(MOTIONPIN), sensorChange, CHANGE);

  dht.begin();
}

void loop() {
  // Wait a few seconds between measurements.
  delay(10 * 1000);

  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();
  // Read temperature as Fahrenheit (isFahrenheit = true)
  float f = dht.readTemperature(true);

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t) || isnan(f)) {
    Serial.println("#error:Failed to read from DHT sensor!#");
    return;
  }

  // Compute heat index in Fahrenheit (the default)
  float hif = dht.computeHeatIndex(f, h);
  // Compute heat index in Celsius (isFahreheit = false)
  float hic = dht.computeHeatIndex(t, h, false);

  String humidity_string = String(h);
  String temperature_string = String(t);
  
  Serial.println("H:" + humidity_string);
  Serial.println("T:" + temperature_string);
}

void sensorChange()
{
  global_sensor_state = digitalRead(MOTIONPIN);
  String global_sensor_state_string = String(global_sensor_state);
  Serial.println("M:" + global_sensor_state_string);
}



