# Arduino Mega Temperaturcontroller

Industri-inspireret temperaturcontroller med 3 PID-regulatorer, 5 temperatursensorer og komplet alarmsystem.

## Hardware Krav

- Arduino Mega 2560
- 3 × PT100 sensorer med MAX31865 amplifier
- 2 × DS18B20 OneWire sensorer
- 3 × PWM-styrede relæer
- 6 × LED'er (3 gule warning, 3 røde alarm)
- 6 × LED'er (3 grønne enabled, 3 røde disabled)
- 3 × Trykknapper (enable/disable)

## Biblioteker

Installer følgende biblioteker via Arduino IDE Library Manager:
- ArduinoJson (v6.x)
- PID (v1.2.x)
- OneWire
- DallasTemperature

## Pin Konfiguration

Se `regulator/config.h` for komplet pin-mapping.

## Funktioner

### 3 Uafhængige Regulatorer
- **PID**: Fuld PID-regulering med konfigurerbare parametre
- **Simple**: On/off regulering med hysterese
- **Manual**: Manuel procentuel styring
- Hver regulator kan konfigureres til at bruge en hvilken som helst af de 5 sensorer

### 5 Temperatursensorer
- 3 × PT100 (høj præcision)
- 2 × DS18B20 OneWire
- Simulerede sensorer til test

### Alarmsystem
- 4 alarmniveauer: none/warning/alarm/technical
- Konfigurerbare grænser pr. regulator (uafhængige)
- Auto-reset eller manuel kvittering pr. regulator
- LED-indikation
- Fail-safe: outputs OFF ved alarm

### JSON Kommunikation
Alle kommandoer via Serial (115200 baud):

```json
{"command": "getStatus"}
{"command": "setConfig", "pids": [...], "alarms": [...]}
{"command": "ackAlarm", "pidIndex": 0}
{"command": "setSimulation", "sensors": [...]}
{"command": "toggleEnable", "pidIndex": 0, "enabled": true}
```

## Fejlkoder

- 1001: Sensor timeout
- 1002: CRC fejl
- 1003: Sensor frakoblet
- 1004: Kortslutning
- 1005: Åben kreds
- 2001: Kommunikationsfejl
- 2002: Konfigurationsfejl

## Eksempler

Se `examples.md` for JSON kommando eksempler.

## Arkitektur

```
regulator.ino (minimal)
├── TemperatureController (hovedklasse)
├── AlarmSystem (alarm håndtering)
├── SensorManager (sensor læsning)
├── PIDController (regulering)
├── JSONHandler (kommunikation)
└── config.h (konstanter)
```

## Sikkerhed

- Fail-safe defaults (outputs OFF)
- Timeout overvågning
- Sensor health monitoring
- Alarm-baseret output disable