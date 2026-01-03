#include "TemperatureController.h"

TemperatureController controller;

void setup() {
  controller.begin();
}

void loop() {
  controller.update();
}