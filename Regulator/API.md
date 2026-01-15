# BrewControl JSON API Dokumentation

Dette API giver mulighed for at kommunikere med BrewControl temperaturregulator via JSON kommandoer over seriel forbindelse.

## System oversigt

**BrewControl** har 3 uafhængige termostater, hver med:
- Valgbar reguleringstype: PID, Simpel (on/off) eller Manuel
- Valgbar sensor (1-7) til temperaturmåling
- PWM output til styring af varmeelementet
- Individuel alarm konfiguration

## Termostat funktioner

### Type 0: PID Regulering
- Fuld PID kontrol med Kp, Ki, Kd parametre
- Kontinuerlig PWM output (0-255)
- Præcis temperaturkontrol

### Type 1: Simpel (On/Off)
- On/off kontrol med hysterese
- PWM output: 0% (off) eller 100% (on)
- Enkel temperaturkontrol

### Type 2: Manuel
- Direkte PWM kontrol (0-100%)
- Ingen automatisk temperaturregulering
- Manuel styring af varmeeffekt

## Generel struktur

**Alle requests** skal indeholde et `command` felt og eventuelle parametre som payload.

**Alle responses** returnerer det komplette systemstatus plus en status for den udførte kommando.

## Kommandoer

### getStatus - Hent systemstatus
Henter komplet status for alle 3 termostater, 7 sensorer og alarmer.

**Request:** 
```json
{"command": "getStatus"}
```

**Response:**
```json
{
  "command": "getStatus",
  "status": "ok",
  "timestamp": 12345678,
  "thermostats": [
    {
      "regulator_id": 0,
      "type": 0,
      "setpoint": 65.0,
      "currentTemp": 64.8,
      "output": 85,
      "enabled": true,
      "outputActive": true,
      "sensorIndex": 0,
      "state": 1,
      "kp": 2.0,
      "ki": 1.0,
      "kd": 0.5,
      "manualOutput": 0,
      "hysteresis": 1.0
    },
    {
      "regulator_id": 1,
      "type": 1,
      "setpoint": 78.0,
      "currentTemp": 77.5,
      "output": 100,
      "enabled": true,
      "outputActive": true,
      "sensorIndex": 2,
      "hysteresis": 2.0
    },
    {
      "regulator_id": 2,
      "type": 2,
      "setpoint": 0,
      "currentTemp": 22.1,
      "output": 45,
      "enabled": true,
      "outputActive": true,
      "sensorIndex": 4,
      "manualOutput": 45
    }
  ],
  "sensors": [
    {
      "sensor_id": 0,
      "temperature": 64.8,
      "health": 0,
      "errorCode": 0,
      "lastUpdate": 12345000,
      "simulated": false,
      "type": "PT100"
    },
    {
      "sensor_id": 1,
      "temperature": 23.2,
      "health": 0,
      "errorCode": 0,
      "lastUpdate": 12345000,
      "simulated": false,
      "type": "PT100"
    },
    {
      "sensor_id": 4,
      "temperature": 22.1,
      "health": 0,
      "errorCode": 0,
      "lastUpdate": 12345000,
      "simulated": false,
      "type": "OneWire"
    }
  ],
  "alarms": [
    {
      "thermostatIndex": 0,
      "level": 0,
      "errorCode": 0,
      "active": false,
      "acknowledged": true,
      "timestamp": 12345
    },
    {
      "thermostatIndex": 1,
      "level": 1,
      "errorCode": 0,
      "active": true,
      "acknowledged": false,
      "timestamp": 12350
    },
    {
      "thermostatIndex": 2,
      "level": 0,
      "errorCode": 0,
      "active": false,
      "acknowledged": true,
      "timestamp": 12345
    }
  ]
}
```

### setConfig - Opdater termostat konfiguration
Opdaterer konfiguration for en specifik termostat. Returnerer komplet systemstatus.

**Request:**
```json
{
  "command": "setConfig",
  "regulator_id": 0,
  "type": 0,
  "setpoint": 65.0,
  "kp": 2.0,
  "ki": 1.0,
  "kd": 0.5,
  "sensorIndex": 0,
  "enabled": true,
  "hysteresis": 1.0,
  "manualOutput": 0
}
```

**Response:** Komplet systemstatus med `"status": "configured"`

### ackAlarm - Kvitter alarm
Kvitterer en aktiv alarm for en specifik termostat.

**Request:** 
```json
{"command": "ackAlarm", "regulator_id": 0}
```

**Response:** Komplet systemstatus med `"status": "acknowledged"`

### setSimulation - Aktiver sensor simulering
Aktiverer eller deaktiverer simulering for sensorer.

**Request:**
```json
{
  "command": "setSimulation",
  "sensorIndex": 0,
  "simulated": true,
  "value": 25.0
}
```

**Response:** Komplet systemstatus med `"status": "simulation_set"`

### toggleEnable - Aktiver/deaktiver termostat
Aktiverer eller deaktiverer en termostat.

**Request:** 
```json
{"command": "toggleEnable", "regulator_id": 0, "enabled": true}
```

**Response:** Komplet systemstatus med `"status": "toggled"`

### autotune - Start PID autotune
Starter automatisk tuning af PID parametre. Controlleren skifter til TUNE tilstand og finder optimale Kp, Ki, Kd værdier.

**Request:**
```json
{
  "command": "autotune",
  "regulator_id": 0,
  "outputStep": 50.0,
  "noiseband": 0.5,
  "lookback": 30
}
```

**Parametre:**
- `outputStep`: Output ændring under tuning (default: 50.0)
- `noiseband`: Støjbånd for detektion (default: 0.5)
- `lookback`: Sekunder at kigge tilbage (default: 30)

**Response:** Komplet systemstatus med `"status": "autotune_started"`

### setState - Skift controller tilstand
Skifter en controllers tilstand manuelt.

**Request:**
```json
{"command": "setState", "regulator_id": 0, "state": 1}
```

**Tilstande:**
- **0: IDLE** - Inaktiv, ingen output
- **1: RUN** - Normal drift
- **2: TUNE** - Autotune mode
- **3: DEMO** - Demo mode (50% output)
- **4: FAIL** - Fejltilstand

**Response:** Komplet systemstatus med `"status": "state_changed"`

## Fejlresponses
Ved fejl returneres komplet systemstatus med fejlbesked:

```json
{
  "command": "setConfig",
  "status": "error",
  "error": "Invalid regulator_id",
  "errorCode": 2001,
  "timestamp": 12345678,
  "thermostats": [...],
  "sensors": [...],
  "alarms": [...]
}
```

## Systemkonstanter

### Controller Types (PID Type)
- **0: PID** - Fuld PID regulering med proportional, integral og differential kontrol
- **1: Simple** - Simpel on/off kontrol med hysterese
- **2: Manual** - Manuel kontrol hvor output sættes direkte

### Alarm Levels
- **0: NONE** - Ingen alarm
- **1: WARNING** - Advarselsniveau
- **2: ALARM** - Alarmniveau
- **3: TECHNICAL** - Teknisk fejl

### Reset Modes
- **0: AUTO_RESET** - Alarm nulstilles automatisk når tilstanden normaliseres
- **1: MANUAL_ACK** - Alarm kræver manuel kvittering

### Sensor Health
- **0: SENSOR_OK** - Sensor fungerer normalt
- **1: SENSOR_FAILED** - Sensor fejl
- **2: SENSOR_TIMED_OUT** - Sensor timeout

### Error Codes
- **0: ERROR_NONE** - Ingen fejl
- **1001: ERROR_SENSOR_TIMEOUT** - Sensor timeout
- **1002: ERROR_SENSOR_CRC** - Sensor CRC fejl
- **1003: ERROR_SENSOR_DISCONNECTED** - Sensor frakoblet
- **1004: ERROR_SENSOR_SHORT_CIRCUIT** - Sensor kortslutning
- **1005: ERROR_SENSOR_OPEN_CIRCUIT** - Sensor åben kreds
- **2001: ERROR_COMMUNICATION** - Kommunikationsfejl
- **2002: ERROR_CONFIGURATION** - Konfigurationsfejl

## Sensor konfiguration

### PT100 Sensorer (Index 0-3)
- **Sensor 1-4:** PT100 temperatursensorer tilsluttet via SPI
- **CS Pins:** 10, 9, 8, 6
- **Opløsning:** 12-bit
- **Område:** -50°C til +200°C

### OneWire Sensorer (Index 4-6)
- **Sensor 5-7:** DS18B20 temperatursensorer på OneWire bus
- **Pin:** 7
- **Opløsning:** 12-bit
- **Område:** -55°C til +125°C

## Eksempler

### Aktiver termostat 1 med setpunkt 65°C
```json
{"command": "toggleEnable", "regulator_id": 0, "enabled": true}
{"command": "setConfig", "regulator_id": 0, "setpoint": 65.0}
```

### Start autotune på termostat 1
```json
{"command": "autotune", "regulator_id": 0, "outputStep": 50.0, "noiseband": 0.5, "lookback": 30}
```

### Sæt termostat 2 til manuel mode med 75% effekt
```json
{"command": "setConfig", "regulator_id": 1, "type": 2, "manualOutput": 75}
```

### Simuler sensor 1 til 25°C
```json
{"command": "setSimulation", "sensorIndex": 0, "simulated": true, "value": 25.0}
```

### Kvitter alarm på termostat 3
```json
{"command": "ackAlarm", "regulator_id": 2}
```