# Testplan - Arduino Temperaturcontroller

## 1. Hardware Setup Test

### 1.1 Pin Connectivity Test
- [ ] Verificer alle PWM outputs (pin 2, 3, 5)
- [ ] Test alle LED'er (warning: 22,24,26 | alarm: 23,25,27 | enabled: 28,29,30 | disabled: 31,32,33)
- [ ] Test trykknapper (pin 34, 35, 36) med pullup
- [ ] Verificer PT100 CS pins (8, 9, 10)
- [ ] Test OneWire pin (7)

### 1.2 Power-on Test
- [ ] Alle outputs OFF ved opstart (fail-safe)
- [ ] Alle disabled LED'er ON ved opstart
- [ ] Serial kommunikation etableret (115200 baud)

## 2. Sensor Tests

### 2.1 PT100 Sensorer
```json
{"command": "setSimulation", "sensors": [
  {"simulated": true, "value": 25.0},
  {"simulated": true, "value": 30.0}, 
  {"simulated": true, "value": 35.0}
]}
```
- [ ] Læs simulerede værdier korrekt
- [ ] Test sensor timeout (fjern sensor)
- [ ] Test CRC fejl simulation

### 2.2 OneWire Sensorer
```json
{"command": "setSimulation", "sensors": [
  {"simulated": false}, {"simulated": false}, {"simulated": false},
  {"simulated": true, "value": 22.0},
  {"simulated": true, "value": 28.0}
]}
```
- [ ] Læs fysiske DS18B20 sensorer
- [ ] Test sensor disconnect alarm
- [ ] Verificer sensor health status

## 3. PID Controller Tests

### 3.1 PID Mode Test
```json
{
  "command": "setConfig",
  "pids": [{
    "type": 0,
    "setpoint": 25.0,
    "kp": 2.0, "ki": 1.0, "kd": 0.5,
    "sensorIndex": 0,
    "enabled": true
  }]
}
```
- [ ] Verificer PID beregning
- [ ] Test setpoint ændring
- [ ] Test parameter tuning

### 3.2 Simple Controller Test
```json
{
  "command": "setConfig", 
  "pids": [{
    "type": 1,
    "setpoint": 30.0,
    "sensorIndex": 1,
    "enabled": true
  }]
}
```
- [ ] Test on/off funktionalitet
- [ ] Verificer hysterese

### 3.3 Manual Mode Test
```json
{
  "command": "setConfig",
  "pids": [{
    "type": 2,
    "manualOutput": 128,
    "enabled": true
  }]
}
```
- [ ] Test manuel output kontrol
- [ ] Verificer PWM output

## 4. Alarm System Tests

### 4.1 Process Alarmer
```json
{
  "command": "setConfig",
  "alarms": [{
    "warningLow": 20.0, "warningHigh": 30.0,
    "alarmLow": 15.0, "alarmHigh": 35.0,
    "resetMode": 0, "enabled": true
  }]
}
```
- [ ] Test warning grænser (gul LED)
- [ ] Test alarm grænser (rød LED, output OFF)
- [ ] Test auto-reset funktionalitet

### 4.2 Manual Acknowledge Test
```json
{
  "command": "setConfig",
  "alarms": [{"resetMode": 1, "enabled": true}]
}
```
- [ ] Trigger alarm
- [ ] Verificer latchende alarm
- [ ] Test acknowledge kommando: `{"command": "ackAlarm", "pidIndex": 0}`

### 4.3 Technical Alarmer
- [ ] Test sensor timeout alarm
- [ ] Test sensor disconnect alarm
- [ ] Test konfigurationsfejl alarm

## 5. Button & LED Tests

### 5.1 Physical Button Test
- [ ] Tryk knap 1 - toggle regulator 0
- [ ] Verificer LED skift (grøn/rød)
- [ ] Test debouncing (hurtige tryk)

### 5.2 JSON Enable/Disable Test
```json
{"command": "toggleEnable", "pidIndex": 0, "enabled": true}
{"command": "toggleEnable", "pidIndex": 1}
```
- [ ] Test enable via JSON
- [ ] Test toggle via JSON
- [ ] Verificer LED opdatering

## 6. Safety & Robustness Tests

### 6.1 Fail-Safe Tests
- [ ] Output OFF ved alarm
- [ ] Output OFF ved sensor fejl
- [ ] Output OFF ved disabled regulator
- [ ] Korrekt opførsel ved power-on

### 6.2 Input Validation Tests
```json
{"command": "setConfig", "pids": [{"type": 99, "kp": -1.0}]}
{"command": "ackAlarm", "pidIndex": 99}
{"command": "toggleEnable", "pidIndex": -1}
```
- [ ] Test invalid controller type
- [ ] Test negative PID parametre
- [ ] Test out-of-bounds pidIndex
- [ ] Test malformed JSON

### 6.3 Edge Case Tests
- [ ] Test millis() overflow (simuler)
- [ ] Test buffer overflow (lang kommando)
- [ ] Test memory allocation fejl
- [ ] Test concurrent sensor læsning

## 7. Integration Tests

### 7.1 Multi-Regulator Test
```json
{
  "command": "setConfig",
  "pids": [
    {"type": 0, "setpoint": 25.0, "sensorIndex": 0, "enabled": true},
    {"type": 1, "setpoint": 30.0, "sensorIndex": 3, "enabled": true}, 
    {"type": 2, "manualOutput": 100, "enabled": true}
  ],
  "alarms": [
    {"warningLow": 20.0, "warningHigh": 30.0, "resetMode": 0},
    {"warningLow": 25.0, "warningHigh": 35.0, "resetMode": 1},
    {"warningLow": 18.0, "warningHigh": 28.0, "resetMode": 0}
  ]
}
```
- [ ] Alle 3 regulatorer aktive samtidig
- [ ] Forskellige alarmgrænser pr. regulator
- [ ] Uafhængige enable/disable states

### 7.2 Stress Test
- [ ] Kontinuerlig drift i 24 timer
- [ ] Hyppige JSON kommandoer (1/sek)
- [ ] Simuler sensor ustabilitet
- [ ] Test memory leaks

## 8. Performance Tests

### 8.1 Timing Tests
- [ ] Mål update cycle tid (<1000ms)
- [ ] Mål JSON response tid
- [ ] Verificer sensor læsning frekvens

### 8.2 Memory Tests
- [ ] Mål RAM forbrug
- [ ] Test JSON buffer limits
- [ ] Verificer stack usage

## 9. Acceptance Criteria

### Funktionalitet
- [ ] Alle 3 regulatorer fungerer uafhængigt
- [ ] Sensor-til-regulator mapping fleksibelt
- [ ] Alarm system følger PLC-filosofi
- [ ] JSON kommunikation stabil

### Sikkerhed
- [ ] Fail-safe ved alle fejlsituationer
- [ ] Input validering på alle parametre
- [ ] Robust error handling
- [ ] Ingen buffer overflows

### Pålidelighed
- [ ] Stabil drift >24 timer
- [ ] Korrekt håndtering af edge cases
- [ ] Deterministisk opførsel
- [ ] Ingen memory leaks

## Test Kommandoer

### Quick Status Check
```json
{"command": "getStatus"}
```

### Full System Test
```json
{
  "command": "setConfig",
  "pids": [
    {"type": 0, "setpoint": 25.0, "kp": 2.0, "ki": 1.0, "kd": 0.5, "sensorIndex": 0, "enabled": true},
    {"type": 1, "setpoint": 30.0, "sensorIndex": 3, "enabled": true},
    {"type": 2, "manualOutput": 128, "enabled": true}
  ],
  "alarms": [
    {"warningLow": 20.0, "warningHigh": 30.0, "alarmLow": 15.0, "alarmHigh": 35.0, "resetMode": 0, "enabled": true},
    {"warningLow": 25.0, "warningHigh": 35.0, "alarmLow": 20.0, "alarmHigh": 40.0, "resetMode": 1, "enabled": true},
    {"warningLow": 18.0, "warningHigh": 28.0, "alarmLow": 10.0, "alarmHigh": 35.0, "resetMode": 0, "enabled": true}
  ]
}
```