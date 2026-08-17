#include <WiFi.h>
#include <WiFiUdp.h>

// Replace "your_ssid" and "your_password" with your desired AP credentials
const char* ssid = "ESP32_AP";
const char* password = "password";

WiFiUDP udp;

void setup() {
  // initialize the serial communication:
  Serial.begin(115200);

  // Create an Access Point
  WiFi.softAP(ssid, password);

  Serial.println("Access Point created");
  Serial.print("IP address: ");
  Serial.println(WiFi.softAPIP());

  // Initialize UDP
  udp.begin(12345); // Choose any port you like
}

void loop() {
  // Read analog input from A0
  int sensorValue = analogRead(A0);

  // Print the analog value to Serial
  Serial.println(sensorValue);

  // Broadcast analog value over UDP
  udp.beginPacket("255.255.255.255", 12345); // Broadcast address and port
  udp.print(sensorValue);
  udp.endPacket();

  // Wait for a bit to prevent saturating the serial data and flooding the network
  delay(100);
}


