#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

// Wi-Fi Credentials (2.4 GHz only)
struct WifiCredential {
  const char* ssid;
  const char* password;
  IPAddress localIP;
  IPAddress gateway;
};

WifiCredential wifiCredentials[] = {
  {"Vishwa", "vishwa@21062002", IPAddress(192, 168, 0, 200), IPAddress(192, 168, 0, 1)},
  {"Gramle_Jio", "Appu@123", IPAddress(192, 168, 31, 200), IPAddress(192, 168, 31, 1)}
};

const int wifiCredentialCount = sizeof(wifiCredentials) / sizeof(wifiCredentials[0]);
const unsigned long wifiConnectTimeoutMs = 15000;

// Shared network settings
IPAddress subnet(255, 255, 255, 0);     // Subnet mask
IPAddress primaryDNS(8, 8, 8, 8);       // Optional DNS
IPAddress secondaryDNS(8, 8, 4, 4);

WiFiUDP udp;
const unsigned int localUdpPort = 4210;
char incomingPacket[255];

// NodeMCU Pin Mapping
#define PIN_RED    D1
#define PIN_YELLOW D2
#define PIN_BLUE   D5
#define PIN_BUZZER D6

enum State { IDLE, WAITING, RUNNING, OUT_OF_TOKENS };
State currentState = IDLE;

void setLEDs(bool red, bool yellow, bool blue) {
  digitalWrite(PIN_RED, red ? HIGH : LOW);
  digitalWrite(PIN_YELLOW, yellow ? HIGH : LOW);
  digitalWrite(PIN_BLUE, blue ? HIGH : LOW);
}

// Helper tone functions (works for both active and passive buzzers)
void shortBeep() {
  for(int i=0;i<3;i++)
  {
    digitalWrite(PIN_BUZZER, HIGH);
    delay(120);
    digitalWrite(PIN_BUZZER, LOW);
    if(i<2)
    {
      delay(100);
    }
  }
}

void longBeep() {
  digitalWrite(PIN_BUZZER, HIGH);
  delay(800);
  digitalWrite(PIN_BUZZER, LOW);
}

void updateLED() {
  switch (currentState) {
    case WAITING:
      setLEDs(false, true, false);   // Yellow
      shortBeep();                   // Short Beep for prompt dispatched
      break;

    case RUNNING:
      setLEDs(false, false, true);   // Blue
      break;
    case OUT_OF_TOKENS:
      setLEDs(true, false, false);   // Red
      longBeep();                    // Long Warning Beep
      break;

    case IDLE:
    default:
      setLEDs(false, false, false);  // Off
      break;
  }
}

bool connectToWiFi() {
  WiFi.mode(WIFI_STA);

  for (int i = 0; i < wifiCredentialCount; i++) {
    Serial.print("\nConnecting to Wi-Fi: ");
    Serial.println(wifiCredentials[i].ssid);

    WiFi.disconnect();
    delay(200);

    // Configure this Wi-Fi's Static IP before connecting
    if (!WiFi.config(wifiCredentials[i].localIP, wifiCredentials[i].gateway, subnet, primaryDNS, secondaryDNS)) {
      Serial.println("Failed to configure Static IP");
    }

    WiFi.begin(wifiCredentials[i].ssid, wifiCredentials[i].password);

    unsigned long startedAt = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - startedAt < wifiConnectTimeoutMs) {
      setLEDs(false, true, false); delay(200);
      setLEDs(false, false, false); delay(200);
      Serial.print(".");
    }

    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\nWiFi Connected!");
      Serial.print("Connected SSID: ");
      Serial.println(wifiCredentials[i].ssid);
      return true;
    }

    Serial.println("\nWiFi not connected, trying next saved network...");
  }

  return false;
}

void setup() {
  Serial.begin(115200);

  pinMode(PIN_RED, OUTPUT);
  pinMode(PIN_YELLOW, OUTPUT);
  pinMode(PIN_BLUE, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  digitalWrite(PIN_BUZZER, LOW);

  // Self-test LED + Audio check
  setLEDs(true, false, false); delay(150);
  setLEDs(false, true, false); delay(150);
  setLEDs(false, false, true); delay(150);
  setLEDs(false, false, false);
  shortBeep();

  while (!connectToWiFi()) {
    Serial.println("No saved Wi-Fi connected. Retrying all networks in 5 seconds...");
    setLEDs(true, true, false);
    delay(5000);
  }

  Serial.print("NodeMCU Fixed IP Address: ");
  Serial.println(WiFi.localIP());

  // Two quick blinks and double beep to confirm connection
  for (int i = 0; i < 2; i++) {
    setLEDs(false, false, true);
    digitalWrite(PIN_BUZZER, HIGH);
    delay(100);
    setLEDs(false, false, false);
    digitalWrite(PIN_BUZZER, LOW);
    delay(100);
  }

  udp.begin(localUdpPort);
  updateLED();
}

void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    int len = udp.read(incomingPacket, 255);
    if (len > 0) {
      incomingPacket[len] = '\0';
      char cmd = incomingPacket[0];

      switch (cmd) {
        case 'Y': currentState = WAITING; break;
        case 'B': currentState = RUNNING; break;
        case 'R': currentState = OUT_OF_TOKENS; break;
        case 'O': currentState = IDLE; break;
        default: break;
      }
      updateLED();
    }
  }
}
