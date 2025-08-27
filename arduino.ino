#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>

// WiFi credentials
const char* ssid = "ICT_Cell_Office_2.4G";        // Your WiFi SSID
const char* password = "Ictcell@Buet"; // Your WiFi password

// Flask server details
const char* serverName = "http://192.168.50.154:5000/log";

// RFID Pins
#define RST_PIN   2
#define SS_PIN    15

MFRC522 mfrc522(SS_PIN, RST_PIN);

// Known cards
byte user1UID[4] = {0x71, 0x18, 0x6E, 0x05};
byte user2UID[4] = {0xDD, 0xB6, 0xAA, 0x04};

WiFiClient client;
HTTPClient http;

bool compareUID(byte *uid, byte *knownUID) {
  for (byte i = 0; i < 4; i++) {
    if (uid[i] != knownUID[i]) return false;
  }
  return true;
}

void setup() {
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".\n");
  }
  Serial.println("\nConnected to WiFi!");
}

void loop() {
  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial()) return;

  // Build UID string
  String uidStr = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) uidStr += "0";
    uidStr += String(mfrc522.uid.uidByte[i], HEX);
  }
  uidStr.toUpperCase();

  // Identify user
  String user = "Unknown";
  if (compareUID(mfrc522.uid.uidByte, user1UID)) {
    user = "User 1";
  } else if (compareUID(mfrc522.uid.uidByte, user2UID)) {
    user = "User 2";
  }

  Serial.printf("Scanned UID: %s (%s)\n", uidStr.c_str(), user.c_str());

  // Send data to Flask server
  if (WiFi.status() == WL_CONNECTED) {
    http.begin(client, serverName);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    String postData = "uid=" + uidStr + "&user=" + user;
    int httpResponseCode = http.POST(postData);

    if (httpResponseCode > 0) {
      Serial.printf("Server Response: %d\n", httpResponseCode);
    } else {
      Serial.printf("Error sending data: %s\n", http.errorToString(httpResponseCode).c_str());
    }

    http.end();
  }

  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();

  delay(1000);
}
