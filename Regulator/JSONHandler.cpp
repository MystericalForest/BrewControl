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
  
  if (request.containsKey("pids")) {
    JsonArray pids = request["pids"].as<JsonArray>();
    for (int i = 0; i < NUM_PIDS && i < pids.size(); i++) {
      JsonObject pidObj = pids[i];
      PIDConfig config = pidController->getPIDConfig(i);
      
      if (pidObj.containsKey("type")) {
        int typeValue = pidObj["type"].as<int>();
        if (typeValue >= 0 && typeValue <= 2) {
          config.type = (ControllerType)typeValue;
        }
      }
      if (pidObj.containsKey("setpoint")) {
        float value = pidObj["setpoint"];
        if (isfinite(value) && value >= -100 && value <= 200) {
          config.setpoint = value;
        }
      }
      if (pidObj.containsKey("kp")) {
        float value = pidObj["kp"];
        if (isfinite(value) && value >= 0 && value <= 1000) {
          config.kp = value;
        }
      }
      if (pidObj.containsKey("ki")) {
        float value = pidObj["ki"];
        if (isfinite(value) && value >= 0 && value <= 1000) {
          config.ki = value;
        }
      }
      if (pidObj.containsKey("kd")) {
        float value = pidObj["kd"];
        if (isfinite(value) && value >= 0 && value <= 1000) {
          config.kd = value;
        }
      }
      if (pidObj.containsKey("sensorIndex")) {
        int sensorIdx = pidObj["sensorIndex"];
        if (sensorIdx >= 0 && sensorIdx < TOTAL_SENSORS) {
          config.sensorIndex = sensorIdx;
        }
      }
      if (pidObj.containsKey("enabled")) config.enabled = pidObj["enabled"];
      if (pidObj.containsKey("manualOutput")) {
        float value = pidObj["manualOutput"];
        if (isfinite(value) && value >= 0 && value <= 255) {
          config.manualOutput = value;
        }
      }
      
      pidController->setPIDConfig(i, config);
    }
  }
  
  if (request.containsKey("alarms")) {
    JsonArray alarms = request["alarms"].as<JsonArray>();
    for (int i = 0; i < NUM_PIDS && i < alarms.size(); i++) {
      JsonObject alarmObj = alarms[i];
      AlarmConfig config = alarmSystem->getAlarmConfig(i);
      
      if (alarmObj.containsKey("warningLow")) {
        float value = alarmObj["warningLow"];
        if (isfinite(value) && value >= -100 && value <= 200) {
          config.warningLow = value;
        }
      }
      if (alarmObj.containsKey("warningHigh")) {
        float value = alarmObj["warningHigh"];
        if (isfinite(value) && value >= -100 && value <= 200) {
          config.warningHigh = value;
        }
      }
      if (alarmObj.containsKey("alarmLow")) {
        float value = alarmObj["alarmLow"];
        if (isfinite(value) && value >= -100 && value <= 200) {
          config.alarmLow = value;
        }
      }
      if (alarmObj.containsKey("alarmHigh")) {
        float value = alarmObj["alarmHigh"];
        if (isfinite(value) && value >= -100 && value <= 200) {
          config.alarmHigh = value;
        }
      }
      if (alarmObj.containsKey("resetMode")) {
        int resetValue = alarmObj["resetMode"].as<int>();
        if (resetValue >= 0 && resetValue <= 1) {
          config.resetMode = (ResetMode)resetValue;
        }
      }
      if (alarmObj.containsKey("enabled")) config.enabled = alarmObj["enabled"];
      
      alarmSystem->setAlarmConfig(i, config);
    }
  }
  
  response["status"] = "configured";
}

void JSONHandler::handleAckAlarm(const JsonDocument& request, JsonDocument& response) {
  if (!alarmSystem) {
    response["error"] = "System not initialized";
    response["errorCode"] = ERROR_CONFIGURATION;
    return;
  }
  
  if (request.containsKey("pidIndex")) {
    int pidIndex = request["pidIndex"];
    if (pidIndex >= 0 && pidIndex < NUM_PIDS) {
      alarmSystem->acknowledgeAlarm(pidIndex);
      response["status"] = "acknowledged";
    } else {
      response["error"] = "Invalid pidIndex";
      response["errorCode"] = ERROR_COMMUNICATION;
    }
  } else {
    response["error"] = "Missing pidIndex";
    response["errorCode"] = ERROR_COMMUNICATION;
  }
}

void JSONHandler::handleSetSimulation(const JsonDocument& request, JsonDocument& response) {
  if (!sensorManager) {
    response["error"] = "System not initialized";
    response["errorCode"] = ERROR_CONFIGURATION;
    return;
  }
  
  if (request.containsKey("sensors")) {
    JsonArray sensors = request["sensors"].as<JsonArray>();
    for (int i = 0; i < TOTAL_SENSORS && i < sensors.size(); i++) {
      JsonObject sensorObj = sensors[i];
      if (sensorObj.containsKey("simulated")) {
        sensorManager->enableSimulation(i, sensorObj["simulated"]);
      }
      if (sensorObj.containsKey("value")) {
        float value = sensorObj["value"];
        if (isfinite(value) && value >= -100 && value <= 200) {
          sensorManager->setSimulatedValue(i, value);
        }
      }
    }
  }
  response["status"] = "simulation_set";
}

void JSONHandler::addSensorData(JsonDocument& doc) {
  if (!sensorManager) return;
  
  JsonArray sensors = doc.createNestedArray("sensors");
  for (int i = 0; i < TOTAL_SENSORS; i++) {
    JsonObject sensor = sensors.createNestedObject();
    const SensorReading& reading = sensorManager->getSensorReading(i);
    
    sensor["index"] = i;
    sensor["temperature"] = reading.temperature;
    sensor["health"] = reading.health;
    sensor["errorCode"] = reading.errorCode;
    sensor["lastUpdate"] = reading.lastUpdate;
    sensor["simulated"] = reading.simulated;
  }
}

void JSONHandler::addPIDData(JsonDocument& doc) {
  if (!pidController || !buttonManager) return;
  
  JsonArray pids = doc.createNestedArray("pids");
  for (int i = 0; i < NUM_PIDS; i++) {
    JsonObject pid = pids.createNestedObject();
    const PIDStatus& status = pidController->getPIDStatus(i);
    
    pid["index"] = i;
    pid["input"] = status.input;
    pid["output"] = status.output;
    pid["setpoint"] = status.setpoint;
    pid["enabled"] = status.enabled;
    pid["type"] = status.type;
    pid["outputActive"] = status.outputActive;
    pid["buttonEnabled"] = buttonManager->isPIDEnabled(i);
  }
}

void JSONHandler::addAlarmData(JsonDocument& doc) {
  if (!alarmSystem) return;
  
  JsonArray alarms = doc.createNestedArray("alarms");
  for (int i = 0; i < NUM_PIDS; i++) {
    JsonObject alarm = alarms.createNestedObject();
    AlarmState state = alarmSystem->getAlarmState(i);
    
    alarm["pidIndex"] = i;
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
  
  if (request.containsKey("pidIndex")) {
    int pidIndex = request["pidIndex"];
    if (pidIndex >= 0 && pidIndex < NUM_PIDS) {
      if (request.containsKey("enabled")) {
        bool enabled = request["enabled"];
        buttonManager->setPIDEnabled(pidIndex, enabled);
      } else {
        bool currentState = buttonManager->isPIDEnabled(pidIndex);
        buttonManager->setPIDEnabled(pidIndex, !currentState);
      }
      response["status"] = "toggled";
      response["pidIndex"] = pidIndex;
      response["enabled"] = buttonManager->isPIDEnabled(pidIndex);
    } else {
      response["error"] = "Invalid pidIndex";
      response["errorCode"] = ERROR_COMMUNICATION;
    }
  } else {
    response["error"] = "Missing pidIndex";
    response["errorCode"] = ERROR_COMMUNICATION;
  }
}