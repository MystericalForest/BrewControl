#ifndef SENSOR_MANAGER_H
#define SENSOR_MANAGER_H

#include "config.h"
#include <OneWire.h>
#include <DallasTemperature.h>

struct SensorReading {
  float temperature = -999;
  SensorHealth health = SENSOR_OK;
  int errorCode = ERROR_NONE;
  unsigned long lastUpdate = 0;
  bool simulated = false;
};

struct SensorConfig {
  bool enabled = true;
  bool simulated = false;
  float simulatedValue = 20.0;
  int sensorIndex = -1; // Which physical sensor to use
  float offset = 0.0;
  float scale = 1.0;
};

class SensorManager {
private:
  OneWire oneWire;
  DallasTemperature dallasTemp;
  SensorReading readings[TOTAL_SENSORS];
  SensorConfig sensorConfigs[TOTAL_SENSORS];
  DeviceAddress oneWireAddresses[NUM_ONEWIRE_SENSORS];
  int pt100CsPins[NUM_PT100_SENSORS] = {PT100_CS_1, PT100_CS_2, PT100_CS_3};
  
  float readPT100(int index);
  float readOneWire(int index);
  void updateSensorHealth(int index);

public:
  SensorManager();
  void begin();
  void update();
  
  SensorReading getSensorReading(int index) const;
  void setSensorConfig(int index, const SensorConfig& config);
  SensorConfig getSensorConfig(int index) const;
  
  // Test hooks
  void setSimulatedValue(int index, float value);
  void enableSimulation(int index, bool enable);
};

#endif