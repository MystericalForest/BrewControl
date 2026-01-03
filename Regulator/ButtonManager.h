#ifndef BUTTON_MANAGER_H
#define BUTTON_MANAGER_H

#include "config.h"

class ButtonManager {
private:
  int buttonPins[NUM_PIDS] = {BUTTON_1, BUTTON_2, BUTTON_3};
  int enabledLedPins[NUM_PIDS] = {LED_ENABLED_1, LED_ENABLED_2, LED_ENABLED_3};
  int disabledLedPins[NUM_PIDS] = {LED_DISABLED_1, LED_DISABLED_2, LED_DISABLED_3};
  
  bool buttonState[NUM_PIDS] = {false, false, false};
  bool lastButtonState[NUM_PIDS] = {false, false, false};
  unsigned long lastDebounceTime[NUM_PIDS] = {0, 0, 0};
  bool pidEnabled[NUM_PIDS] = {false, false, false};
  
  static const unsigned long DEBOUNCE_DELAY = 50;

public:
  void begin();
  void update();
  bool isPIDEnabled(int pidIndex) const;
  void setPIDEnabled(int pidIndex, bool enabled);
  void updateLEDs();
};

#endif