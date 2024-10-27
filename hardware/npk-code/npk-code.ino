#include <ModbusMaster.h>

#define MAX485_DE      32
#define MAX485_RE_NEG  33

#define RXD2 16
#define TXD2 17

// Modbus RTU requests for reading NPK values
const byte nitro[] = {0x01, 0x03, 0x00, 0x1E, 0x00, 0x01, 0xE4, 0x0C};
const byte phos[] = {0x01, 0x03, 0x00, 0x1F, 0x00, 0x01, 0xB5, 0xCC};
const byte pota[] = {0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xC0};

// Buffer to store response from sensor
byte values[7];

void setup() {
  Serial.begin(9600);
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);

  pinMode(MAX485_RE_NEG, OUTPUT);
  pinMode(MAX485_DE, OUTPUT);
  digitalWrite(MAX485_RE_NEG, LOW);
  digitalWrite(MAX485_DE, LOW);
}

void loop() {
  // Read Nitrogen (N)
  int nitrogenValue = readSensor(nitro);
  Serial.print("Nitrogen: ");
  Serial.print(nitrogenValue);
  Serial.println(" mg/kg");

  delay(250);

  // Read Phosphorus (P)
  int phosphorusValue = readSensor(phos);
  Serial.print("Phosphorus: ");
  Serial.print(phosphorusValue);
  Serial.println(" mg/kg");

  delay(250);

  // Read Potassium (K)
  int potassiumValue = readSensor(pota);
  Serial.print("Potassium: ");
  Serial.print(potassiumValue);
  Serial.println(" mg/kg");

  Serial.println("\n\n\n");

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
