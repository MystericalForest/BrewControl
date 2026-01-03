#include "TemperatureController.h"
#include "config.h"
#include <Arduino.h>

TemperatureController::TemperatureController() 
  : jsonHandler(&alarmSystem, &sensorManager, &pidController, &buttonManager) {
}

void TemperatureController::begin() {
  Serial.begin(SERIAL_BAUD);
  
  // Initialize all subsystems
  alarmSystem.begin();
  sensorManager.begin();
  pidController.begin();
  buttonManager.begin();
  
  // Set default configurations
  for (int i = 0; i < NUM_PIDS; i++) {
    PIDConfig pidConfig;
    pidConfig.sensorIndex = -1; // No sensor assigned by default
    pidConfig.enabled = false; // Fail-safe default
    pidController.setPIDConfig(i, pidConfig);
    
    AlarmConfig alarmConfig;
    alarmConfig.enabled = true;
    alarmSystem.setAlarmConfig(i, alarmConfig);
  }
  
  lastUpdate = millis();
}

void TemperatureController::update() {
  processSerialInput();
  buttonManager.update();
  
  unsigned long now = millis();
  if ((unsigned long)(now - lastUpdate) >= UPDATE_INTERVAL) {
    updateSystem();
    lastUpdate = now;
  }
}

void TemperatureController::updateSystem() {
  // Update sensors
  sensorManager.update();
  
  // Update each PID controller
  for (int i = 0; i < NUM_PIDS; i++) {
    const PIDConfig& pidConfig = pidController.getPIDConfig(i);
    
    // Get sensor reading from configured sensor
    float sensorValue = INVALID_SENSOR_VALUE;
    if (pidConfig.sensorIndex >= 0 && pidConfig.sensorIndex < TOTAL_SENSORS) {
      SensorReading reading = sensorManager.getSensorReading(pidConfig.sensorIndex);
      sensorValue = reading.temperature;
      
      // Handle sensor alarms
      if (reading.health == SENSOR_FAILED) {
        alarmSystem.setTechnicalAlarm(i, reading.errorCode);
      } else {
        alarmSystem.clearTechnicalAlarm(i);
        // Update process alarms only if we have valid sensor data
        if (sensorValue != INVALID_SENSOR_VALUE) {
          alarmSystem.updateProcessAlarm(i, sensorValue);
        }
      }
    } else if (pidConfig.enabled) {
      // PID enabled but no valid sensor configured - technical alarm
      alarmSystem.setTechnicalAlarm(i, ERROR_CONFIGURATION);
    }
    
    // Update PID controller with button enable state
    bool outputEnabled = alarmSystem.isOutputEnabled(i) && buttonManager.isPIDEnabled(i);
    pidController.update(i, sensorValue, outputEnabled);
  }
  
  // Update alarm LEDs
  alarmSystem.updateLEDs();
}

void TemperatureController::processSerialInput() {
  static char buffer[JSON_BUFFER_SIZE];
  static int bufferIndex = 0;
  
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (bufferIndex > 0) {
        buffer[bufferIndex] = '\0';
        jsonHandler.processCommand(String(buffer));
        bufferIndex = 0;
      }
    } else {
      if (bufferIndex < JSON_BUFFER_SIZE - 1) {
        buffer[bufferIndex++] = c;
      } else {
        // Buffer overflow - consume remaining characters until newline
        StaticJsonDocument<256> errorResponse;
        errorResponse["error"] = "Command too long";
        errorResponse["errorCode"] = ERROR_COMMUNICATION;
        serializeJson(errorResponse, Serial);
        Serial.println();
        bufferIndex = 0;
        
        // Consume remaining characters until newline
        while (Serial.available() && Serial.read() != '\n');
      }
    }
  }
}