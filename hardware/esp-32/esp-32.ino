#include "DHT.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>

// #define DHTPIN 4      // Pin where DHT11 is connected
// #define DHTTYPE DHT11 

const char* ssid = "Yamete";
const char* password = "Todotodo";
const char* serverName = "http://192.168.0.110:80/update-data";

WebServer server(3000);
// DHT dht(DHTPIN, DHTTYPE);

int LED = 13;

void setup() {
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);
  
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.print(".");
  }
  Serial.println("Connected to WiFi");
  Serial.println("IP: ");
  Serial.print(WiFi.localIP());
  // dht.begin(); 

  server.on("/toggle-led", HTTP_GET, []() {
      digitalWrite(LED, !digitalRead(LED));
      if (digitalRead(LED) == LOW){
        server.send(200, "text/plain", "on");
      }
      else{
        server.send(200, "text/plain", "off");
      }
  });

  // Add CORS headers for all requests
  server.onNotFound([](){
    if (server.method() == HTTP_OPTIONS) {
      server.sendHeader("Access-Control-Allow-Origin", "*");
      server.sendHeader("Access-Control-Max-Age", "10000");
      server.sendHeader("Access-Control-Allow-Methods", "PUT,POST,GET,OPTIONS");
      server.sendHeader("Access-Control-Allow-Headers", "*");
      server.send(204);
    } else {
      server.send(404, "text/plain", "Not Found");
    }
  });

  server.begin();
}

void loop() {
    server.handleClient();

    float temperature = 21; //dht.readTemperature(); 
    float humidity = 73; //dht.readHumidity();
    float soil_moisture = 55;

    if (isnan(temperature) || isnan(humidity)) { 
        Serial.println("Failed to read from DHT sensor!");
        return;
    }

    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.print(" °C, Humidity: ");
    Serial.print(humidity);
    Serial.println(" %");

     if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(serverName);
        http.addHeader("Content-Type", "application/json");

        String jsonData = "{\"temperature\":" + String(temperature) + ",\"humidity\":" + String(humidity) + ",\"soil_moisture\":" + String(soil_moisture) + "}";
        int httpResponseCode = http.POST(jsonData);

        http.end();
    } else {
        Serial.println("Error in WiFi connection");
    }

    delay(1000);
}