#include <HardwareSerial.h>
#include <Wire.h>

// RE and DE Pins set the RS485 module to Receiver or Transmitter mode
#define RE 16
#define DE 17

// Modbus RTU requests for reading NPK values
const byte nitro[] = {0x01, 0x03, 0x00, 0x1e, 0x00, 0x01, 0xe4, 0x0c};
const byte phos[] = {0x01, 0x03, 0x00, 0x1f, 0x00, 0x01, 0xb5, 0xcc};
const byte pota[] = {0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xc0};

// A variable used to store NPK values
byte values[11];

// Use Hardware Serial (Serial1 or Serial2) for RS485 communication
HardwareSerial mod(1);

void setup() {
  // Set the baud rate for the main Serial port (USB)
  Serial.begin(9600);

  // Set the baud rate and GPIO pins for the RS485 communication
  mod.begin(9600, SERIAL_8N1, 2, 4);

  // Define pin modes for RE and DE
  pinMode(RE, OUTPUT);
  pinMode(DE, OUTPUT);
  
  delay(500);
}

void loop() {
  // Read values
  byte val1, val2, val3;
  val1 = nitrogen();
  delay(250);
  val2 = phosphorous();
  delay(250);
  val3 = potassium();
  delay(250);

  // Print values to the serial monitor
  Serial.print("Nitrogen: ");
  Serial.print(val1);
  Serial.println(" mg/kg");
  Serial.print("Phosphorous: ");
  Serial.print(val2);
  Serial.println(" mg/kg");
  Serial.print("Potassium: ");
  Serial.print(val3);
  Serial.println(" mg/kg");

  delay(2000);
}

// Decipher data from the npk sensor
byte nitrogen() {
  digitalWrite(DE, HIGH);
  digitalWrite(RE, HIGH);
  delay(10);

  if (mod.write(nitro, sizeof(nitro)) == 8) {
    digitalWrite(DE, LOW);
    digitalWrite(RE, LOW);
    delay(10);
    for (byte i = 0; i < 7; i++) {
      if (mod.available()) {
        values[i] = mod.read();
        Serial.print(values[i], HEX);
        Serial.print(" ");
      }
    }
    Serial.println();
  }
  return values[4];
}

byte phosphorous() {
  digitalWrite(DE, HIGH);
  digitalWrite(RE, HIGH);
  delay(10);

  if (mod.write(phos, sizeof(phos)) == 8) {
    digitalWrite(DE, LOW);
    digitalWrite(RE, LOW);
    delay(10);
    for (byte i = 0; i < 7; i++) {
      if (mod.available()) {
        values[i] = mod.read();
        Serial.print(values[i], HEX);
        Serial.print(" ");
      }
    }
    Serial.println();
  }
  return values[4];
}

byte potassium() {
  digitalWrite(DE, HIGH);
  digitalWrite(RE, HIGH);
  delay(10);

  if (mod.write(pota, sizeof(pota)) == 8) {
    digitalWrite(DE, LOW);
    digitalWrite(RE, LOW);
    delay(10);
    for (byte i = 0; i < 7; i++) {
      if (mod.available()) {
        values[i] = mod.read();
        Serial.print(values[i], HEX);
        Serial.print(" ");
      }
    }
    Serial.println();
  }
  return values[4];
}
