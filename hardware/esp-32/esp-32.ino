#include "DHT.h"
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "todo";
const char* password = "todotodo";

const char* serverName = "https://sugoi-api.vercel.app/agri/update";

#define DHTPIN 4      // Pin where DHT11 is connected
#define DHTTYPE DHT11 

DHT dht(DHTPIN, DHTTYPE);

void setup() {
    Serial.begin(115200);  
    WiFi.begin(ssid, password); 

    while (WiFi.status() != WL_CONNECTED) {  
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");

    dht.begin(); 
}

void loop() {
    delay(2000); 
    float temperature = dht.readTemperature(); 
    float humidity = dht.readHumidity();
    float soil_moisture = 0;

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


    delay(10000);
}
