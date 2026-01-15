#ifndef JSON_HANDLER_H
#define JSON_HANDLER_H

#include "config.h"
#include "AlarmSystem.h"
#include "SensorManager.h"
#include "PIDController.h"
#include "ButtonManager.h"
#include <ArduinoJson.h>

class JSONHandler {
private:
  AlarmSystem* alarmSystem;
  SensorManager* sensorManager;
  PIDController* pidController;
  ButtonManager* buttonManager;
  
  void handleGetStatus(JsonDocument& response);
  void handleSetConfig(const JsonDocument& request, JsonDocument& response);
  void handleAckAlarm(const JsonDocument& request, JsonDocument& response);
  void handleSetSimulation(const JsonDocument& request, JsonDocument& response);
  void handleToggleEnable(const JsonDocument& request, JsonDocument& response);
  void handleAutotune(const JsonDocument& request, JsonDocument& response);
  void handleSetState(const JsonDocument& request, JsonDocument& response);
  
  void addSensorData(JsonDocument& doc);
  void addPIDData(JsonDocument& doc);
  void addAlarmData(JsonDocument& doc);
  void addConfigData(JsonDocument& doc);

public:
  JSONHandler(AlarmSystem* alarm, SensorManager* sensor, PIDController* pid, ButtonManager* button);
  void processCommand(const String& command);
  void sendResponse(const JsonDocument& response);
};

#endif