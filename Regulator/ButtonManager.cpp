#include "ButtonManager.h"
#include <Arduino.h>

void ButtonManager::begin() {
  for (int i = 0; i < NUM_PIDS; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);
    pinMode(enabledLedPins[i], OUTPUT);
    pinMode(disabledLedPins[i], OUTPUT);
    
    // Default disabled state
    digitalWrite(enabledLedPins[i], LOW);
    digitalWrite(disabledLedPins[i], HIGH);
  }
}

void ButtonManager::update() {
  for (int i = 0; i < NUM_PIDS; i++) {
    bool reading = !digitalRead(buttonPins[i]); // Inverted due to pullup
    
    if (reading != lastButtonState[i]) {
      lastDebounceTime[i] = millis();
    }
    
    if ((unsigned long)(millis() - lastDebounceTime[i]) > DEBOUNCE_DELAY) {
      if (reading != buttonState[i]) {
        buttonState[i] = reading;
        
        if (buttonState[i]) { // Button pressed
          pidEnabled[i] = !pidEnabled[i]; // Toggle state
        }
      }
    }
    
    lastButtonState[i] = reading;
  }
  
  updateLEDs();
}

bool ButtonManager::isPIDEnabled(int pidIndex) const {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS) return false;
  return pidEnabled[pidIndex];
}

void ButtonManager::setPIDEnabled(int pidIndex, bool enabled) {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS) return;
  pidEnabled[pidIndex] = enabled;
  updateLEDs();
}

void ButtonManager::updateLEDs() {
  for (int i = 0; i < NUM_PIDS; i++) {
    digitalWrite(enabledLedPins[i], pidEnabled[i] ? HIGH : LOW);
    digitalWrite(disabledLedPins[i], pidEnabled[i] ? LOW : HIGH);
  }
}