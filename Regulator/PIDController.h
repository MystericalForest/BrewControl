#ifndef PID_CONTROLLER_H
#define PID_CONTROLLER_H

#include "config.h"
#include <PID_v1.h>
#include <pid-autotune.h>

class PID_ATune;

enum ControllerType {
  CONTROLLER_PID = 0,
  CONTROLLER_SIMPLE = 1,
  CONTROLLER_MANUAL = 2
};

enum ControllerState {
  STATE_IDLE = 0,
  STATE_RUN = 1,
  STATE_TUNE = 2,
  STATE_DEMO = 3,
  STATE_FAIL = 4
};

struct PIDConfig {
  ControllerType type = CONTROLLER_PID;
  double kp = 2.0;
  double ki = 5.0;
  double kd = 1.0;
  double setpoint = 20.0;
  double outputMin = 0.0;
  double outputMax = 255.0;
  int sensorIndex = -1;
  bool enabled = false;
  double manualOutput = 0.0;
  double hysteresis = 0.5; // For simple controller
};

struct PIDStatus {
  int sensorIndex;
  double input = 0.0;
  double output = 0.0;
  double setpoint = 0.0;
  bool enabled = false;
  ControllerType type = CONTROLLER_PID;
  bool outputActive = false;
  ControllerState state = STATE_IDLE;
};

class PIDController {
private:
  PID* pid[NUM_PIDS];
  PID_ATune* autotuner[NUM_PIDS];
  PIDConfig config[NUM_PIDS];
  PIDStatus status[NUM_PIDS];
  double pidInput[NUM_PIDS];
  double pidOutput[NUM_PIDS];
  double pidSetpoint[NUM_PIDS];
  int outputPins[NUM_PIDS] = {PWM_OUTPUT_1, PWM_OUTPUT_2, PWM_OUTPUT_3};
  bool simpleControllerState[NUM_PIDS] = {false, false, false};
  ControllerState state[NUM_PIDS] = {STATE_IDLE, STATE_IDLE, STATE_IDLE};
  
  void updateStateMachine(int pidIndex);

public:
  PIDController();
  ~PIDController();
  void begin();
  void update(int pidIndex, double sensorValue, bool outputEnabled);
  
  void setPIDConfig(int pidIndex, const PIDConfig& cfg);
  PIDConfig getPIDConfig(int pidIndex) const;
  PIDStatus getPIDStatus(int pidIndex) const;
  
  void setOutput(int pidIndex, double value);
  void enableOutput(int pidIndex, bool enable);
  
  void setState(int pidIndex, ControllerState newState);
  ControllerState getState(int pidIndex) const;
  void startAutotune(int pidIndex, double outputStep, double noiseband, int lookback);
  void cancelAutotune(int pidIndex);
};

#endif