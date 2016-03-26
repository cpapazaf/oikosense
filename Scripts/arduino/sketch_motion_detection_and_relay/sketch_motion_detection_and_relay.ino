
#define RELAY1  4
#define MOTIONPIN 3

volatile int global_sensor_state = LOW;
volatile int global_relay_state = LOW;

String inputString = "";         // a string to hold incoming data

void setup() {
  // initialize serial:
  Serial.begin(9600);

  //set relay output
  pinMode(RELAY1, OUTPUT);

  //set motion input
  pinMode(MOTIONPIN, INPUT);

  // reserve 200 bytes for the inputString:
  inputString.reserve(200);

  // this is pin 3 with interrupt
  attachInterrupt(0, sensorChange, CHANGE);
}

void loop() {
  serialEvent();
}

void sensorChange()
{
  global_sensor_state = digitalRead(MOTIONPIN);
  Serial.print("Event: "); 
  Serial.println(global_sensor_state);

}

void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read(); 
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      if(inputString.equals("motion")){
        Serial.print("Motion: "); 
        Serial.println(global_sensor_state);
      }

      if(inputString.equals("relayoff")){
        digitalWrite(RELAY1,LOW); // Turns OFF Relays 1
        global_relay_state = LOW;
      }

      if(inputString.equals("relayon")){
        digitalWrite(RELAY1,HIGH); // Turns ON Relays 1
        global_relay_state=HIGH;
      }

      inputString = "";

    }
    else{
      // add it to the inputString:
      inputString += inChar;
    } 

  }
}


