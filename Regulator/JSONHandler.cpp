#include "JSONHandler.h"
#include <Arduino.h>

JSONHandler::JSONHandler(AlarmSystem* alarm, SensorManager* sensor, PIDController* pid, ButtonManager* button) 
  : alarmSystem(alarm), sensorManager(sensor), pidController(pid), buttonManager(button) {
}

void JSONHandler::processCommand(const String& command) {
  StaticJsonDocument<JSON_BUFFER_SIZE> request;
  StaticJsonDocument<JSON_BUFFER_SIZE> response;
  
  DeserializationError error = deserializeJson(request, command);
  if (error) {
    response["error"] = "Invalid JSON";
    response["errorCode"] = ERROR_COMMUNICATION;
    sendResponse(response);
    return;
  }
  
  String cmd = request["command"];
  if (cmd.length() == 0) {
    response["error"] = "Missing command";
    response["errorCode"] = ERROR_COMMUNICATION;
    sendResponse(response);
    return;
  }
  response["command"] = cmd;
  response["timestamp"] = millis();
  
  if (cmd == "getStatus") {
    handleGetStatus(response);
  } else if (cmd == "setConfig") {
    handleSetConfig(request, response);
  } else if (cmd == "ackAlarm") {
    handleAckAlarm(request, response);
  } else if (cmd == "setSimulation") {
    handleSetSimulation(request, response);
  } else if (cmd == "toggleEnable") {
    handleToggleEnable(request, response);
  } else {
    response["error"] = "Unknown command";
    response["errorCode"] = ERROR_COMMUNICATION;
    sendResponse(response);
    return;
  }
  
  sendResponse(response);
}

void JSONHandler::handleGetStatus(JsonDocument& response) {
  if (!alarmSystem || !sensorManager || !pidController || !buttonManager) {
    response["error"] = "System not initialized";
    response["errorCode"] = ERROR_CONFIGURATION;
    return;
  }
  response["status"] = "ok";
  addSensorData(response);
  addPIDData(response);
  addAlarmData(response);
  addConfigData(response);
}

void JSONHandler::handleSetConfig(const JsonDocument& request, JsonDocument& response) {
  if (!pidController || !alarmSystem) {
    response["error"] = "System not initialized";
    response["errorCode"] = ERROR_CONFIGURATION;
    return;
  }
  
  // Handle single PID config
  if (request.containsKey("regulator_id")) {
    int regulatorId = request["regulator_id"];
    if (regulatorId >= 0 && regulatorId < NUM_PIDS) {
      PIDConfig config = pidController->getPIDConfig(regulatorId);
      
      if (request.containsKey("type")) config.type = (ControllerType)request["type"].as<int>();
      if (request.containsKey("setpoint")) config.setpoint = request["setpoint"];
      if (request.containsKey("kp")) config.kp = request["kp"];
      if (request.containsKey("ki")) config.ki = request["ki"];
      if (request.containsKey("kd")) config.kd = request["kd"];
      if (request.containsKey("sensorIndex")) config.sensorIndex = request["sensorIndex"];
      if (request.containsKey("enabled")) config.enabled = request["enabled"];
      if (request.containsKey("manualOutput")) config.manualOutput = request["manualOutput"];
      
      pidController->setPIDConfig(regulatorId, config);
    }
  }
  
  response["status"] = "configured";
  // Add full system status
  addSensorData(response);
  addPIDData(response);
  addAlarmData(response);
  addConfigData(response);
}

void JSONHandler::handleAckAlarm(const JsonDocument& request, JsonDocument& response) {
  if (!alarmSystem) {
    response["error"] = "System not initialized";
    response["errorCode"] = ERROR_CONFIGURATION;
    return;
  }
  
  if (request.containsKey("regulator_id")) {
    int regulatorId = request["regulator_id"];
    if (regulatorId >= 0 && regulatorId < NUM_PIDS) {
      alarmSystem->acknowledgeAlarm(regulatorId);
      response["status"] = "acknowledged";
    } else {
      response["error"] = "Invalid regulator_id";
      response["errorCode"] = ERROR_COMMUNICATION;
    }
  } else {
    response["error"] = "Missing regulator_id";
    response["errorCode"] = ERROR_COMMUNICATION;
  }
  
  // Add full system status
  addSensorData(response);
  addPIDData(response);
  addAlarmData(response);
  addConfigData(response);
}

void JSONHandler::handleSetSimulation(const JsonDocument& request, JsonDocument& response) {
  if (!sensorManager) {
    response["error"] = "System not initialized";
    response["errorCode"] = ERROR_CONFIGURATION;
    return;
  }
  
  // Handle single sensor simulation
  if (request.containsKey("sensorIndex")) {
    int sensorIndex = request["sensorIndex"];
    if (sensorIndex >= 0 && sensorIndex < TOTAL_SENSORS) {
      if (request.containsKey("simulated")) {
        sensorManager->enableSimulation(sensorIndex, request["simulated"]);
      }
      if (request.containsKey("value")) {
        sensorManager->setSimulatedValue(sensorIndex, request["value"]);
      }
    }
  }
  
  response["status"] = "simulation_set";
  // Add full system status
  addSensorData(response);
  addPIDData(response);
  addAlarmData(response);
  addConfigData(response);
}

void JSONHandler::addSensorData(JsonDocument& doc) {
  if (!sensorManager) return;
  
  JsonArray sensors = doc.createNestedArray("sensors");
  for (int i = 0; i < TOTAL_SENSORS; i++) {
    JsonObject sensor = sensors.createNestedObject();
    const SensorReading& reading = sensorManager->getSensorReading(i);
    
    sensor["sensor_id"] = i;
    sensor["temperature"] = reading.temperature;
    sensor["health"] = reading.health;
    sensor["errorCode"] = reading.errorCode;
    sensor["lastUpdate"] = reading.lastUpdate;
    sensor["simulated"] = reading.simulated;
  }
}

void JSONHandler::addPIDData(JsonDocument& doc) {
  if (!pidController || !buttonManager) return;
  
  JsonArray thermostats = doc.createNestedArray("thermostats");
  for (int i = 0; i < NUM_PIDS; i++) {
    JsonObject thermostat = thermostats.createNestedObject();
    const PIDStatus& status = pidController->getPIDStatus(i);
    
    thermostat["regulator_id"] = i;
    thermostat["currentTemp"] = status.input;
    thermostat["output"] = status.output;
    thermostat["setpoint"] = status.setpoint;
    thermostat["enabled"] = status.enabled;
    thermostat["type"] = status.type;
    thermostat["outputActive"] = status.outputActive;
    thermostat["sensorIndex"] = status.sensorIndex;
  }
}

void JSONHandler::addAlarmData(JsonDocument& doc) {
  if (!alarmSystem) return;
  
  JsonArray alarms = doc.createNestedArray("alarms");
  for (int i = 0; i < NUM_PIDS; i++) {
    JsonObject alarm = alarms.createNestedObject();
    AlarmState state = alarmSystem->getAlarmState(i);
    
    alarm["regulator_id"] = i;
    alarm["level"] = state.level;
    alarm["errorCode"] = state.errorCode;
    alarm["acknowledged"] = state.acknowledged;
    alarm["timestamp"] = state.timestamp;
    alarm["active"] = state.active;
  }
}

void JSONHandler::addConfigData(JsonDocument& doc) {
  if (!pidController || !alarmSystem) return;
  
  JsonObject config = doc.createNestedObject("config");
  
  JsonArray pidConfigs = config.createNestedArray("pids");
  for (int i = 0; i < NUM_PIDS; i++) {
    JsonObject pidConfig = pidConfigs.createNestedObject();
    const PIDConfig& cfg = pidController->getPIDConfig(i);
    
    pidConfig["type"] = cfg.type;
    pidConfig["kp"] = cfg.kp;
    pidConfig["ki"] = cfg.ki;
    pidConfig["kd"] = cfg.kd;
    pidConfig["setpoint"] = cfg.setpoint;
    pidConfig["sensorIndex"] = cfg.sensorIndex;
    pidConfig["enabled"] = cfg.enabled;
    pidConfig["manualOutput"] = cfg.manualOutput;
  }
  
  JsonArray alarmConfigs = config.createNestedArray("alarms");
  for (int i = 0; i < NUM_PIDS; i++) {
    JsonObject alarmConfig = alarmConfigs.createNestedObject();
    const AlarmConfig& cfg = alarmSystem->getAlarmConfig(i);
    
    alarmConfig["warningLow"] = cfg.warningLow;
    alarmConfig["warningHigh"] = cfg.warningHigh;
    alarmConfig["alarmLow"] = cfg.alarmLow;
    alarmConfig["alarmHigh"] = cfg.alarmHigh;
    alarmConfig["resetMode"] = cfg.resetMode;
    alarmConfig["enabled"] = cfg.enabled;
  }
}

void JSONHandler::sendResponse(const JsonDocument& response) {
  serializeJson(response, Serial);
  Serial.println();
}

void JSONHandler::handleToggleEnable(const JsonDocument& request, JsonDocument& response) {
  if (!buttonManager) {
    response["error"] = "System not initialized";
    response["errorCode"] = ERROR_CONFIGURATION;
    return;
  }
  
  if (request.containsKey("regulator_id")) {
    int regulatorId = request["regulator_id"];
    if (regulatorId >= 0 && regulatorId < NUM_PIDS) {
      if (request.containsKey("enabled")) {
        bool enabled = request["enabled"];
        buttonManager->setPIDEnabled(regulatorId, enabled);
      } else {
        bool currentState = buttonManager->isPIDEnabled(regulatorId);
        buttonManager->setPIDEnabled(regulatorId, !currentState);
      }
      response["status"] = "toggled";
      response["regulator_id"] = regulatorId;
      response["enabled"] = buttonManager->isPIDEnabled(regulatorId);
    } else {
      response["error"] = "Invalid regulator_id";
      response["errorCode"] = ERROR_COMMUNICATION;
    }
  } else {
    response["error"] = "Missing regulator_id";
    response["errorCode"] = ERROR_COMMUNICATION;
  }
  
  // Add full system status
  addSensorData(response);
  addPIDData(response);
  addAlarmData(response);
  addConfigData(response);
}