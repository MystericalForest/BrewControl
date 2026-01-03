# Eksempel JSON kommandoer til temperaturcontroller

## Hent status
{"command": "getStatus"}

## Konfigurer PID controller
{
  "command": "setConfig",
  "pids": [
    {
      "type": 0,
      "setpoint": 25.0,
      "kp": 2.0,
      "ki": 5.0,
      "kd": 1.0,
      "sensorIndex": 0,
      "enabled": true
    },
    {
      "type": 1,
      "setpoint": 30.0,
      "sensorIndex": 3,
      "enabled": true
    },
    {
      "type": 2,
      "manualOutput": 128,
      "sensorIndex": 4,
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
    },
    {
      "warningLow": 25.0,
      "warningHigh": 35.0,
      "alarmLow": 20.0,
      "alarmHigh": 40.0,
      "resetMode": 1,
      "enabled": true
    },
    {
      "warningLow": 18.0,
      "warningHigh": 28.0,
      "alarmLow": 10.0,
      "alarmHigh": 35.0,
      "resetMode": 0,
      "enabled": true
    }
  ]
}

## Kvittér alarm
{"command": "ackAlarm", "pidIndex": 0}

## Aktivér simulering
{
  "command": "setSimulation",
  "sensors": [
    {"simulated": true, "value": 22.5},
    {"simulated": true, "value": 28.0},
    {"simulated": false}
  ]
}

## Enable/disable regulator
{"command": "toggleEnable", "pidIndex": 0, "enabled": true}
{"command": "toggleEnable", "pidIndex": 1} // Toggle current state

# Alarm konfiguration pr. regulator:
# Regulator 0: Strenge grænser (20-30°C warning, 15-35°C alarm)
# Regulator 1: Løsere grænser (25-35°C warning, 20-40°C alarm) med manuel kvittering
# Regulator 2: Brede grænser (18-28°C warning, 10-35°C alarm)

# Sensor indeks (0-4):
# 0-2: PT100 sensorer
# 3-4: OneWire sensorer

# Controller typer:
# 0 = PID
# 1 = Simple (on/off)
# 2 = Manual

# Alarm reset modes:
# 0 = AUTO_RESET
# 1 = MANUAL_ACK

# Alarm niveauer:
# 0 = NONE
# 1 = WARNING
# 2 = ALARM
# 3 = TECHNICAL

# Sensor health:
# 0 = OK
# 1 = DEGRADED
# 2 = FAILED