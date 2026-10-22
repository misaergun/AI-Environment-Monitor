
#include <DHT.h>

// DHT11 data pin
#define DHTPIN 2
#define DHTTYPE DHT11

// LDR analog pin
#define LDR_PIN A0

DHT dht(DHTPIN, DHTTYPE);

void setup()
{
  Serial.begin(9600);
  dht.begin();

  Serial.println("AI Environment Monitor");
  Serial.println("Sensor initialization complete.");
  Serial.println("--------------------------------");
}

void loop()
{
  // Read temperature and humidity
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // Read light level
  int lightLevel = analogRead(LDR_PIN);

  // Check DHT11 readings
  if (isnan(humidity) || isnan(temperature))
  {
    Serial.println("ERROR: Failed to read DHT11 sensor.");
  }
  else
  {
    Serial.print("Temperature: ");
    Serial.print(temperature, 1);
    Serial.print(" C | Humidity: ");
    Serial.print(humidity, 1);
    Serial.print(" % | Light: ");
    Serial.println(lightLevel);
  }

  delay(2000);
}
