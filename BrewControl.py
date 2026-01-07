import sys
import json
import serial
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QSpinBox, 
                             QDoubleSpinBox, QComboBox, QGroupBox, QGridLayout,
                             QTextEdit, QTabWidget, QCheckBox, QMessageBox)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont

class SerialThread(QThread):
    data_received = pyqtSignal(dict)
    
    def __init__(self, port='COM3', baudrate=115200):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.running = False
    
    def run(self):
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
            
            while self.running:
                if self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode().strip()
                    if line:
                        try:
                            data = json.loads(line)
                            self.data_received.emit(data)
                        except json.JSONDecodeError:
                            pass
                time.sleep(0.1)
        except Exception as e:
            print(f"Serial error: {e}")
    
    def send_command(self, command):
        if self.serial_conn and self.serial_conn.is_open:
            try:
                json_str = json.dumps(command) + '\n'
                self.serial_conn.write(json_str.encode())
            except Exception as e:
                print(f"Send error: {e}")
    
    def stop(self):
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()

class ThermostatWidget(QWidget):
    def __init__(self, regulator_id, parent=None):
        super().__init__(parent)
        self.regulator_id = regulator_id
        self.parent_app = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Status display
        self.status_label = QLabel(f"Termostat {self.regulator_id + 1}: Deaktiveret")
        self.status_label.setFont(QFont('Arial', 12, QFont.Bold))
        layout.addWidget(self.status_label)
        
        # Controls
        controls = QGridLayout()
        
        # Type selector
        controls.addWidget(QLabel("Type:"), 0, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["PID", "Simple", "Manual"])
        controls.addWidget(self.type_combo, 0, 1)
        
        # Setpoint
        controls.addWidget(QLabel("Sætpunkt:"), 1, 0)
        self.setpoint_spin = QDoubleSpinBox()
        self.setpoint_spin.setRange(-50, 150)
        self.setpoint_spin.setSuffix("°C")
        controls.addWidget(self.setpoint_spin, 1, 1)
        
        # Sensor selector
        controls.addWidget(QLabel("Sensor:"), 2, 0)
        self.sensor_combo = QComboBox()
        self.sensor_combo.addItems([f"Sensor {i+1}" for i in range(7)])
        controls.addWidget(self.sensor_combo, 2, 1)
        
        # PID parameters
        controls.addWidget(QLabel("Kp:"), 3, 0)
        self.kp_spin = QDoubleSpinBox()
        self.kp_spin.setRange(0, 100)
        self.kp_spin.setDecimals(2)
        controls.addWidget(self.kp_spin, 3, 1)
        
        controls.addWidget(QLabel("Ki:"), 4, 0)
        self.ki_spin = QDoubleSpinBox()
        self.ki_spin.setRange(0, 100)
        self.ki_spin.setDecimals(2)
        controls.addWidget(self.ki_spin, 4, 1)
        
        controls.addWidget(QLabel("Kd:"), 5, 0)
        self.kd_spin = QDoubleSpinBox()
        self.kd_spin.setRange(0, 100)
        self.kd_spin.setDecimals(2)
        controls.addWidget(self.kd_spin, 5, 1)
        
        # Hysteresis for Simple mode
        controls.addWidget(QLabel("Hysterese:"), 6, 0)
        self.hysteresis_spin = QDoubleSpinBox()
        self.hysteresis_spin.setRange(0.1, 10.0)
        self.hysteresis_spin.setDecimals(1)
        self.hysteresis_spin.setSuffix("°C")
        self.hysteresis_spin.setValue(1.0)
        controls.addWidget(self.hysteresis_spin, 6, 1)
        
        # Manual output for Manual mode
        controls.addWidget(QLabel("Manuel output:"), 7, 0)
        self.manual_output_spin = QSpinBox()
        self.manual_output_spin.setRange(0, 100)
        self.manual_output_spin.setSuffix("%")
        controls.addWidget(self.manual_output_spin, 7, 1)
        
        # Enable/Disable button
        self.enable_btn = QPushButton("Aktiver")
        self.enable_btn.clicked.connect(self.toggle_enable)
        controls.addWidget(self.enable_btn, 8, 0, 1, 2)
        
        layout.addLayout(controls)
        self.setLayout(layout)
        
        # Connect type change to update UI
        self.type_combo.currentIndexChanged.connect(self.update_controls_visibility)
        self.update_controls_visibility()
    
    def update_controls_visibility(self):
        """Show/hide controls based on thermostat type"""
        thermostat_type = self.type_combo.currentIndex()
        
        # PID controls (only for PID type)
        pid_visible = thermostat_type == 0
        self.kp_spin.setVisible(pid_visible)
        self.ki_spin.setVisible(pid_visible)
        self.kd_spin.setVisible(pid_visible)
        
        # Hysteresis (only for Simple type)
        hysteresis_visible = thermostat_type == 1
        self.hysteresis_spin.setVisible(hysteresis_visible)
        
        # Manual output (only for Manual type)
        manual_visible = thermostat_type == 2
        self.manual_output_spin.setVisible(manual_visible)
        
        # Setpoint (not for Manual type)
        setpoint_visible = thermostat_type != 2
        self.setpoint_spin.setVisible(setpoint_visible)
    
    def toggle_enable(self):
        if self.parent_app:
            enabled = self.enable_btn.text() == "Aktiver"
            self.parent_app.toggle_thermostat(self.regulator_id, enabled)
    
    def update_display(self, thermostat_data, sensor_data):
        enabled = thermostat_data.get('enabled', False)
        setpoint = thermostat_data.get('setpoint', 0)
        output = thermostat_data.get('output', 0)
        current_temp = thermostat_data.get('currentTemp', 0)
        sensor_idx = thermostat_data.get('sensorIndex', 0)
        thermostat_type = thermostat_data.get('type', 0)
        
        # Find sensor data by sensor_id
        sensor_temp = current_temp
        sensor_health = 0
        for sensor in sensor_data:
            if sensor.get('sensor_id') == sensor_idx:
                sensor_temp = sensor.get('temperature', current_temp)
                sensor_health = sensor.get('health', 0)
                break
        
        status = "Aktiv" if enabled else "Deaktiveret"
        health_str = ["OK", "Fejl", "Timeout"][sensor_health]
        type_str = ["PID", "Simple", "Manuel"][thermostat_type]
        
        self.status_label.setText(
            f"Termostat {self.regulator_id + 1}: {status} ({type_str}) | "
            f"Temp: {sensor_temp:.1f}°C | Sæt: {setpoint:.1f}°C | "
            f"Output: {output:.0f}% | Sensor: {health_str}"
        )
        # Color coding
        if not enabled:
            self.status_label.setStyleSheet("background-color: gray; color: white; padding: 5px;")
        elif sensor_health > 0:
            self.status_label.setStyleSheet("background-color: orange; color: white; padding: 5px;")
        elif abs(sensor_temp - setpoint) > 2:
            self.status_label.setStyleSheet("background-color: red; color: white; padding: 5px;")
        else:
            self.status_label.setStyleSheet("background-color: green; color: white; padding: 5px;")
        
        # Update controls
        self.setpoint_spin.setValue(setpoint)
        self.sensor_combo.setCurrentIndex(sensor_idx)
        self.type_combo.setCurrentIndex(thermostat_type)
        
        # Update type-specific controls
        if thermostat_type == 0:  # PID
            self.kp_spin.setValue(thermostat_data.get('kp', 2.0))
            self.ki_spin.setValue(thermostat_data.get('ki', 1.0))
            self.kd_spin.setValue(thermostat_data.get('kd', 0.5))
        elif thermostat_type == 1:  # Simple
            self.hysteresis_spin.setValue(thermostat_data.get('hysteresis', 1.0))
        elif thermostat_type == 2:  # Manual
            self.manual_output_spin.setValue(thermostat_data.get('manualOutput', 0))
        
        self.enable_btn.setText("Deaktiver" if enabled else "Aktiver")
        self.update_controls_visibility()

class AlarmWidget(QWidget):
    def __init__(self, alarm_index, parent=None):
        super().__init__(parent)
        self.alarm_index = alarm_index
        self.parent_app = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Status
        self.status_label = QLabel(f"Alarm {self.alarm_index + 1}: OK")
        self.status_label.setFont(QFont('Arial', 10, QFont.Bold))
        layout.addWidget(self.status_label)
        
        # Controls
        controls = QGridLayout()
        
        controls.addWidget(QLabel("Advarsel lav:"), 0, 0)
        self.warn_low_spin = QDoubleSpinBox()
        self.warn_low_spin.setRange(-50, 150)
        self.warn_low_spin.setSuffix("°C")
        controls.addWidget(self.warn_low_spin, 0, 1)
        
        controls.addWidget(QLabel("Advarsel høj:"), 1, 0)
        self.warn_high_spin = QDoubleSpinBox()
        self.warn_high_spin.setRange(-50, 150)
        self.warn_high_spin.setSuffix("°C")
        controls.addWidget(self.warn_high_spin, 1, 1)
        
        controls.addWidget(QLabel("Alarm lav:"), 2, 0)
        self.alarm_low_spin = QDoubleSpinBox()
        self.alarm_low_spin.setRange(-50, 150)
        self.alarm_low_spin.setSuffix("°C")
        controls.addWidget(self.alarm_low_spin, 2, 1)
        
        controls.addWidget(QLabel("Alarm høj:"), 3, 0)
        self.alarm_high_spin = QDoubleSpinBox()
        self.alarm_high_spin.setRange(-50, 150)
        self.alarm_high_spin.setSuffix("°C")
        controls.addWidget(self.alarm_high_spin, 3, 1)
        
        # Reset mode
        self.auto_reset_cb = QCheckBox("Auto reset")
        controls.addWidget(self.auto_reset_cb, 4, 0)
        
        # Acknowledge button
        self.ack_btn = QPushButton("Kvitter")
        self.ack_btn.clicked.connect(self.acknowledge_alarm)
        controls.addWidget(self.ack_btn, 4, 1)
        
        layout.addLayout(controls)
        self.setLayout(layout)
    
    def acknowledge_alarm(self):
        if self.parent_app:
            self.parent_app.acknowledge_alarm(self.alarm_index)
    
    def update_display(self, alarm_data):
        level = alarm_data.get('level', 0)
        active = alarm_data.get('active', False)
        acknowledged = alarm_data.get('acknowledged', False)
        error_code = alarm_data.get('errorCode', 0)
        
        level_names = ["OK", "Advarsel", "Alarm", "Teknisk"]
        status = level_names[level] if level < len(level_names) else "Ukendt"
        
        if error_code > 0:
            status += f" (Fejl: {error_code})"
        
        self.status_label.setText(f"Alarm {self.alarm_index + 1}: {status}")
        
        # Color coding
        if level == 0:
            self.status_label.setStyleSheet("background-color: green; color: white; padding: 5px;")
        elif level == 1:
            self.status_label.setStyleSheet("background-color: orange; color: white; padding: 5px;")
        else:
            self.status_label.setStyleSheet("background-color: red; color: white; padding: 5px;")
        
        self.ack_btn.setEnabled(active and not acknowledged)

class BrewControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.serial_thread = None
        self.current_data = {}
        self.init_ui()
        self.init_serial()
        
        # Timer for status updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.request_status)
        self.update_timer.start(2000)
    
    def init_ui(self):
        self.setWindowTitle('BrewControl - Arduino Temperaturregulator')
        self.setGeometry(100, 100, 1000, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Connection status and controls
        conn_layout = QHBoxLayout()
        self.conn_label = QLabel("Forbindelse: Ikke tilsluttet")
        self.conn_label.setFont(QFont('Arial', 10, QFont.Bold))
        conn_layout.addWidget(self.conn_label)
        
        # Serial port controls
        conn_layout.addWidget(QLabel("Port:"))
        self.port_combo = QComboBox()
        self.port_combo.addItems(["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8"])
        self.port_combo.setCurrentText("COM3")
        conn_layout.addWidget(self.port_combo)
        
        conn_layout.addWidget(QLabel("Baudrate:"))
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baudrate_combo.setCurrentText("115200")
        conn_layout.addWidget(self.baudrate_combo)
        
        self.connect_btn = QPushButton("Tilslut")
        self.connect_btn.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.connect_btn)
        
        layout.addLayout(conn_layout)
        
        # Tabs
        tabs = QTabWidget()
        
        # Thermostat Controllers tab
        thermostat_tab = QWidget()
        thermostat_layout = QHBoxLayout()
        
        self.thermostat_widgets = []
        for i in range(3):
            group = QGroupBox(f"Termostat {i+1}")
            group_layout = QVBoxLayout()
            
            thermostat_widget = ThermostatWidget(i, self)
            self.thermostat_widgets.append(thermostat_widget)
            group_layout.addWidget(thermostat_widget)
            group.setLayout(group_layout)
            
            thermostat_layout.addWidget(group)
        
        thermostat_tab.setLayout(thermostat_layout)
        tabs.addTab(thermostat_tab, "Termostater")
        
        # Alarms tab
        alarm_tab = QWidget()
        alarm_layout = QHBoxLayout()
        
        self.alarm_widgets = []
        for i in range(3):
            group = QGroupBox(f"Alarm {i+1}")
            group_layout = QVBoxLayout()
            
            alarm_widget = AlarmWidget(i, self)
            self.alarm_widgets.append(alarm_widget)
            group_layout.addWidget(alarm_widget)
            group.setLayout(group_layout)
            
            alarm_layout.addWidget(group)
        
        alarm_tab.setLayout(alarm_layout)
        tabs.addTab(alarm_tab, "Alarmer")
        
        # Sensors tab
        sensor_tab = QWidget()
        sensor_layout = QVBoxLayout()
        
        self.sensor_labels = []
        for i in range(7):
            label = QLabel(f"Sensor {i+1}: --")
            label.setFont(QFont('Arial', 12))
            self.sensor_labels.append(label)
            sensor_layout.addWidget(label)
        
        sensor_tab.setLayout(sensor_layout)
        tabs.addTab(sensor_tab, "Sensorer")
        
        # Manual command tab
        manual_tab = QWidget()
        manual_layout = QVBoxLayout()
        
        # Command input
        manual_layout.addWidget(QLabel("JSON Kommando:"))
        self.manual_command_text = QTextEdit()
        self.manual_command_text.setMaximumHeight(100)
        self.manual_command_text.setPlainText('{"command": "getStatus"}')
        manual_layout.addWidget(self.manual_command_text)
        
        # Send button
        send_btn = QPushButton("Send Kommando")
        send_btn.clicked.connect(self.send_manual_command)
        manual_layout.addWidget(send_btn)
        
        # Response
        manual_layout.addWidget(QLabel("Svar:"))
        self.manual_response_text = QTextEdit()
        self.manual_response_text.setReadOnly(True)
        manual_layout.addWidget(self.manual_response_text)
        
        manual_tab.setLayout(manual_layout)
        tabs.addTab(manual_tab, "Manuel Kommando")
        
        # Communication tab
        comm_tab = QWidget()
        comm_layout = QVBoxLayout()
        
        # Last command sent
        comm_layout.addWidget(QLabel("Seneste kommando:"))
        self.last_command_text = QTextEdit()
        self.last_command_text.setReadOnly(True)
        self.last_command_text.setMaximumHeight(100)
        comm_layout.addWidget(self.last_command_text)
        
        # Last response received
        comm_layout.addWidget(QLabel("Seneste svar:"))
        self.last_response_text = QTextEdit()
        self.last_response_text.setReadOnly(True)
        self.last_response_text.setMaximumHeight(100)
        comm_layout.addWidget(self.last_response_text)
        
        comm_tab.setLayout(comm_layout)
        tabs.addTab(comm_tab, "Kommunikation")
        
        # Log tab
        log_tab = QWidget()
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_tab.setLayout(log_layout)
        tabs.addTab(log_tab, "Log")
        
        layout.addWidget(tabs)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Anvend Konfiguration")
        apply_btn.clicked.connect(self.apply_config)
        button_layout.addWidget(apply_btn)
        
        emergency_btn = QPushButton("NØDSTOP")
        emergency_btn.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        emergency_btn.clicked.connect(self.emergency_stop)
        button_layout.addWidget(emergency_btn)
        
        layout.addLayout(button_layout)
        central_widget.setLayout(layout)
    
    def init_serial(self):
        # Don't auto-start serial connection
        pass
    
    def toggle_connection(self):
        if self.serial_thread and self.serial_thread.isRunning():
            # Disconnect
            self.serial_thread.stop()
            self.serial_thread.wait()
            self.serial_thread = None
            self.connect_btn.setText("Tilslut")
            self.conn_label.setText("Forbindelse: Ikke tilsluttet")
            self.conn_label.setStyleSheet("background-color: red; color: white; padding: 5px;")
        else:
            # Connect
            port = self.port_combo.currentText()
            baudrate = int(self.baudrate_combo.currentText())
            self.serial_thread = SerialThread(port, baudrate)
            self.serial_thread.data_received.connect(self.handle_serial_data)
            self.serial_thread.start()
            self.connect_btn.setText("Afbryd")
            
            # Start status updates when connected
            QTimer.singleShot(1000, self.request_status)
    
    def handle_serial_data(self, data):
        self.current_data = data
        self.conn_label.setText("Forbindelse: Tilsluttet")
        self.conn_label.setStyleSheet("background-color: green; color: white; padding: 5px;")
        
        # Update communication tab with response
        self.last_response_text.setPlainText(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Update manual command response
        timestamp = time.strftime("%H:%M:%S")
        self.manual_response_text.append(f"[{timestamp}] MODTAGET: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # Update displays
        if 'thermostats' in data and 'sensors' in data:
            for i, thermostat_widget in enumerate(self.thermostat_widgets):
                if i < len(data['thermostats']):
                    thermostat_widget.update_display(data['thermostats'][i], data['sensors'])
        
        if 'alarms' in data:
            for i, alarm_widget in enumerate(self.alarm_widgets):
                # Find alarm for this thermostat
                for alarm in data['alarms']:
                    if alarm.get('regulator_id') == i:
                        alarm_widget.update_display(alarm)
                        break
        
        if 'sensors' in data:
            for i, sensor_label in enumerate(self.sensor_labels):
                # Find sensor by sensor_id
                for sensor in data['sensors']:
                    if sensor.get('sensor_id') == i:
                        temp = sensor.get('temperature', 0)
                        health = sensor.get('health', 0)
                        simulated = sensor.get('simulated', False)
                        sensor_type = sensor.get('type', 'Unknown')
                        
                        health_str = ["OK", "Fejl", "Timeout"][health]
                        sim_str = " (Simuleret)" if simulated else ""
                        
                        sensor_label.setText(f"Sensor {i+1} ({sensor_type}): {temp:.1f}°C - {health_str}{sim_str}")
                        
                        if health == 0:
                            sensor_label.setStyleSheet("background-color: lightgreen; padding: 5px;")
                        elif health == 1:
                            sensor_label.setStyleSheet("background-color: orange; padding: 5px;")
                        else:
                            sensor_label.setStyleSheet("background-color: red; color: white; padding: 5px;")
                        break
        
        # Log data
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] Status modtaget")
    
    def send_command_with_log(self, command):
        if self.serial_thread and self.serial_thread.isRunning():
            # Update communication tab with command
            self.last_command_text.setPlainText(json.dumps(command, indent=2, ensure_ascii=False))
            self.serial_thread.send_command(command)
    
    def send_manual_command(self):
        try:
            # Parse JSON from text field
            command_text = self.manual_command_text.toPlainText().strip()
            command = json.loads(command_text)
            
            # Send command
            if self.serial_thread and self.serial_thread.isRunning():
                self.serial_thread.send_command(command)
                
                # Show sent command in response area
                timestamp = time.strftime("%H:%M:%S")
                self.manual_response_text.append(f"[{timestamp}] SENDT: {json.dumps(command, indent=2, ensure_ascii=False)}")
                
                # Log in main log
                self.log_text.append(f"[{timestamp}] Manuel kommando sendt")
            else:
                QMessageBox.warning(self, "Fejl", "Ikke forbundet til enhed")
                
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "JSON Fejl", f"Ugyldig JSON: {str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "Fejl", f"Kunne ikke sende kommando: {str(e)}")
        if self.serial_thread and self.serial_thread.isRunning():
            # Update communication tab with command
            self.last_command_text.setPlainText(json.dumps(command, indent=2, ensure_ascii=False))
            self.serial_thread.send_command(command)
    
    def request_status(self):
        command = {"command": "getStatus"}
        self.send_command_with_log(command)
    
    def toggle_thermostat(self, regulator_id, enabled):
        command = {
            "command": "toggleEnable",
            "regulator_id": regulator_id,
            "enabled": enabled
        }
        self.send_command_with_log(command)
        
        timestamp = time.strftime("%H:%M:%S")
        status = "aktiveret" if enabled else "deaktiveret"
        self.log_text.append(f"[{timestamp}] Termostat {regulator_id + 1} {status}")
    
    def acknowledge_alarm(self, alarm_index):
        command = {
            "command": "ackAlarm",
            "regulator_id": alarm_index
        }
        self.send_command_with_log(command)
        
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] Alarm {alarm_index + 1} kvitteret")
    
    def apply_config(self):
        if not self.serial_thread:
            return
        
        # Collect thermostat configuration
        for i, widget in enumerate(self.thermostat_widgets):
            thermostat_config = {
                "command": "setConfig",
                "regulator_id": i,
                "type": widget.type_combo.currentIndex(),
                "sensorIndex": widget.sensor_combo.currentIndex(),
                "enabled": widget.enable_btn.text() == "Deaktiver"
            }
            
            # Add type-specific parameters
            thermostat_type = widget.type_combo.currentIndex()
            if thermostat_type == 0:  # PID
                thermostat_config.update({
                    "setpoint": widget.setpoint_spin.value(),
                    "kp": widget.kp_spin.value(),
                    "ki": widget.ki_spin.value(),
                    "kd": widget.kd_spin.value()
                })
            elif thermostat_type == 1:  # Simple
                thermostat_config.update({
                    "setpoint": widget.setpoint_spin.value(),
                    "hysteresis": widget.hysteresis_spin.value()
                })
            elif thermostat_type == 2:  # Manual
                thermostat_config.update({
                    "manualOutput": widget.manual_output_spin.value()
                })
            
            self.send_command_with_log(thermostat_config)
        
        
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] Konfiguration sendt til Arduino")
        
        QMessageBox.information(self, "Konfiguration", "Konfiguration sendt til Arduino")
    
    def emergency_stop(self):
        # Disable all thermostats
        for i in range(3):
            command = {
                "command": "toggleEnable",
                "regulator_id": i,
                "enabled": False
            }
            self.send_command_with_log(command)
        
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] NØDSTOP aktiveret - alle termostater deaktiveret")
        
        QMessageBox.warning(self, "NØDSTOP", "Alle termostater er blevet deaktiveret!")
    
    def closeEvent(self, event):
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread.wait()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BrewControlApp()
    window.show()
    sys.exit(app.exec_())