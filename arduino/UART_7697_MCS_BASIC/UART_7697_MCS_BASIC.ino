#include <LWiFi.h>
#include <WiFiClient.h>
#include "MCS.h"

// WIFI 設定
#define _SSID "CAVEDU_02"
#define _KEY  "12345678"
int status = WL_IDLE_STATUS;

// MCS 測試裝置設定
MCSDevice mcs("DAbXmRRG", "rhDZFokaNR8b6r7e");

// MCS 通道設定
MCSControllerOnOff led("LED");

// 連 WIFI 的副函式
void connectedWIFI() {
  while (WL_CONNECTED != WiFi.status())
  {
    Serial.print("Wifi Connecting...");
    WiFi.begin(_SSID, _KEY);
  }
  Serial.println("WiFi Connected !!");
}

// 連 MCS
void connectMCS() {

  mcs.addChannel(led);
  
  while (!mcs.connected())
  {
    Serial.print("MCS Connecting...");
    mcs.connect();
  }
  Serial.println("MCS Connected !!");
}

// 確認是否連線MCS
void reconnectedMCS() {

  while (!mcs.connected())
  {
    Serial.print("re-connect to MCS...");
    mcs.connect();
    Serial.println("connected !!");
  }
}

//   初始設定 ( 只跑一次 ) 
void setup() {

  Serial.begin(9600);       // 胞率

  pinMode(7, OUTPUT);       // 內建LED燈

  connectedWIFI();         // WIFI連線

  connectMCS();          // MCS連線

  Serial.print("finish");
}

// 無限迴圈
void loop() {

  // mcs.process 允許後臺處理
  mcs.process(100);

  // 確認MCS上的控制元件是否更新
  if (led.updated())
  {
    // 寫入訊號
    digitalWrite(7, led.value() ? HIGH : LOW);
  }

  reconnectedMCS();

}
