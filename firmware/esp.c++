#include <OneWire.h>
#include <DallasTemperature.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

// ============================
// DS18B20 Setup
// ============================
#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// ============================
// Wi-Fi Credentials
// ============================
const char* ssid = "Dat’s IPHONE";
const char* password = "pineapple";

// ============================
// Supabase Credentials
// ============================
// IMPORTANT: no trailing slash
const char* supabaseUrl = "https://fmhxjiqadxdlmalscvoc.supabase.co";
const char* supabaseAnonKey = "sb_publishable_QIs5RteU49_YkZ35JoEfRQ_T2UHVhV_";

// Your table name
const char* tableName = "fan_readings";

// Identify your ESP32
const char* deviceId = "esp32_01";

// Send every 10 seconds
const unsigned long SEND_INTERVAL_MS = 10000;
unsigned long lastSend = 0;

// ============================
// Power constants (Watts)
// ============================
const float P_OFF    = 0.0;
const float P_LOW    = 0.437;
const float P_MEDIUM = 1.182;
const float P_HIGH   = 2.949;

// ============================
// Decide fan_mode + power_w from temperature
// ============================
void computeFanModeAndPower(float tempC, String &fanMode, float &powerW) {
  if (tempC < 22.0) {
    fanMode = "OFF";
    powerW = P_OFF;
  } else if (tempC < 25.0) {
    fanMode = "LOW";
    powerW = P_LOW;
  } else if (tempC < 28.0) {
    fanMode = "MEDIUM";
    powerW = P_MEDIUM;
  } else {
    fanMode = "HIGH";
    powerW = P_HIGH;
  }
}

// ============================
// Wi-Fi connect helper
// ============================
void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.persistent(false);

  Serial.print("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 15000) {
    delay(1000);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWi-Fi connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWi-Fi failed. Will retry in loop.");
  }
}

// ============================
// POST to Supabase
// ============================
int sendToSupabase(float tempC, float powerW, const String &fanMode) {
  // Endpoint: https://<ref>.supabase.co/rest/v1/<table>
  String endpoint = String(supabaseUrl) + "/rest/v1/" + tableName;

  // JSON payload (matches your table columns: device_id, temp_c, power_w, fan_mode)
  String jsonData =
    String("{\"device_id\":\"") + deviceId +
    "\",\"temp_c\":" + String(tempC, 2) +
    ",\"power_w\":" + String(powerW, 3) +
    ",\"fan_mode\":\"" + fanMode + "\"}";

  WiFiClientSecure client;
  client.setInsecure(); // ok for testing/demo

  HTTPClient https;
  if (!https.begin(client, endpoint)) {
    Serial.println("HTTPS begin() failed");
    return -1;
  }

  https.addHeader("Content-Type", "application/json");
  https.addHeader("apikey", supabaseAnonKey);
  https.addHeader("Authorization", String("Bearer ") + supabaseAnonKey);
  https.addHeader("Prefer", "return=minimal");

  int httpCode = https.POST(jsonData);
  String response = https.getString();

  Serial.println("\n--- Supabase POST ---");
  Serial.println(endpoint);
  Serial.print("Payload: ");
  Serial.println(jsonData);
  Serial.print("HTTP code: ");
  Serial.println(httpCode);

  if (response.length() > 0) {
    Serial.print("Response: ");
    Serial.println(response);
  }

  https.end();
  return httpCode;
}

// ============================
// Setup
// ============================
void setup(void) {
  // KEEP baud rate 9600 (as you requested)
  Serial.begin(9600);
  Serial.println("DS18B20 + Supabase (temp, fan_mode, power_w)");

  sensors.begin();
  connectWiFi();
}

// ============================
// Loop
// ============================
void loop(void) {
  // ensure interval
  if (millis() - lastSend < SEND_INTERVAL_MS) return;
  lastSend = millis();

  // reconnect if needed
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi disconnected. Reconnecting...");
    WiFi.disconnect();
    connectWiFi();
    if (WiFi.status() != WL_CONNECTED) return; // skip send this round
  }

  Serial.print("Requesting temperatures...");
  sensors.requestTemperatures();
  Serial.println("DONE");

  float tempC = sensors.getTempCByIndex(0);

  if (tempC == DEVICE_DISCONNECTED_C) {
    Serial.println("Error: Could not read temperature data");
    return;
  }

  // compute fan mode + estimated power
  String fanMode;
  float powerW = 0.0;
  computeFanModeAndPower(tempC, fanMode, powerW);

  // debug prints
  Serial.print("Temperature (C): ");
  Serial.println(tempC);
  Serial.print("fan_mode: ");
  Serial.println(fanMode);
  Serial.print("power_w: ");
  Serial.println(powerW);

  // send to Supabase
  sendToSupabase(tempC, powerW, fanMode);
}
