#include "PIDController.h"
#include <Arduino.h>

PIDController::PIDController() {
  for (int i = 0; i < NUM_PIDS; i++) {
    pidInput[i] = 0;
    pidOutput[i] = 0;
    pidSetpoint[i] = 20.0;
    pid[i] = new PID(&pidInput[i], &pidOutput[i], &pidSetpoint[i], 2.0, 5.0, 1.0, DIRECT);
  }
}

PIDController::~PIDController() {
  for (int i = 0; i < NUM_PIDS; i++) {
    delete pid[i];
    pid[i] = nullptr;
  }
}

void PIDController::begin() {
  for (int i = 0; i < NUM_PIDS; i++) {
    if (outputPins[i] >= 0 && outputPins[i] <= 53) { // Valid Arduino Mega pins
      pinMode(outputPins[i], OUTPUT);
      analogWrite(outputPins[i], 0);
    }
    
    if (pid[i]) {
      pid[i]->SetMode(AUTOMATIC);
      pid[i]->SetOutputLimits(0, 255);
      pid[i]->SetSampleTime(UPDATE_INTERVAL);
    }
  }
}

void PIDController::update(int pidIndex, double sensorValue, bool outputEnabled) {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS) return;
  
  status[pidIndex].input = sensorValue;
  status[pidIndex].setpoint = config[pidIndex].setpoint;
  status[pidIndex].enabled = config[pidIndex].enabled;
  status[pidIndex].type = config[pidIndex].type;
  status[pidIndex].outputActive = outputEnabled && config[pidIndex].enabled;
  
  if (!status[pidIndex].outputActive) {
    status[pidIndex].output = 0;
    if (outputPins[pidIndex] >= 0 && outputPins[pidIndex] <= 53) {
      analogWrite(outputPins[pidIndex], 0);
    }
    return;
  }
  
  double output = 0;
  
  switch (config[pidIndex].type) {
    case CONTROLLER_PID:
      pidInput[pidIndex] = sensorValue;
      pidSetpoint[pidIndex] = config[pidIndex].setpoint;
      if (pid[pidIndex]) {
        pid[pidIndex]->Compute();
        output = pidOutput[pidIndex];
      }
      break;
      
    case CONTROLLER_SIMPLE:
      {
        double error = config[pidIndex].setpoint - sensorValue;
        if (!simpleControllerState[pidIndex] && error > config[pidIndex].hysteresis) {
          simpleControllerState[pidIndex] = true;
        } else if (simpleControllerState[pidIndex] && error < -config[pidIndex].hysteresis) {
          simpleControllerState[pidIndex] = false;
        }
        output = simpleControllerState[pidIndex] ? config[pidIndex].outputMax : 0;
      }
      break;
      
    case CONTROLLER_MANUAL:
      output = config[pidIndex].manualOutput;
      break;
      
    default:
      output = 0; // Safe default for unknown controller type
      break;
  }
  
  // Apply output limits
  output = constrain(output, config[pidIndex].outputMin, config[pidIndex].outputMax);
  status[pidIndex].output = output;
  
  // Convert to PWM (0-255)
  int pwmValue = 0;
  if (config[pidIndex].outputMax > 0) {
    pwmValue = map(output, 0, config[pidIndex].outputMax, 0, 255);
  }
  if (outputPins[pidIndex] >= 0 && outputPins[pidIndex] <= 53) {
    analogWrite(outputPins[pidIndex], pwmValue);
  }
}

void PIDController::setPIDConfig(int pidIndex, const PIDConfig& cfg) {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS) return;
  
  // Validate PID parameters
  if (cfg.kp < 0 || cfg.ki < 0 || cfg.kd < 0) return;
  if (cfg.outputMax <= cfg.outputMin) return;
  
  config[pidIndex] = cfg;
  
  // Update PID parameters
  if (pid[pidIndex]) {
    pid[pidIndex]->SetTunings(cfg.kp, cfg.ki, cfg.kd);
    pid[pidIndex]->SetOutputLimits(cfg.outputMin, cfg.outputMax);
  }
  pidSetpoint[pidIndex] = cfg.setpoint;
}

PIDConfig PIDController::getPIDConfig(int pidIndex) const {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS) return PIDConfig();
  return config[pidIndex];
}

PIDStatus PIDController::getPIDStatus(int pidIndex) const {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS) return PIDStatus();
  return status[pidIndex];
}

void PIDController::setOutput(int pidIndex, double value) {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS) return;
  config[pidIndex].manualOutput = constrain(value, config[pidIndex].outputMin, config[pidIndex].outputMax);
}

void PIDController::enableOutput(int pidIndex, bool enable) {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS) return;
  config[pidIndex].enabled = enable;
}