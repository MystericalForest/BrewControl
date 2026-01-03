#ifndef TEMPERATURE_CONTROLLER_H
#define TEMPERATURE_CONTROLLER_H

#include "config.h"
#include "AlarmSystem.h"
#include "SensorManager.h"
#include "PIDController.h"
#include "JSONHandler.h"
#include "ButtonManager.h"

class TemperatureController {
private:
  AlarmSystem alarmSystem;
  SensorManager sensorManager;
  PIDController pidController;
  ButtonManager buttonManager;
  JSONHandler jsonHandler;
  
  unsigned long lastUpdate = 0;

public:
  TemperatureController();
  void begin();
  void update();
  
private:
  void updateSystem();
  void processSerialInput();
};

#endif