#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>

// WiFi credentials
const char* ssid = "Urmi";        
const char* password = "zdtm8900"; 

// Flask server details
const char* serverName = "http://192.168.15.121:5001/log";

// RFID Pins
#define RST_PIN   2
#define SS_PIN    15

MFRC522 mfrc522(SS_PIN, RST_PIN);

// Known cards
byte user1UID[4] = {0x71, 0x18, 0x6E, 0x05};
byte user2UID[4] = {0xDD, 0xB6, 0xAA, 0x04};

// WiFi + HTTP
WiFiClient client;
HTTPClient http;

// LED pin (found: GPIO16)
#define LED_PIN 16

// LED states
enum LedMode { WIFI_CONNECTING, WIFI_CONNECTED, CARD_FLASH };
LedMode ledMode = WIFI_CONNECTING;

unsigned long previousMillis = 0;  
unsigned long interval = 50;       // default fast blink while connecting
bool ledState = HIGH;              // LED off (active low)

// For card flash timing
unsigned long cardFlashStart = 0;
bool cardFlashing = false;

// Compare two UIDs
bool compareUID(byte *uid, byte *knownUID) {
  for (byte i = 0; i < 4; i++) {
    if (uid[i] != knownUID[i]) return false;
  }
  return true;
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH); // off by default

  SPI.begin();
  mfrc522.PCD_Init();

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...\n");
}

void handleLED() {
  unsigned long currentMillis = millis();

  // Card flash overrides other modes
  if (cardFlashing) {
    digitalWrite(LED_PIN, LOW); // ON
    if (currentMillis - cardFlashStart >= 500) {
      digitalWrite(LED_PIN, HIGH); // OFF
      cardFlashing = false;
      // return to heartbeat after flash
      ledMode = (WiFi.status() == WL_CONNECTED) ? WIFI_CONNECTED : WIFI_CONNECTING;
    }
    return;
  }

  // Set interval depending on mode
  if (ledMode == WIFI_CONNECTING) {
    interval = 50;   // fast blink
  } else if (ledMode == WIFI_CONNECTED) {
    interval = 1000; // heartbeat blink
  }

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    ledState = !ledState;
    digitalWrite(LED_PIN, ledState ? LOW : HIGH);  
    // (LOW = ON, HIGH = OFF) so invert logic
  }
}

void loop() {
  handleLED();

  // Update mode depending on WiFi status
  if (!cardFlashing) {
    if (WiFi.status() == WL_CONNECTED) {
      if (ledMode != WIFI_CONNECTED) {
        ledMode = WIFI_CONNECTED;
        Serial.println("Connected to WiFi!");
      }
    } else {
      ledMode = WIFI_CONNECTING;
    }
  }

  // RFID handling
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
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

    // Trigger LED flash (500ms ON)
    cardFlashing = true;
    cardFlashStart = millis();

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
  }
}
