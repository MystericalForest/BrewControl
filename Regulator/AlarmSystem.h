#ifndef ALARM_SYSTEM_H
#define ALARM_SYSTEM_H

#include "config.h"

enum AlarmLevel {
  ALARM_NONE = 0,
  ALARM_WARNING = 1,
  ALARM_ALARM = 2,
  ALARM_TECHNICAL = 3
};

enum ResetMode {
  AUTO_RESET = 0,
  MANUAL_ACK = 1
};

struct AlarmConfig {
  float warningLow = -999;
  float warningHigh = 999;
  float alarmLow = -999;
  float alarmHigh = 999;
  ResetMode resetMode = AUTO_RESET;
  bool enabled = true;
};

struct AlarmState {
  AlarmLevel level = ALARM_NONE;
  int errorCode = ERROR_NONE;
  bool acknowledged = false;
  unsigned long timestamp = 0;
  bool active = false;
};

class AlarmSystem {
private:
  AlarmConfig config[NUM_PIDS];
  AlarmState state[NUM_PIDS];
  int warningLedPins[NUM_PIDS] = {LED_WARNING_1, LED_WARNING_2, LED_WARNING_3};
  int alarmLedPins[NUM_PIDS] = {LED_ALARM_1, LED_ALARM_2, LED_ALARM_3};

public:
  void begin();
  void updateProcessAlarm(int pidIndex, float value);
  void setTechnicalAlarm(int pidIndex, int errorCode);
  void clearTechnicalAlarm(int pidIndex);
  void acknowledgeAlarm(int pidIndex);
  void updateLEDs();
  
  AlarmLevel getAlarmLevel(int pidIndex) const { return state[pidIndex].level; }
  AlarmState getAlarmState(int pidIndex) const { return state[pidIndex]; }
  void setAlarmConfig(int pidIndex, const AlarmConfig& cfg) { config[pidIndex] = cfg; }
  AlarmConfig getAlarmConfig(int pidIndex) const { return config[pidIndex]; }
  
  bool isOutputEnabled(int pidIndex) const;
};

#endif