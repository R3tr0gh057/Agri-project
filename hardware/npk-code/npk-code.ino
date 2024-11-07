#include <ModbusMaster.h>
#include <WiFi.h>
#include "DHT.h"
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

#define MAX485_DE      32
#define MAX485_RE_NEG  33

#define RXD2 16
#define TXD2 17

#define DHTPIN 4      // Pin where DHT11 is connected
#define DHTTYPE DHT11 

const char* ssid = "Todo";
const char* password = "Todotodo";
const char* tempServer = "http://192.168.193.55:5000/update-data";
const char* npkServer = "http://192.168.193.55:5000/update-npk";

int nitrogenValue = 0;
int phosphorusValue = 0;
int potassiumValue = 0;
float temperature = 0;
float humidity = 0;
float soil_moisture = 0;

// Modbus RTU requests for reading NPK values
const byte nitro[] = {0x01, 0x03, 0x00, 0x1E, 0x00, 0x01, 0xE4, 0x0C};
const byte phos[] = {0x01, 0x03, 0x00, 0x1F, 0x00, 0x01, 0xB5, 0xCC};
const byte pota[] = {0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xC0};

// Buffer to store response from sensor
byte values[7];
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);

  WiFi.begin(ssid, password); 
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {  
      delay(1000);
      Serial.print(".");
  }
  Serial.println("Connected to WiFi");

  dht.begin(); 

  pinMode(MAX485_RE_NEG, OUTPUT);
  pinMode(MAX485_DE, OUTPUT);
  digitalWrite(MAX485_RE_NEG, LOW);
  digitalWrite(MAX485_DE, LOW);
}

void loop() {

  // Read Nitrogen (N)
  nitrogenValue = readSensor(nitro);
  Serial.print("Nitrogen: ");
  Serial.print(nitrogenValue);
  Serial.println(" mg/kg");

  delay(250);

  // Read Phosphorus (P)
  phosphorusValue = readSensor(phos);
  Serial.print("Phosphorus: ");
  Serial.print(phosphorusValue);
  Serial.println(" mg/kg");

  delay(250);

  // Read Potassium (K)
  potassiumValue = readSensor(pota);
  Serial.print("Potassium: ");
  Serial.print(potassiumValue);
  Serial.println(" mg/kg");
  Serial.println("\n\n\n");

  delay(250);

  // Send the temperature and humidity data
  dth_read();

  delay(250);

  String jsonData = "{\"temperature\":" + String(temperature) +
                  ",\"humidity\":" + String(humidity) +
                  ",\"soil_moisture\":" + String(soil_moisture) +
                  ",\"potassium\":" + String(potassiumValue) +
                  ",\"phosphorus\":" + String(phosphorusValue) +
                  ",\"nitrogen\":" + String(nitrogenValue) + "}";

  sendData(tempServer, jsonData);

  delay(2000);  // Delay before next cycle


}

int readSensor(const byte *command) {
  // Set RS485 to transmit mode
  digitalWrite(MAX485_RE_NEG, HIGH);
  digitalWrite(MAX485_DE, HIGH);

  // Send command to sensor
  Serial2.write(command, 8);
  Serial2.flush();

  // Set RS485 to receive mode
  digitalWrite(MAX485_RE_NEG, LOW);
  digitalWrite(MAX485_DE, LOW);

  // Wait for response
  delay(20);

  int bytesRead = 0;
  while (Serial2.available() && bytesRead < 7) {
    values[bytesRead++] = Serial2.read();
  }

  // Verify if we received a valid response
  if (bytesRead == 7) {
    // The nutrient value is typically in the 4th byte for Modbus responses
    return (int)values[4];
  } else {
    Serial.println("Failed to read sensor data");
    return -1;  // Indicate error
  }
}

void dth_read() {
  temperature = dht.readTemperature(); 
  humidity = dht.readHumidity();
  soil_moisture = 55;

  if (isnan(temperature) || isnan(humidity)) { 
      Serial.println("Failed to read from DHT sensor!");
      return;
  }

  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.print("Soil Moisture: ");
  Serial.print(soil_moisture);
  Serial.print(" °C, Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");
}

void sendData(const String &address, const String &jsonData) {
  if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(address);
      http.addHeader("Content-Type", "application/json");

      int httpResponseCode = http.POST(jsonData);
      Serial.print("Status of POST request: ");
      Serial.println(httpResponseCode);

      http.end();
  } else {
      Serial.println("Error in WiFi connection");
  }
}