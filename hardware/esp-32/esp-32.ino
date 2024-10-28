#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "Yamete";
const char* password = "Todotodo";

WebServer server(3000);
int LED = 13;

void setup() {
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);
  
  Serial.begin(9600);

  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());

  // Basic route for testing connectivity
  server.on("/", HTTP_GET, []() {
      server.send(200, "text/plain", "ESP32 server is up and running");
  });

  // Toggle LED route
  server.on("/toggle-led", HTTP_GET, []() {
      digitalWrite(LED, !digitalRead(LED));
      if (digitalRead(LED) == LOW){
        server.send(200, "text/plain", "LED is ON");
      }
      else{
        server.send(200, "text/plain", "LED is OFF");
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
}