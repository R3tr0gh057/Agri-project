#include <WiFi.h>
#include <WebServer.h>

const char *ssid = "todo";        // Your WiFi SSID
const char *password = "todotodo";    // Your WiFi Password

WebServer server(3000);

int ledPin1 = 13; // GPIO 13 for LED 1 (blue)
int ledPin2 = 12; // GPIO 12 for LED 2 (red)
int temp = 0;
int temp2 = 0;

void setup() {
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);
  digitalWrite(ledPin1, LOW);
  digitalWrite(ledPin2, LOW);
  Serial.begin(9600);

  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.print(".");
  }
  Serial.println("Connected to WiFi");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  server.on("/toggle-led1", HTTP_GET, []() {
      digitalWrite(ledPin1, !digitalRead(ledPin1));
      if (digitalRead(ledPin1) == HIGH){
        server.send(200, "text/plain", "Hall room lights are turned on");
      }
      else{
        server.send(200, "text/plain", "Hall room lights are turned off");
      }
  });

  server.on("/toggle-led2", HTTP_GET, []() {
      digitalWrite(ledPin2, !digitalRead(ledPin2));
      if (digitalRead(ledPin2) == HIGH){
        server.send(200, "text/plain", "Bedroom lights are turned on");
      }
      else{
        server.send(200, "text/plain", "Bedroom lights are turned off");
      }
  });

  server.on("/deactivate", HTTP_GET, []() {
      digitalWrite(ledPin1, LOW);
      digitalWrite(ledPin2, LOW);
      server.send(200, "text/plain", "All lights are turned off");
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
