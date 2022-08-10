// Initialize DHT sensor.
#include "DHT.h"
#define DHTPIN 2     // Digital pin connected to the DHT sensor
#define DHTTYPE DHT11   // DHT 11
#define RELAYPIN 3

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  // Serial.println(F("DHTxx test!"));

  dht.begin();
  pinMode(RELAYPIN, OUTPUT);

}

void loop() {
  // Wait a few seconds between measurements.
  delay(5000);

  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  // Check if any reads failed and exit early (to try again).
  // if (isnan(h) || isnan(t)) {
  //  Serial.println(F("Failed to read from DHT sensor!"));
  //  return;
  //    }
  float hic = dht.computeHeatIndex(t, h, false);

  Serial.print(h);
  Serial.print(F(","));
  Serial.print(t);
  Serial.print(F(","));
  Serial.print(hic);
  Serial.print(F(","));

  if (t <= 25) {
    digitalWrite(RELAYPIN, LOW);
    Serial.println(F("1"));
  }
  else if (t >= 27) {
    digitalWrite(RELAYPIN, HIGH);
    Serial.println(F("0"));
  }
  else {
    bool RELAYSTATUS = digitalRead(RELAYPIN);
    Serial.println(!RELAYSTATUS);
  }
}
