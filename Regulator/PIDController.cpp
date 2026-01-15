#include "PIDController.h"
#include <Arduino.h>

PIDController::PIDController() {
  for (int i = 0; i < NUM_PIDS; i++) {
    pidInput[i] = 0;
    pidOutput[i] = 0;
    pidSetpoint[i] = 20.0;
    pid[i] = new PID(&pidInput[i], &pidOutput[i], &pidSetpoint[i], 2.0, 5.0, 1.0, DIRECT);
    state[i] = STATE_IDLE;
    tuneCycles[i] = 0;
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
  status[pidIndex].state = state[pidIndex];
  status[pidIndex].outputActive = outputEnabled && config[pidIndex].enabled;
  
  updateStateMachine(pidIndex);
  
  if (!status[pidIndex].outputActive && state[pidIndex] != STATE_TUNE) {
    status[pidIndex].output = 0;
    if (outputPins[pidIndex] >= 0 && outputPins[pidIndex] <= 53) {
      analogWrite(outputPins[pidIndex], 0);
    }
    return;
  }
  
  double output = 0;
  
  if (state[pidIndex] == STATE_TUNE) {
    updateAutotune(pidIndex, sensorValue);
    output = tuneOutput[pidIndex];
  } else if (state[pidIndex] == STATE_RUN) {
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
    }
  } else if (state[pidIndex] == STATE_DEMO) {
    output = config[pidIndex].outputMax * 0.5;
  }
  
  output = constrain(output, config[pidIndex].outputMin, config[pidIndex].outputMax);
  status[pidIndex].output = output;
  
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

void PIDController::updateStateMachine(int pidIndex) {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS) return;
  
  if (!config[pidIndex].enabled && state[pidIndex] != STATE_IDLE) {
    state[pidIndex] = STATE_IDLE;
  }
}

void PIDController::setState(int pidIndex, ControllerState newState) {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS) return;
  state[pidIndex] = newState;
  status[pidIndex].state = newState;
}

ControllerState PIDController::getState(int pidIndex) const {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS) return STATE_IDLE;
  return state[pidIndex];
}

void PIDController::startAutotune(int pidIndex, double outputStep, double noiseband, int lookback) {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS) return;
  
  tuneOutputStep[pidIndex] = outputStep;
  tuneOutput[pidIndex] = outputStep;
  tuneStartTime[pidIndex] = millis();
  tunePeakHigh[pidIndex] = config[pidIndex].setpoint;
  tunePeakLow[pidIndex] = config[pidIndex].setpoint;
  tuneCycles[pidIndex] = 0;
  
  state[pidIndex] = STATE_TUNE;
  status[pidIndex].state = STATE_TUNE;
}

void PIDController::cancelAutotune(int pidIndex) {
  if (pidIndex < 0 || pidIndex >= NUM_PIDS) return;
  state[pidIndex] = STATE_IDLE;
  status[pidIndex].state = STATE_IDLE;
}

void PIDController::updateAutotune(int pidIndex, double sensorValue) {
  if (sensorValue > config[pidIndex].setpoint) {
    tuneOutput[pidIndex] = 0;
    if (sensorValue > tunePeakHigh[pidIndex]) tunePeakHigh[pidIndex] = sensorValue;
  } else {
    tuneOutput[pidIndex] = tuneOutputStep[pidIndex];
    if (sensorValue < tunePeakLow[pidIndex]) tunePeakLow[pidIndex] = sensorValue;
  }
  
  if (millis() - tuneStartTime[pidIndex] > 1800000) {
    double amplitude = (tunePeakHigh[pidIndex] - tunePeakLow[pidIndex]) / 2.0;
    double Ku = 4.0 * tuneOutputStep[pidIndex] / (3.14159 * amplitude);
    double Pu = 1800.0;
    
    config[pidIndex].kp = 0.6 * Ku;
    config[pidIndex].ki = 1.2 * Ku / Pu;
    config[pidIndex].kd = 0.075 * Ku * Pu;
    
    if (pid[pidIndex]) {
      pid[pidIndex]->SetTunings(config[pidIndex].kp, config[pidIndex].ki, config[pidIndex].kd);
    }
    
    state[pidIndex] = STATE_RUN;
    status[pidIndex].state = STATE_RUN;
  }
}