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

class PIDWidget(QWidget):
    def __init__(self, pid_index, parent=None):
        super().__init__(parent)
        self.pid_index = pid_index
        self.parent_app = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Status display
        self.status_label = QLabel(f"PID {self.pid_index + 1}: Deaktiveret")
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
        self.sensor_combo.addItems([f"Sensor {i+1}" for i in range(5)])
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
        
        # Enable/Disable button
        self.enable_btn = QPushButton("Aktiver")
        self.enable_btn.clicked.connect(self.toggle_enable)
        controls.addWidget(self.enable_btn, 6, 0, 1, 2)
        
        layout.addLayout(controls)
        self.setLayout(layout)
    
    def toggle_enable(self):
        if self.parent_app:
            enabled = self.enable_btn.text() == "Aktiver"
            self.parent_app.toggle_pid(self.pid_index, enabled)
    
    def update_display(self, pid_data, sensor_data):
        enabled = pid_data.get('enabled', False)
        setpoint = pid_data.get('setpoint', 0)
        output = pid_data.get('output', 0)
        sensor_idx = pid_data.get('sensorIndex', 0)
        
        if sensor_idx < len(sensor_data):
            temp = sensor_data[sensor_idx].get('value', 0)
            health = sensor_data[sensor_idx].get('health', 0)
            
            status = "Aktiv" if enabled else "Deaktiveret"
            health_str = ["OK", "Nedsat", "Fejl"][health]
            
            self.status_label.setText(
                f"PID {self.pid_index + 1}: {status} | "
                f"Temp: {temp:.1f}°C | Sæt: {setpoint:.1f}°C | "
                f"Output: {output}% | Sensor: {health_str}"
            )
            
            # Color coding
            if not enabled:
                self.status_label.setStyleSheet("background-color: gray; color: white; padding: 5px;")
            elif health > 0:
                self.status_label.setStyleSheet("background-color: orange; color: white; padding: 5px;")
            elif abs(temp - setpoint) > 2:
                self.status_label.setStyleSheet("background-color: red; color: white; padding: 5px;")
            else:
                self.status_label.setStyleSheet("background-color: green; color: white; padding: 5px;")
        
        # Update controls
        self.setpoint_spin.setValue(setpoint)
        self.sensor_combo.setCurrentIndex(sensor_idx)
        self.enable_btn.setText("Deaktiver" if enabled else "Aktiver")

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
        
        # Connection status
        self.conn_label = QLabel("Forbindelse: Ikke tilsluttet")
        self.conn_label.setFont(QFont('Arial', 10, QFont.Bold))
        layout.addWidget(self.conn_label)
        
        # Tabs
        tabs = QTabWidget()
        
        # PID Controllers tab
        pid_tab = QWidget()
        pid_layout = QHBoxLayout()
        
        self.pid_widgets = []
        for i in range(3):
            group = QGroupBox(f"Regulator {i+1}")
            group_layout = QVBoxLayout()
            
            pid_widget = PIDWidget(i, self)
            self.pid_widgets.append(pid_widget)
            group_layout.addWidget(pid_widget)
            group.setLayout(group_layout)
            
            pid_layout.addWidget(group)
        
        pid_tab.setLayout(pid_layout)
        tabs.addTab(pid_tab, "Regulatorer")
        
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
        for i in range(5):
            label = QLabel(f"Sensor {i+1}: --")
            label.setFont(QFont('Arial', 12))
            self.sensor_labels.append(label)
            sensor_layout.addWidget(label)
        
        sensor_tab.setLayout(sensor_layout)
        tabs.addTab(sensor_tab, "Sensorer")
        
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
        self.serial_thread = SerialThread()
        self.serial_thread.data_received.connect(self.handle_serial_data)
        self.serial_thread.start()
        
        # Initial status request
        QTimer.singleShot(1000, self.request_status)
    
    def handle_serial_data(self, data):
        self.current_data = data
        self.conn_label.setText("Forbindelse: Tilsluttet")
        self.conn_label.setStyleSheet("background-color: green; color: white; padding: 5px;")
        
        # Update displays
        if 'pids' in data and 'sensors' in data:
            for i, pid_widget in enumerate(self.pid_widgets):
                if i < len(data['pids']):
                    pid_widget.update_display(data['pids'][i], data['sensors'])
        
        if 'alarms' in data:
            for i, alarm_widget in enumerate(self.alarm_widgets):
                if i < len(data['alarms']):
                    alarm_widget.update_display(data['alarms'][i])
        
        if 'sensors' in data:
            for i, sensor_label in enumerate(self.sensor_labels):
                if i < len(data['sensors']):
                    sensor = data['sensors'][i]
                    value = sensor.get('value', 0)
                    health = sensor.get('health', 0)
                    simulated = sensor.get('simulated', False)
                    
                    health_str = ["OK", "Nedsat", "Fejl"][health]
                    sim_str = " (Simuleret)" if simulated else ""
                    
                    sensor_label.setText(f"Sensor {i+1}: {value:.1f}°C - {health_str}{sim_str}")
                    
                    if health == 0:
                        sensor_label.setStyleSheet("background-color: lightgreen; padding: 5px;")
                    elif health == 1:
                        sensor_label.setStyleSheet("background-color: orange; padding: 5px;")
                    else:
                        sensor_label.setStyleSheet("background-color: red; color: white; padding: 5px;")
        
        # Log data
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] Status modtaget")
    
    def request_status(self):
        if self.serial_thread:
            command = {"command": "getStatus"}
            self.serial_thread.send_command(command)
    
    def toggle_pid(self, pid_index, enabled):
        if self.serial_thread:
            command = {
                "command": "toggleEnable",
                "pidIndex": pid_index,
                "enabled": enabled
            }
            self.serial_thread.send_command(command)
            
            timestamp = time.strftime("%H:%M:%S")
            status = "aktiveret" if enabled else "deaktiveret"
            self.log_text.append(f"[{timestamp}] PID {pid_index + 1} {status}")
    
    def acknowledge_alarm(self, alarm_index):
        if self.serial_thread:
            command = {
                "command": "ackAlarm",
                "pidIndex": alarm_index
            }
            self.serial_thread.send_command(command)
            
            timestamp = time.strftime("%H:%M:%S")
            self.log_text.append(f"[{timestamp}] Alarm {alarm_index + 1} kvitteret")
    
    def apply_config(self):
        if not self.serial_thread:
            return
        
        # Collect PID configuration
        pids = []
        for i, widget in enumerate(self.pid_widgets):
            pid_config = {
                "type": widget.type_combo.currentIndex(),
                "setpoint": widget.setpoint_spin.value(),
                "kp": widget.kp_spin.value(),
                "ki": widget.ki_spin.value(),
                "kd": widget.kd_spin.value(),
                "sensorIndex": widget.sensor_combo.currentIndex(),
                "enabled": widget.enable_btn.text() == "Deaktiver"
            }
            pids.append(pid_config)
        
        # Collect alarm configuration
        alarms = []
        for i, widget in enumerate(self.alarm_widgets):
            alarm_config = {
                "warningLow": widget.warn_low_spin.value(),
                "warningHigh": widget.warn_high_spin.value(),
                "alarmLow": widget.alarm_low_spin.value(),
                "alarmHigh": widget.alarm_high_spin.value(),
                "resetMode": 0 if widget.auto_reset_cb.isChecked() else 1,
                "enabled": True
            }
            alarms.append(alarm_config)
        
        command = {
            "command": "setConfig",
            "pids": pids,
            "alarms": alarms
        }
        
        self.serial_thread.send_command(command)
        
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] Konfiguration sendt til Arduino")
        
        QMessageBox.information(self, "Konfiguration", "Konfiguration sendt til Arduino")
    
    def emergency_stop(self):
        if self.serial_thread:
            # Disable all PIDs
            for i in range(3):
                command = {
                    "command": "toggleEnable",
                    "pidIndex": i,
                    "enabled": False
                }
                self.serial_thread.send_command(command)
            
            timestamp = time.strftime("%H:%M:%S")
            self.log_text.append(f"[{timestamp}] NØDSTOP aktiveret - alle regulatorer deaktiveret")
            
            QMessageBox.warning(self, "NØDSTOP", "Alle regulatorer er blevet deaktiveret!")
    
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