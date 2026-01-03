# JSON API Dokumentation

## Kommandoer

### getStatus
**Request:** `{"command": "getStatus"}`

**Response:**
```json
{
  "pids": [
    {
      "type": 0,
      "setpoint": 25.0,
      "output": 128,
      "enabled": true,
      "sensorIndex": 0
    }
  ],
  "sensors": [
    {
      "value": 24.5,
      "health": 0,
      "simulated": false
    }
  ],
  "alarms": [
    {
      "level": 1,
      "errorCode": 0,
      "active": true,
      "acknowledged": false,
      "timestamp": 12345
    }
  ]
}
```

### setConfig
**Request:**
```json
{
  "command": "setConfig",
  "pids": [
    {
      "type": 0,
      "setpoint": 25.0,
      "kp": 2.0,
      "ki": 1.0,
      "kd": 0.5,
      "sensorIndex": 0,
      "enabled": true
    }
  ],
  "alarms": [
    {
      "warningLow": 20.0,
      "warningHigh": 30.0,
      "alarmLow": 15.0,
      "alarmHigh": 35.0,
      "resetMode": 0,
      "enabled": true
    }
  ]
}
```

**Response:** `{"status": "ok"}`

### ackAlarm
**Request:** `{"command": "ackAlarm", "pidIndex": 0}`
**Response:** `{"status": "ok"}`

### setSimulation
**Request:**
```json
{
  "command": "setSimulation",
  "sensors": [
    {"simulated": true, "value": 25.0},
    {"simulated": false}
  ]
}
```

**Response:** `{"status": "ok"}`

### toggleEnable
**Request:** `{"command": "toggleEnable", "pidIndex": 0, "enabled": true}`
**Response:** `{"status": "ok"}`

## Fejlresponses
```json
{"error": "Invalid command"}
{"error": "Invalid pidIndex"}
{"error": "Configuration error"}
```

## Konstanter

### Controller Types
- 0: PID
- 1: Simple (on/off)
- 2: Manual

### Alarm Levels
- 0: NONE
- 1: WARNING  
- 2: ALARM
- 3: TECHNICAL

### Reset Modes
- 0: AUTO_RESET
- 1: MANUAL_ACK

### Sensor Health
- 0: OK
- 1: DEGRADED
- 2: FAILED