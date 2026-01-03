#include "AlarmSystem.h"
#include <Arduino.h>

void AlarmSystem::begin() {
  for (int i = 0; i < NUM_PIDS; i++) {
    pinMode(warningLedPins[i], OUTPUT);
    pinMode(alarmLedPins[i], OUTPUT);
    digitalWrite(warningLedPins[i], LOW);
    digitalWrite(alarmLedPins[i], LOW);
  }
}

void AlarmSystem::updateProcessAlarm(int pidIndex, float value) {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS || !config[pidIndex].enabled) return;
  
  AlarmLevel newLevel = ALARM_NONE;
  int errorCode = ERROR_NONE;
  
  if (value <= config[pidIndex].alarmLow || value >= config[pidIndex].alarmHigh) {
    newLevel = ALARM_ALARM;
    errorCode = ERROR_NONE; // Process alarm, not technical
  } else if (value <= config[pidIndex].warningLow || value >= config[pidIndex].warningHigh) {
    newLevel = ALARM_WARNING;
  }
  
  // Handle alarm state changes
  if (newLevel > state[pidIndex].level) {
    state[pidIndex].level = newLevel;
    state[pidIndex].errorCode = errorCode;
    state[pidIndex].timestamp = millis();
    state[pidIndex].active = true;
    state[pidIndex].acknowledged = false;
  } else if (newLevel < state[pidIndex].level && config[pidIndex].resetMode == AUTO_RESET) {
    state[pidIndex].level = newLevel;
    state[pidIndex].active = (newLevel != ALARM_NONE);
  }
}

void AlarmSystem::setTechnicalAlarm(int pidIndex, int errorCode) {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS) return;
  
  state[pidIndex].level = ALARM_TECHNICAL;
  state[pidIndex].errorCode = errorCode;
  state[pidIndex].timestamp = millis();
  state[pidIndex].active = true;
  state[pidIndex].acknowledged = false;
}

void AlarmSystem::clearTechnicalAlarm(int pidIndex) {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS) return;
  
  if (state[pidIndex].level == ALARM_TECHNICAL) {
    state[pidIndex].active = false;
    if (config[pidIndex].resetMode == AUTO_RESET) {
      state[pidIndex].level = ALARM_NONE;
      state[pidIndex].errorCode = ERROR_NONE;
    }
  }
}

void AlarmSystem::acknowledgeAlarm(int pidIndex) {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS) return;
  
  state[pidIndex].acknowledged = true;
  if (config[pidIndex].resetMode == MANUAL_ACK && !state[pidIndex].active) {
    state[pidIndex].level = ALARM_NONE;
    state[pidIndex].errorCode = ERROR_NONE;
  }
}

void AlarmSystem::updateLEDs() {
  for (int i = 0; i < NUM_PIDS; i++) {
    bool warningLed = false;
    bool alarmLed = false;
    
    if (state[i].active && !state[i].acknowledged) {
      if (state[i].level == ALARM_WARNING) {
        warningLed = true;
      } else if (state[i].level >= ALARM_ALARM) {
        alarmLed = true;
      }
    }
    
    if (warningLedPins[i] >= 0 && warningLedPins[i] <= 53) {
      digitalWrite(warningLedPins[i], warningLed ? HIGH : LOW);
    }
    if (alarmLedPins[i] >= 0 && alarmLedPins[i] <= 53) {
      digitalWrite(alarmLedPins[i], alarmLed ? HIGH : LOW);
    }
  }
}

bool AlarmSystem::isOutputEnabled(int pidIndex) const {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS) return false;
  return state[pidIndex].level <= ALARM_WARNING;
}