#include "SensorManager.h"
#include <Arduino.h>
#include <SPI.h>

SensorManager::SensorManager() : oneWire(ONEWIRE_PIN), dallasTemp(&oneWire) {
}

void SensorManager::begin() {
  SPI.begin();
  dallasTemp.begin();
  
  // Initialize PT100 CS pins
  for (int i = 0; i < NUM_PT100_SENSORS; i++) {
    pinMode(pt100CsPins[i], OUTPUT);
    digitalWrite(pt100CsPins[i], HIGH);
  }
  
  // Discover OneWire devices
  if (!dallasTemp.setResolution(12)) {
    // Log setResolution failure but continue
  }
  int deviceCount = dallasTemp.getDeviceCount();
  for (int i = 0; i < NUM_ONEWIRE_SENSORS && i < deviceCount; i++) {
    if (!dallasTemp.getAddress(oneWireAddresses[i], i)) {
      // Mark sensor as failed and zero address
      memset(oneWireAddresses[i], 0, 8);
    }
  }
  
  // Initialize sensor configs with default values
  for (int i = 0; i < TOTAL_SENSORS; i++) {
    sensorConfigs[i].sensorIndex = i;
    sensorConfigs[i].enabled = true;
    sensorConfigs[i].simulated = false;
    sensorConfigs[i].simulatedValue = 20.0;
    sensorConfigs[i].offset = 0.0;
    sensorConfigs[i].scale = 1.0;
  }
}

void SensorManager::update() {
  // Only request OneWire temperatures if needed
  bool needOneWire = false;
  for (int i = NUM_PT100_SENSORS; i < TOTAL_SENSORS; i++) {
    if (sensorConfigs[i].enabled && !sensorConfigs[i].simulated) {
      needOneWire = true;
      break;
    }
  }
  if (needOneWire) {
    if (!dallasTemp.requestTemperatures()) {
      // Mark OneWire sensors as failed if request fails
      for (int i = NUM_PT100_SENSORS; i < TOTAL_SENSORS; i++) {
        if (sensorConfigs[i].enabled && !sensorConfigs[i].simulated) {
          readings[i].health = SENSOR_FAILED;
          readings[i].errorCode = ERROR_SENSOR_DISCONNECTED;
        }
      }
    }
  }
  
  for (int i = 0; i < TOTAL_SENSORS; i++) {
    if (!sensorConfigs[i].enabled) continue;
    
    if (sensorConfigs[i].simulated) {
      readings[i].temperature = sensorConfigs[i].simulatedValue;
      readings[i].health = SENSOR_OK;
      readings[i].errorCode = ERROR_NONE;
      readings[i].simulated = true;
    } else {
      float temp = INVALID_SENSOR_VALUE;
      if (i < NUM_PT100_SENSORS) {
        temp = readPT100(i);
      } else {
        temp = readOneWire(i - NUM_PT100_SENSORS);
      }
      
      if (temp != INVALID_SENSOR_VALUE) {
        readings[i].temperature = temp * sensorConfigs[i].scale + sensorConfigs[i].offset;
        readings[i].health = SENSOR_OK;
        readings[i].errorCode = ERROR_NONE;
      } else {
        readings[i].health = SENSOR_FAILED;
        readings[i].errorCode = ERROR_SENSOR_DISCONNECTED;
      }
      readings[i].simulated = false;
    }
    
    readings[i].lastUpdate = millis();
    updateSensorHealth(i);
  }
}

float SensorManager::readPT100(int index) {
  if (index >= NUM_PT100_SENSORS) return INVALID_SENSOR_VALUE;
  
  // Simplified PT100 reading - in real implementation use MAX31865
  digitalWrite(pt100CsPins[index], LOW);
  delayMicroseconds(10);
  
  // Per-sensor simulation with different offsets
  static unsigned long counter = 0;
  float temp = 20.0 + index * 2.0 + ((counter++ + index * 17) & 0x3F) / 10.0;
  
  digitalWrite(pt100CsPins[index], HIGH);
  return temp;
}

float SensorManager::readOneWire(int index) {
  if (index >= NUM_ONEWIRE_SENSORS) return INVALID_SENSOR_VALUE;
  
  float temp = dallasTemp.getTempC(oneWireAddresses[index]);
  if (temp == DEVICE_DISCONNECTED_C) {
    return INVALID_SENSOR_VALUE;
  }
  return temp;
}

void SensorManager::updateSensorHealth(int index) {
  if (index < 0 || index >= TOTAL_SENSORS) return;
  
  unsigned long now = millis();
  if ((unsigned long)(now - readings[index].lastUpdate) > SENSOR_TIMEOUT) {
    readings[index].health = SENSOR_FAILED;
    readings[index].errorCode = ERROR_SENSOR_TIMEOUT;
  }
}

SensorReading SensorManager::getSensorReading(int index) const {
  if (index < 0 || index >= TOTAL_SENSORS) {
    SensorReading invalid;
    invalid.temperature = INVALID_SENSOR_VALUE;
    invalid.health = SENSOR_FAILED;
    invalid.errorCode = ERROR_CONFIGURATION;
    invalid.lastUpdate = 0;
    invalid.simulated = false;
    return invalid;
  }
  return readings[index];
}

void SensorManager::setSensorConfig(int index, const SensorConfig& config) {
  if (index >= 0 && index < TOTAL_SENSORS) {
    sensorConfigs[index] = config;
  }
}

SensorConfig SensorManager::getSensorConfig(int index) const {
  if (index < 0 || index >= TOTAL_SENSORS) return SensorConfig();
  return sensorConfigs[index];
}

void SensorManager::setSimulatedValue(int index, float value) {
  if (index >= 0 && index < TOTAL_SENSORS) {
    sensorConfigs[index].simulatedValue = value;
  }
}

void SensorManager::enableSimulation(int index, bool enable) {
  if (index >= 0 && index < TOTAL_SENSORS) {
    sensorConfigs[index].simulated = enable;
  }
}